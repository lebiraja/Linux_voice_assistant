"""Response generation utilities."""

import logging

logger = logging.getLogger(__name__)


def generate_response(result, parser=None):
    """
    Generate a natural language response from action result.
    
    Args:
        result: Result dictionary from action
        parser: Optional CommandParser for templates
        
    Returns:
        str: Response message
    """
    if result is None:
        return "I encountered an error processing your request."
    
    return result.get('message', "Operation completed.")


def get_error_response(error_type, parser=None):
    """
    Get error response message.
    
    Args:
        error_type: Type of error
        parser: Optional CommandParser for templates
        
    Returns:
        str: Error message
    """
    error_messages = {
        'transcription_failed': "I couldn't hear you clearly. Please try again.",
        'unknown_command': "I didn't understand that command. Try saying 'open firefox' or 'what's my CPU usage'.",
        'no_audio': "No audio was recorded. Please try again.",
        'general': "I encountered an error. Please try again."
    }
    
    if parser:
        try:
            return parser.get_response_template('error', error_type)
        except:
            pass
    
    return error_messages.get(error_type, error_messages['general'])
