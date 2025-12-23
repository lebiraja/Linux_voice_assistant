"""System information query actions."""

import psutil
import logging

logger = logging.getLogger(__name__)


class SystemInfo:
    """Query system information."""
    
    def __init__(self, parser=None):
        """
        Initialize system info handler.
        
        Args:
            parser: CommandParser instance for response templates
        """
        self.parser = parser
    
    def get_info(self, query_type):
        """
        Get system information based on query type.
        
        Args:
            query_type: Type of query (cpu, ram, disk)
            
        Returns:
            dict: Result with 'success', 'message', and 'data'
        """
        logger.info(f"Getting system info: {query_type}")
        
        if query_type == 'cpu':
            return self.get_cpu_usage()
        elif query_type == 'ram':
            return self.get_ram_usage()
        elif query_type == 'disk':
            return self.get_disk_usage()
        else:
            return {
                'success': False,
                'message': "Unknown system query type.",
                'data': None
            }
    
    def get_cpu_usage(self):
        """
        Get CPU usage percentage.
        
        Returns:
            dict: Result with CPU usage
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            template = self.parser.get_response_template('system_info', 'cpu') if self.parser else "CPU usage is {value} percent."
            message = template.format(value=int(cpu_percent))
            
            logger.info(f"CPU usage: {cpu_percent}%")
            
            return {
                'success': True,
                'message': message,
                'data': {'cpu_percent': cpu_percent}
            }
            
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return {
                'success': False,
                'message': "I couldn't get CPU information.",
                'data': None
            }
    
    def get_ram_usage(self):
        """
        Get RAM usage information.
        
        Returns:
            dict: Result with RAM usage
        """
        try:
            memory = psutil.virtual_memory()
            
            total_gb = memory.total / (1024 ** 3)
            available_gb = memory.available / (1024 ** 3)
            used_gb = memory.used / (1024 ** 3)
            percent = memory.percent
            
            template = self.parser.get_response_template('system_info', 'ram') if self.parser else "You have {total} gigabytes of RAM, with {available} gigabytes available."
            message = template.format(
                total=f"{total_gb:.1f}",
                available=f"{available_gb:.1f}"
            )
            
            logger.info(f"RAM: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent}%)")
            
            return {
                'success': True,
                'message': message,
                'data': {
                    'total_gb': total_gb,
                    'available_gb': available_gb,
                    'used_gb': used_gb,
                    'percent': percent
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting RAM usage: {e}")
            return {
                'success': False,
                'message': "I couldn't get RAM information.",
                'data': None
            }
    
    def get_disk_usage(self):
        """
        Get disk usage information.
        
        Returns:
            dict: Result with disk usage
        """
        try:
            disk = psutil.disk_usage('/')
            
            total_gb = disk.total / (1024 ** 3)
            used_gb = disk.used / (1024 ** 3)
            free_gb = disk.free / (1024 ** 3)
            percent = disk.percent
            
            template = self.parser.get_response_template('system_info', 'disk') if self.parser else "Your main disk is {percent} percent full."
            message = template.format(
                percent=int(percent),
                used=f"{used_gb:.1f}",
                total=f"{total_gb:.1f}"
            )
            
            logger.info(f"Disk: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent}%)")
            
            return {
                'success': True,
                'message': message,
                'data': {
                    'total_gb': total_gb,
                    'used_gb': used_gb,
                    'free_gb': free_gb,
                    'percent': percent
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {
                'success': False,
                'message': "I couldn't get disk information.",
                'data': None
            }
