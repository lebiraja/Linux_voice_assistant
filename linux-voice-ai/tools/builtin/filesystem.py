"""
Filesystem tools for file operations
"""

import os
import glob
import logging
from pathlib import Path
from typing import Dict, Any, List
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class ListFilesTool(Tool):
    """List files in a directory"""
    
    @property
    def name(self) -> str:
        return "list_files"
    
    @property
    def description(self) -> str:
        return "List files and directories in a specified path. Can filter by pattern (e.g., *.py for Python files)."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Directory path to list files from",
                required=False,
                default="."
            ),
            ToolParameter(
                name="pattern",
                type="string",
                description="File pattern to match (e.g., *.py, *.txt). Use * for all files.",
                required=False,
                default="*"
            ),
            ToolParameter(
                name="recursive",
                type="boolean",
                description="Whether to search recursively in subdirectories",
                required=False,
                default=False
            )
        ]
    
    def execute(self, path: str = ".", pattern: str = "*", recursive: bool = False, **kwargs) -> Dict[str, Any]:
        """List files in directory"""
        try:
            path_obj = Path(path).expanduser().resolve()
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "error": f"Path does not exist: {path}"
                }
            
            if not path_obj.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {path}"
                }
            
            # List files
            if recursive:
                files = list(path_obj.rglob(pattern))
            else:
                files = list(path_obj.glob(pattern))
            
            # Format results
            file_list = []
            for f in files:
                file_info = {
                    "name": f.name,
                    "path": str(f),
                    "type": "directory" if f.is_dir() else "file",
                    "size": f.stat().st_size if f.is_file() else None
                }
                file_list.append(file_info)
            
            return {
                "success": True,
                "path": str(path_obj),
                "pattern": pattern,
                "count": len(file_list),
                "files": file_list[:50]  # Limit to 50 files
            }
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ReadFileTool(Tool):
    """Read contents of a text file"""
    
    @property
    def name(self) -> str:
        return "read_file"
    
    @property
    def description(self) -> str:
        return "Read the contents of a text file. Returns the file content as a string."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type="string",
                description="Path to the file to read",
                required=True
            ),
            ToolParameter(
                name="max_lines",
                type="integer",
                description="Maximum number of lines to read (default: 100)",
                required=False,
                default=100
            )
        ]
    
    def execute(self, file_path: str, max_lines: int = 100, **kwargs) -> Dict[str, Any]:
        """Read file contents"""
        try:
            path_obj = Path(file_path).expanduser().resolve()
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}"
                }
            
            if not path_obj.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}"
                }
            
            # Read file
            with open(path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.rstrip())
            
            content = "\n".join(lines)
            
            return {
                "success": True,
                "file_path": str(path_obj),
                "lines_read": len(lines),
                "content": content,
                "truncated": len(lines) >= max_lines
            }
            
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class SearchFilesTool(Tool):
    """Search for files by name"""
    
    @property
    def name(self) -> str:
        return "search_files"
    
    @property
    def description(self) -> str:
        return "Search for files by name pattern in a directory tree."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="search_path",
                type="string",
                description="Directory to search in",
                required=False,
                default="."
            ),
            ToolParameter(
                name="filename_pattern",
                type="string",
                description="Filename pattern to search for (e.g., *.py, config.yaml)",
                required=True
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description="Maximum number of results to return",
                required=False,
                default=20
            )
        ]
    
    def execute(self, search_path: str = ".", filename_pattern: str = "*", max_results: int = 20, **kwargs) -> Dict[str, Any]:
        """Search for files"""
        try:
            path_obj = Path(search_path).expanduser().resolve()
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "error": f"Search path does not exist: {search_path}"
                }
            
            # Search recursively
            matches = []
            for file_path in path_obj.rglob(filename_pattern):
                if len(matches) >= max_results:
                    break
                matches.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "type": "directory" if file_path.is_dir() else "file"
                })
            
            return {
                "success": True,
                "search_path": str(path_obj),
                "pattern": filename_pattern,
                "count": len(matches),
                "matches": matches
            }
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return {
                "success": False,
                "error": str(e)
            }
