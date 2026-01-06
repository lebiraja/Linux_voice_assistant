"""
AI-powered script generation and execution tool using aichat
"""

import subprocess
import logging
import os
import tempfile
import shlex
from typing import Dict, Any, List
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class GenerateAndRunScriptTool(Tool):
    """Generate and execute scripts using AI (aichat)"""
    
    @property
    def name(self) -> str:
        return "generate_and_run_script"
    
    @property
    def description(self) -> str:
        return (
            "Generate and execute scripts based on natural language requirements using AI. "
            "This tool can create bash scripts, Python scripts, or any other executable code "
            "to accomplish complex tasks. Specify the task requirements and optionally the "
            "programming language (defaults to bash). The script will be generated, reviewed, "
            "and executed automatically."
        )
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="task_description",
                type="string",
                description="Detailed description of what the script should do",
                required=True
            ),
            ToolParameter(
                name="language",
                type="string",
                description="Programming language for the script (bash, python, etc.)",
                required=False,
                default="bash"
            ),
            ToolParameter(
                name="auto_execute",
                type="boolean",
                description="Whether to automatically execute the script after generation",
                required=False,
                default=True
            ),
            ToolParameter(
                name="working_directory",
                type="string",
                description="Directory where the script should run",
                required=False,
                default=None
            )
        ]
    
    def _check_aichat_installed(self) -> bool:
        """Check if aichat is installed"""
        try:
            result = subprocess.run(
                ["which", "aichat"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking aichat installation: {e}")
            return False
    
    def _generate_script(self, task_description: str, language: str) -> Dict[str, Any]:
        """Generate script using aichat"""
        try:
            # Craft the prompt for aichat
            prompt = f"""Generate a {language} script that does the following:

{task_description}

Requirements:
- Write clean, well-commented code
- Include error handling where appropriate
- Make the script executable and production-ready
- Output ONLY the script code without any explanation or markdown formatting
- Do not include code block markers (```)

Generate the complete script:"""

            # Call aichat to generate the script
            logger.info(f"Generating {language} script with aichat for task: {task_description}")
            
            result = subprocess.run(
                ["aichat", "--no-stream", prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"aichat failed: {result.stderr}"
                }
            
            script_content = result.stdout.strip()
            
            # Clean up any markdown code blocks if present
            if script_content.startswith("```"):
                lines = script_content.split("\n")
                # Remove first and last lines if they are code block markers
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                script_content = "\n".join(lines)
            
            return {
                "success": True,
                "script": script_content
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Script generation timed out after 60 seconds"
            }
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_script(self, script_content: str, language: str, working_dir: str = None) -> Dict[str, Any]:
        """Execute the generated script"""
        try:
            # Create a temporary file for the script
            suffix = self._get_file_suffix(language)
            
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=suffix,
                delete=False
            ) as script_file:
                script_file.write(script_content)
                script_path = script_file.name
            
            try:
                # Make script executable for bash/sh scripts
                if language.lower() in ['bash', 'sh', 'shell']:
                    os.chmod(script_path, 0o755)
                    cmd = [script_path]
                elif language.lower() == 'python':
                    cmd = ['python3', script_path]
                else:
                    # Try to execute directly
                    os.chmod(script_path, 0o755)
                    cmd = [script_path]
                
                logger.info(f"Executing {language} script: {script_path}")
                
                # Execute the script
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    cwd=working_dir
                )
                
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "script_path": script_path
                }
                
            finally:
                # Clean up the temporary script file
                try:
                    os.unlink(script_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Script execution timed out after 5 minutes"
            }
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_file_suffix(self, language: str) -> str:
        """Get appropriate file suffix for the language"""
        suffixes = {
            'bash': '.sh',
            'sh': '.sh',
            'shell': '.sh',
            'python': '.py',
            'python3': '.py',
            'javascript': '.js',
            'node': '.js',
            'perl': '.pl',
            'ruby': '.rb',
            'php': '.php'
        }
        return suffixes.get(language.lower(), '.sh')
    
    def execute(
        self,
        task_description: str,
        language: str = "bash",
        auto_execute: bool = True,
        working_directory: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate and optionally execute a script based on task description.
        
        Args:
            task_description: What the script should accomplish
            language: Programming language (bash, python, etc.)
            auto_execute: Whether to automatically run the generated script
            working_directory: Directory to run the script in
        """
        try:
            # Check if aichat is installed
            if not self._check_aichat_installed():
                return {
                    "success": False,
                    "error": "aichat is not installed. Please install it first using: curl -fsSL https://raw.githubusercontent.com/sigoden/aichat/main/scripts/install.sh | bash"
                }
            
            # Generate the script
            gen_result = self._generate_script(task_description, language)
            
            if not gen_result["success"]:
                return gen_result
            
            script_content = gen_result["script"]
            
            result = {
                "success": True,
                "script_generated": script_content,
                "language": language
            }
            
            # Execute if requested
            if auto_execute:
                exec_result = self._execute_script(
                    script_content,
                    language,
                    working_directory
                )
                result.update({
                    "executed": True,
                    "execution_success": exec_result.get("success", False),
                    "output": exec_result.get("stdout", ""),
                    "errors": exec_result.get("stderr", ""),
                    "return_code": exec_result.get("return_code")
                })
            else:
                result["executed"] = False
                result["message"] = "Script generated but not executed (auto_execute=False)"
            
            return result
            
        except Exception as e:
            logger.error(f"Error in generate_and_run_script: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ExecuteCommandTool(Tool):
    """Execute a shell command directly"""
    
    @property
    def name(self) -> str:
        return "execute_command"
    
    @property
    def description(self) -> str:
        return (
            "Execute a shell command directly in the terminal. Use this for simple "
            "commands that don't require script generation. For complex multi-step "
            "tasks, use generate_and_run_script instead."
        )
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="command",
                type="string",
                description="The shell command to execute",
                required=True
            ),
            ToolParameter(
                name="working_directory",
                type="string",
                description="Directory where the command should run",
                required=False,
                default=None
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="Command timeout in seconds",
                required=False,
                default=30
            )
        ]
    
    def execute(
        self,
        command: str,
        working_directory: str = None,
        timeout: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a shell command"""
        try:
            logger.info(f"Executing command: {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_directory
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "command": command
            }
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
