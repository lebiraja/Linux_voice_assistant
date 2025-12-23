"""Application control actions."""

import subprocess
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class AppController:
    """Control applications (open, close)."""
    
    def __init__(self, parser=None):
        """
        Initialize app controller.
        
        Args:
            parser: CommandParser instance for app executable lookup
        """
        self.parser = parser
    
    def open_app(self, app_name):
        """
        Open/launch an application.
        
        Args:
            app_name: Name of the application
            
        Returns:
            dict: Result with 'success', 'message', and 'app'
        """
        logger.info(f"Attempting to open: {app_name}")
        
        # Handle None app_name
        if app_name is None:
            logger.warning("No app name provided")
            template = self.parser.get_response_template('error', 'unknown_command') if self.parser else "I didn't understand which app to open."
            return {
                'success': False,
                'message': template,
                'app': None
            }
        
        # Get possible executables
        executables = self.parser.get_app_executables(app_name) if self.parser else [app_name]
        
        # Try each executable
        for executable in executables:
            if self._is_executable_available(executable):
                try:
                    # Launch the application
                    subprocess.Popen(
                        [executable],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                    
                    logger.info(f"Successfully opened: {executable}")
                    
                    template = self.parser.get_response_template('success', 'open_app') if self.parser else "{app} is now open."
                    message = template.format(app=app_name.title())
                    
                    return {
                        'success': True,
                        'message': message,
                        'app': app_name
                    }
                    
                except Exception as e:
                    logger.error(f"Error opening {executable}: {e}")
                    continue
        
        # If we get here, none of the executables worked
        logger.warning(f"Could not open {app_name}")
        
        template = self.parser.get_response_template('error', 'app_not_found') if self.parser else "I couldn't find {app}."
        message = template.format(app=app_name.title())
        
        return {
            'success': False,
            'message': message,
            'app': app_name
        }
    
    def close_app(self, app_name):
        """
        Close an application.
        
        Args:
            app_name: Name of the application
            
        Returns:
            dict: Result with 'success', 'message', and 'app'
        """
        logger.info(f"Attempting to close: {app_name}")
        
        # Get possible executables
        executables = self.parser.get_app_executables(app_name) if self.parser else [app_name]
        
        # Try to kill each executable
        killed = False
        for executable in executables:
            try:
                result = subprocess.run(
                    ['pkill', '-f', executable],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    killed = True
                    logger.info(f"Successfully closed: {executable}")
                    
            except Exception as e:
                logger.error(f"Error closing {executable}: {e}")
        
        if killed:
            template = self.parser.get_response_template('success', 'close_app') if self.parser else "{app} has been closed."
            message = template.format(app=app_name.title())
            
            return {
                'success': True,
                'message': message,
                'app': app_name
            }
        else:
            template = self.parser.get_response_template('error', 'not_running') if self.parser else "{app} is not currently running."
            message = template.format(app=app_name.title())
            
            return {
                'success': False,
                'message': message,
                'app': app_name
            }
    
    def _is_executable_available(self, executable):
        """
        Check if an executable is available in PATH.
        
        Args:
            executable: Name of the executable
            
        Returns:
            bool: True if available, False otherwise
        """
        return shutil.which(executable) is not None
