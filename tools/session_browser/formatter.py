"""Message formatting functionality for the session browser.

This module provides type-specific formatting for different message types,
converting raw database message data into user-friendly display formats.
"""

import json
from typing import Dict, Any, Tuple, List
from ..database import Message as DBMessage
from .config import BrowserSettings


class MessageFormatter:
    """Handles type-specific formatting of database messages.

    Provides clean, readable formatting for different message types while
    preserving access to complete metadata when needed.

    Supported message types:
    - function_call: Tool invocations with clean syntax
    - function_call_output: Tool results with formatted output
    - output_text: Assistant responses with extracted text content
    - regular: User/assistant messages with role indicators

    Example:
        >>> formatter = MessageFormatter()
        >>> content, metadata = formatter.format_message(message)
        >>> print(content)
        🔧 Function Call
        setup_sandbox()
    """

    def __init__(self, show_metadata: bool = False):
        """Initialize the formatter.

        Args:
            show_metadata: Whether to show metadata view by default
        """
        self.show_metadata = show_metadata

    def format_message(self, message: DBMessage) -> Tuple[str, Dict[str, Any]]:
        """Format a message for display with enhanced type-specific formatting.

        Args:
            message: The database message to format

        Returns:
            Tuple of (formatted_content, metadata_dict)
        """
        if self.show_metadata:
            return self._format_metadata(message)

        # Detect message type and format accordingly
        msg_type = message.message_data.get('type')

        if msg_type == 'function_call':
            return self._format_function_call(message)
        elif msg_type == 'function_call_output':
            return self._format_function_output(message)
        elif self._is_output_text_message(message):
            return self._format_output_text(message)
        else:
            return self._format_regular_message(message)

    def _format_function_call(self, message: DBMessage) -> Tuple[str, Dict[str, Any]]:
        """Format function call message as: function_name(arg1=value1, arg2=value2).

        Args:
            message: Database message with function call data

        Returns:
            Tuple of (formatted_content, metadata)
        """
        data = message.message_data
        function_name = data.get('name', 'unknown_function')

        # Parse arguments
        arguments = data.get('arguments', '{}')
        if isinstance(arguments, str):
            try:
                args_dict = json.loads(arguments)
            except json.JSONDecodeError:
                args_dict = {'raw': arguments}
        else:
            args_dict = arguments or {}

        # Format arguments as function call syntax
        formatted_call = self._format_function_signature(function_name, args_dict)

        # Get type indicator
        icon = BrowserSettings.TYPE_INDICATORS.get('function_call', '🔧')
        content = f'[bold]{icon} Function Call[/bold]\n{formatted_call}'

        metadata = {
            'time': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'call_id': data.get('call_id'),
            'raw_arguments': arguments,
            'function_name': function_name,
            'parsed_arguments': args_dict,
            'full_data': data,
        }

        return content, metadata

    def _format_function_output(self, message: DBMessage) -> Tuple[str, Dict[str, Any]]:
        """Format function call output with clean text display.

        Args:
            message: Database message with function output data

        Returns:
            Tuple of (formatted_content, metadata)
        """
        data = message.message_data
        output = data.get('output', '')

        # Format output with appropriate styling
        formatted_output = self._format_output_content(output)

        # Get type indicator
        icon = BrowserSettings.TYPE_INDICATORS.get('function_call_output', '📤')
        content = f'[bold]{icon} Output[/bold]\n{formatted_output}'

        metadata = {
            'time': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'call_id': data.get('call_id'),
            'output_length': len(str(output)),
            'output_type': self._detect_output_type(output),
            'full_data': data,
        }

        return content, metadata

    def _format_output_text(self, message: DBMessage) -> Tuple[str, Dict[str, Any]]:
        """Format output_text message by extracting just the text content.

        Args:
            message: Database message with output_text content

        Returns:
            Tuple of (formatted_content, metadata)
        """
        content_list = message.message_data.get('content', [])
        text_parts = []
        annotations_list = []

        # Extract text content and annotations
        for item in content_list:
            if isinstance(item, dict) and item.get('type') == 'output_text':
                text_parts.append(item.get('text', ''))
                annotations_list.append(item.get('annotations', []))

        if text_parts:
            formatted_content = '\n'.join(text_parts)
        else:
            # Fallback to regular content if no output_text found
            formatted_content = (
                str(message.content) if message.content else 'No content'
            )

        # Get role and appropriate icon
        role = message.message_data.get('role', 'assistant')
        icon = BrowserSettings.TYPE_INDICATORS.get(role, '🤖')

        content = f'[bold]{icon} {role.title()} Response[/bold]\n{formatted_content}'

        metadata = {
            'time': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'role': role,
            'status': message.message_data.get('status'),
            'annotations': annotations_list,
            'text_parts_count': len(text_parts),
            'content_length': len(formatted_content),
            'full_data': message.message_data,
        }

        return content, metadata

    def _format_regular_message(self, message: DBMessage) -> Tuple[str, Dict[str, Any]]:
        """Format regular user/assistant messages.

        Args:
            message: Database message with regular content

        Returns:
            Tuple of (formatted_content, metadata)
        """
        role = message.role or message.message_data.get('role', 'unknown')
        content = message.content or message.message_data.get('content', 'No content')

        # Get appropriate icon for role
        icon = BrowserSettings.TYPE_INDICATORS.get(role, '❓')

        formatted_content = f'[bold]{icon} {role.title()}[/bold]\n{content}'

        metadata = {
            'time': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'role': role,
            'content_length': len(str(content)),
            'message_type': 'regular',
            'full_data': message.message_data,
        }

        return formatted_content, metadata

    def _format_metadata(self, message: DBMessage) -> Tuple[str, Dict[str, Any]]:
        """Format complete message metadata in JSON.

        Args:
            message: Database message to show metadata for

        Returns:
            Tuple of (formatted_metadata_content, metadata)
        """
        metadata = {
            'id': message.id,
            'session_id': message.session_id,
            'created_at': message.created_at.isoformat(),
            'message_data': message.message_data,
            'parsed_role': message.role,
            'parsed_content': message.content,
            'parsed_tool_calls': message.tool_calls,
        }

        try:
            formatted_json = json.dumps(metadata, indent=2, default=str)
        except Exception:
            formatted_json = str(metadata)

        content = f'[bold]🔍 Complete Metadata[/bold]\n{formatted_json}'

        return content, metadata

    def _format_function_signature(
        self, function_name: str, args_dict: Dict[str, Any]
    ) -> str:
        """Format function call with arguments as readable signature.

        Args:
            function_name: Name of the function
            args_dict: Dictionary of function arguments

        Returns:
            Formatted function signature string
        """
        if not args_dict:
            return f'[cyan]{function_name}[/cyan]()'

        arg_parts = []
        for key, value in args_dict.items():
            formatted_value = self._format_argument_value(value)
            arg_parts.append(f'{key}={formatted_value}')

        args_str = ', '.join(arg_parts)
        return f'[cyan]{function_name}[/cyan]({args_str})'

    def _format_argument_value(self, value: Any) -> str:
        """Format a function argument value for display.

        Args:
            value: The argument value to format

        Returns:
            Formatted value string
        """
        if isinstance(value, str):
            if len(value) > BrowserSettings.ARGUMENT_TRUNCATION_LENGTH:
                # Truncate long string values
                truncated = value[: BrowserSettings.ARGUMENT_TRUNCATION_LENGTH - 3]
                return f'"{truncated}..."'
            else:
                return f'"{value}"'
        elif isinstance(value, (dict, list)):
            # For complex types, show type and length
            type_name = type(value).__name__
            length = len(value)
            return f'<{type_name}[{length}]>'
        else:
            return str(value)

    def _format_output_content(self, output: Any) -> str:
        """Format function output content with appropriate styling.

        Args:
            output: The output content to format

        Returns:
            Formatted output string
        """
        if not isinstance(output, str):
            output = str(output)

        # Detect if it's code/terminal output and apply styling
        if self._is_terminal_output(output):
            return f'[dim]{output}[/dim]'
        else:
            return output

    def _is_terminal_output(self, text: str) -> bool:
        """Detect if text appears to be terminal/command output.

        Args:
            text: Text to analyze

        Returns:
            True if text appears to be terminal output
        """
        terminal_indicators = ['$', '>', 'error:', 'warning:', 'info:', '~/']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in terminal_indicators)

    def _detect_output_type(self, output: Any) -> str:
        """Detect the type of function output.

        Args:
            output: Output content to analyze

        Returns:
            String describing the output type
        """
        if not isinstance(output, str):
            return type(output).__name__

        if self._is_terminal_output(output):
            return 'terminal'
        elif output.strip().startswith('{') and output.strip().endswith('}'):
            return 'json'
        elif '\n' in output:
            return 'multiline_text'
        else:
            return 'text'

    def _is_output_text_message(self, message: DBMessage) -> bool:
        """Check if message contains output_text content.

        Args:
            message: Database message to check

        Returns:
            True if message contains output_text content
        """
        content = message.message_data.get('content', [])
        if isinstance(content, list):
            return any(
                isinstance(item, dict) and item.get('type') == 'output_text'
                for item in content
            )
        return False

    def toggle_metadata_view(self) -> bool:
        """Toggle between normal and metadata view.

        Returns:
            New metadata view state (True if now showing metadata)
        """
        self.show_metadata = not self.show_metadata
        return self.show_metadata

    def set_metadata_view(self, show_metadata: bool) -> None:
        """Set metadata view state.

        Args:
            show_metadata: Whether to show metadata view
        """
        self.show_metadata = show_metadata
