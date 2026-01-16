"""
Sandboxed script execution environment.
Provides safe execution of user-generated scripts with resource limits.
"""

import os
import subprocess
import tempfile
import shutil
import logging
import signal
import resource
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SandboxType(Enum):
    """Available sandbox implementations"""
    NONE = "none"           # No sandboxing (dangerous)
    SUBPROCESS = "subprocess"  # Basic subprocess with limits
    FIREJAIL = "firejail"   # Firejail sandboxing
    BUBBLEWRAP = "bubblewrap"  # Bubblewrap sandboxing


@dataclass
class ExecutionResult:
    """Result of script execution"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    sandbox_used: str
    error: Optional[str] = None


class SandboxExecutor:
    """
    Safe script execution with sandboxing and resource limits.

    Features:
    - Multiple sandbox backends (firejail, bubblewrap, basic)
    - Resource limits (CPU, memory, time)
    - Blocked dangerous commands
    - Audit logging
    """

    # Dangerous patterns that should never be executed
    BLOCKED_PATTERNS = [
        'rm -rf /',
        'rm -rf ~',
        'rm -rf /*',
        ':(){:|:&};:',  # Fork bomb
        '> /dev/sd',
        'mkfs.',
        'dd if=',
        '> /dev/null 2>&1 &',  # Background without control
        'chmod -R 777 /',
        'chown -R',
        '| sh',
        '| bash',
        'curl | bash',
        'wget | bash',
        'eval',
        'sudo rm',
        'sudo dd',
        'sudo mkfs',
    ]

    # Safe directories for script output
    SAFE_DIRS = [
        '/tmp',
        '/var/tmp',
    ]

    def __init__(self, config: dict = None):
        config = config or {}

        self.timeout = config.get('timeout', 30)  # Default 30 seconds
        self.max_memory_mb = config.get('max_memory_mb', 512)
        self.max_output_bytes = config.get('max_output_bytes', 1024 * 100)  # 100KB

        # Determine best available sandbox
        self.sandbox_type = self._detect_sandbox()

        # Working directory for scripts
        self.work_dir = Path(config.get('work_dir', '/tmp/jarvis_sandbox'))
        self.work_dir.mkdir(parents=True, exist_ok=True)

        # Audit log
        self.audit_log: List[Dict] = []

        logger.info(f"SandboxExecutor initialized: {self.sandbox_type.value}")

    def _detect_sandbox(self) -> SandboxType:
        """Detect the best available sandbox"""
        # Check for firejail
        if shutil.which('firejail'):
            return SandboxType.FIREJAIL

        # Check for bubblewrap
        if shutil.which('bwrap'):
            return SandboxType.BUBBLEWRAP

        # Fall back to basic subprocess
        logger.warning("No sandbox tool found. Using basic subprocess limits.")
        return SandboxType.SUBPROCESS

    def is_safe(self, script: str) -> tuple[bool, Optional[str]]:
        """
        Check if a script is safe to execute.

        Returns:
            Tuple of (is_safe, reason_if_not_safe)
        """
        script_lower = script.lower()

        for pattern in self.BLOCKED_PATTERNS:
            if pattern.lower() in script_lower:
                return False, f"Blocked pattern detected: {pattern}"

        # Check for suspicious redirections
        if '>' in script and any(
            danger in script for danger in ['/dev/', '/etc/', '/bin/', '/sbin/', '/usr/']
        ):
            return False, "Dangerous file redirection detected"

        # Check for network exfiltration attempts
        if any(cmd in script_lower for cmd in ['curl', 'wget', 'nc', 'netcat']):
            if any(danger in script_lower for danger in ['@', '|', 'bash', 'sh', 'eval']):
                return False, "Potential command injection via network"

        return True, None

    def execute(
        self,
        script: str,
        language: str = 'bash',
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute a script in a sandboxed environment.

        Args:
            script: The script content to execute
            language: Script language (bash, python, etc.)
            working_dir: Working directory for execution
            env: Additional environment variables

        Returns:
            ExecutionResult with output and status
        """
        import time
        start_time = time.time()

        # Safety check
        is_safe, reason = self.is_safe(script)
        if not is_safe:
            logger.warning(f"Blocked unsafe script: {reason}")
            self._audit("blocked", script, reason)
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Script blocked for safety: {reason}",
                duration_ms=0,
                sandbox_used="none",
                error=reason
            )

        # Create temporary script file
        script_file = self._create_script_file(script, language)

        try:
            # Execute based on sandbox type
            if self.sandbox_type == SandboxType.FIREJAIL:
                result = self._execute_firejail(script_file, language, working_dir, env)
            elif self.sandbox_type == SandboxType.BUBBLEWRAP:
                result = self._execute_bubblewrap(script_file, language, working_dir, env)
            else:
                result = self._execute_subprocess(script_file, language, working_dir, env)

            duration_ms = int((time.time() - start_time) * 1000)
            result.duration_ms = duration_ms

            # Audit log
            self._audit("executed", script, f"exit_code={result.exit_code}")

            return result

        finally:
            # Cleanup script file
            try:
                script_file.unlink()
            except Exception:
                pass

    def _create_script_file(self, script: str, language: str) -> Path:
        """Create a temporary script file"""
        extensions = {
            'bash': '.sh',
            'python': '.py',
            'python3': '.py',
            'javascript': '.js',
            'node': '.js',
            'perl': '.pl',
            'ruby': '.rb',
        }

        ext = extensions.get(language, '.sh')
        fd, path = tempfile.mkstemp(suffix=ext, dir=self.work_dir)

        with os.fdopen(fd, 'w') as f:
            # Add shebang if needed
            if language == 'bash' and not script.startswith('#!'):
                f.write('#!/bin/bash\n')
            elif language in ('python', 'python3') and not script.startswith('#!'):
                f.write('#!/usr/bin/env python3\n')
            f.write(script)

        os.chmod(path, 0o755)
        return Path(path)

    def _execute_firejail(
        self,
        script_file: Path,
        language: str,
        working_dir: Optional[str],
        env: Optional[Dict[str, str]]
    ) -> ExecutionResult:
        """Execute with firejail sandbox"""
        interpreter = self._get_interpreter(language)

        cmd = [
            'firejail',
            '--quiet',
            '--private',  # Private /home
            '--private-tmp',  # Private /tmp
            '--private-dev',  # Minimal /dev
            '--net=none',  # No network (can enable if needed)
            '--nogroups',
            '--nosound',
            '--no3d',
            '--nodvd',
            f'--rlimit-as={self.max_memory_mb * 1024 * 1024}',
            '--timeout', str(self.timeout),
            interpreter, str(script_file)
        ]

        return self._run_command(cmd, working_dir, env, SandboxType.FIREJAIL)

    def _execute_bubblewrap(
        self,
        script_file: Path,
        language: str,
        working_dir: Optional[str],
        env: Optional[Dict[str, str]]
    ) -> ExecutionResult:
        """Execute with bubblewrap sandbox"""
        interpreter = self._get_interpreter(language)

        cmd = [
            'bwrap',
            '--unshare-all',
            '--die-with-parent',
            '--ro-bind', '/usr', '/usr',
            '--ro-bind', '/lib', '/lib',
            '--ro-bind', '/lib64', '/lib64' if Path('/lib64').exists() else '/lib',
            '--ro-bind', '/bin', '/bin',
            '--symlink', 'usr/lib', '/lib',
            '--proc', '/proc',
            '--dev', '/dev',
            '--tmpfs', '/tmp',
            '--bind', str(self.work_dir), '/sandbox',
            '--chdir', '/sandbox',
            interpreter, str(script_file)
        ]

        return self._run_command(cmd, working_dir, env, SandboxType.BUBBLEWRAP)

    def _execute_subprocess(
        self,
        script_file: Path,
        language: str,
        working_dir: Optional[str],
        env: Optional[Dict[str, str]]
    ) -> ExecutionResult:
        """Execute with basic subprocess (limited sandboxing)"""
        interpreter = self._get_interpreter(language)
        cmd = [interpreter, str(script_file)]

        return self._run_command(cmd, working_dir, env, SandboxType.SUBPROCESS)

    def _get_interpreter(self, language: str) -> str:
        """Get interpreter path for language"""
        interpreters = {
            'bash': '/bin/bash',
            'sh': '/bin/sh',
            'python': 'python3',
            'python3': 'python3',
            'javascript': 'node',
            'node': 'node',
            'perl': 'perl',
            'ruby': 'ruby',
        }
        return interpreters.get(language, '/bin/bash')

    def _run_command(
        self,
        cmd: List[str],
        working_dir: Optional[str],
        env: Optional[Dict[str, str]],
        sandbox_type: SandboxType
    ) -> ExecutionResult:
        """Run a command with resource limits"""
        # Prepare environment
        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        # Prepare working directory
        cwd = working_dir or str(self.work_dir)

        def set_limits():
            """Set resource limits for child process"""
            # Memory limit
            mem_bytes = self.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))

            # CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout + 5))

            # Prevent core dumps
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout,
                cwd=cwd,
                env=run_env,
                preexec_fn=set_limits if sandbox_type == SandboxType.SUBPROCESS else None
            )

            stdout = process.stdout.decode('utf-8', errors='replace')[:self.max_output_bytes]
            stderr = process.stderr.decode('utf-8', errors='replace')[:self.max_output_bytes]

            return ExecutionResult(
                success=process.returncode == 0,
                exit_code=process.returncode,
                stdout=stdout,
                stderr=stderr,
                duration_ms=0,  # Will be set by caller
                sandbox_used=sandbox_type.value
            )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Script timed out after {self.timeout} seconds",
                duration_ms=self.timeout * 1000,
                sandbox_used=sandbox_type.value,
                error="timeout"
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_ms=0,
                sandbox_used=sandbox_type.value,
                error=str(e)
            )

    def _audit(self, action: str, script: str, details: str):
        """Add entry to audit log"""
        import time
        entry = {
            "timestamp": time.time(),
            "action": action,
            "script_preview": script[:100],
            "details": details
        }
        self.audit_log.append(entry)

        # Keep only last 100 entries
        if len(self.audit_log) > 100:
            self.audit_log = self.audit_log[-100:]

    def get_audit_log(self) -> List[Dict]:
        """Get the audit log"""
        return self.audit_log.copy()

    def cleanup(self):
        """Clean up temporary files"""
        try:
            for file in self.work_dir.glob("*"):
                if file.is_file():
                    file.unlink()
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")


# Convenience function
def create_sandbox(config: dict = None) -> SandboxExecutor:
    """Create a sandbox executor"""
    return SandboxExecutor(config)
