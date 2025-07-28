"""Database utilities for accessing SQLite session data."""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class Session:
    """Represents a session from the database."""

    session_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    def __str__(self) -> str:
        """String representation of the session."""
        return f'Session({self.session_id}, {self.message_count} messages)'


@dataclass
class WorkflowGroup:
    """Represents a grouped multi-agent workflow."""

    workflow_name: str
    workflow_time: str
    sessions: List[Session]
    total_messages: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Calculate aggregate data after initialization."""
        if self.sessions:
            self.total_messages = sum(
                session.message_count for session in self.sessions
            )
            # Use earliest created_at and latest updated_at
            created_times = [
                session.created_at for session in self.sessions if session.created_at
            ]
            updated_times = [
                session.updated_at for session in self.sessions if session.updated_at
            ]
            if created_times:
                self.created_at = min(created_times)
            if updated_times:
                self.updated_at = max(updated_times)

    @property
    def agent_names(self) -> List[str]:
        """Get list of agent names in this workflow."""
        agents = []
        for session in self.sessions:
            session_id = session.session_id
            # Reconstruct the full workflow key
            full_workflow_key = f'{self.workflow_name} {self.workflow_time}'

            # Find where the workflow key appears in the session ID
            if full_workflow_key in session_id:
                # Extract agent name (everything before the workflow key)
                workflow_start = session_id.find(full_workflow_key)
                agent_part = session_id[:workflow_start].rstrip('-')
                agents.append(agent_part)
        return agents

    @property
    def display_name(self) -> str:
        """Get display name for the workflow group."""
        return f'{self.workflow_name}-{self.workflow_time}'


@dataclass
class Message:
    """Represents a message from the database."""

    id: int
    session_id: str
    message_data: Dict[str, Any]
    created_at: datetime
    role: Optional[str] = None
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

    def __post_init__(self) -> None:
        """Parse message data after initialization."""
        if isinstance(self.message_data, dict):
            self.role = self.message_data.get('role')
            self.content = self.message_data.get('content')
            self.tool_calls = self.message_data.get('tool_calls')

    @property
    def agent_name(self) -> Optional[str]:
        """Extract and format agent name from session_id for display."""
        raw_name = self.raw_agent_name
        if raw_name:
            return self._format_agent_name_for_display(raw_name)
        return None

    @property
    def raw_agent_name(self) -> Optional[str]:
        """Extract raw agent name from session_id for internal mapping."""
        # Look for workflow pattern in session ID
        session_id = self.session_id

        # Check if it contains a space followed by a time pattern (indicating workflow)
        import re

        time_pattern = r'\s+\w+-\d{2}:\d{2}:\d{2}$'
        match = re.search(time_pattern, session_id)

        if match:
            # This is a workflow session - extract agent name before the workflow key
            workflow_start = match.start()
            before_workflow = session_id[:workflow_start]

            # Find the last '-' before the workflow to get the agent name
            parts = before_workflow.split('-')
            if len(parts) >= 2:
                # Take everything except the workflow name part
                return '-'.join(parts[:-1])

        return None

    def _format_agent_name_for_display(self, raw_name: str) -> str:
        """Format raw agent name for user-friendly display.

        Args:
            raw_name: Raw agent name like "MultiAgent-multi" or "code-analyst-multi"

        Returns:
            Formatted display name like "MultiAgent" or "Code Analyst"
        """
        # Remove common suffixes
        if raw_name.endswith('-multi'):
            raw_name = raw_name[:-6]

        # Handle special cases
        if raw_name == 'MultiAgent':
            return 'MultiAgent'

        # Convert hyphenated names to title case
        # e.g., "code-analyst" -> "Code Analyst"
        # e.g., "security-specialist" -> "Security Specialist"
        # e.g., "red-team-operator" -> "Red Team Operator"
        words = raw_name.split('-')
        return ' '.join(word.capitalize() for word in words)


class SessionDatabase:
    """Handles database operations for session data."""

    def __init__(self, db_path: Union[str, Path]):
        """Initialize database connection.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f'Database file not found: {self.db_path}')

        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row

    def __del__(self) -> None:
        """Destructor to ensure database connection is closed."""
        if hasattr(self, 'connection'):
            self.close()

    def close(self) -> None:
        """Close database connection."""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self) -> 'SessionDatabase':
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        """Context manager exit."""
        self.close()

    def get_sessions(self) -> List[Session]:
        """Get all sessions with message counts.

        Returns:
            List of Session objects ordered by creation date (newest first).
        """
        query = """
        SELECT 
            s.session_id, 
            s.created_at, 
            s.updated_at,
            COUNT(m.id) as message_count
        FROM agent_sessions s
        LEFT JOIN agent_messages m ON s.session_id = m.session_id
        GROUP BY s.session_id, s.created_at, s.updated_at
        ORDER BY s.created_at DESC
        """

        cursor = self.connection.execute(query)
        sessions = []

        for row in cursor.fetchall():
            session = Session(
                session_id=row['session_id'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                message_count=row['message_count'],
            )
            sessions.append(session)

        return sessions

    def get_workflow_groups(self) -> List[WorkflowGroup]:
        """Get sessions grouped by workflow.

        Returns:
            List of WorkflowGroup objects ordered by creation date (newest first)
        """
        sessions = self.get_sessions()

        # First, find all MultiAgent sessions and extract their workflow keys
        workflow_keys = set()
        for session in sessions:
            if 'MultiAgent-' in session.session_id:
                # Extract everything after 'MultiAgent-' as the workflow key
                key_start = session.session_id.find('MultiAgent-') + len('MultiAgent-')
                workflow_key = session.session_id[key_start:]
                workflow_keys.add(workflow_key)

        # Now group all sessions by these workflow keys
        workflows = {}
        for workflow_key in workflow_keys:
            workflows[workflow_key] = {'workflow_key': workflow_key, 'sessions': []}

        # Match sessions to workflow groups
        for session in sessions:
            for workflow_key in workflow_keys:
                # Check if this session belongs to this workflow
                if workflow_key in session.session_id:
                    workflows[workflow_key]['sessions'].append(session)
                    break

        # Create WorkflowGroup objects
        workflow_groups = []
        for workflow_key, workflow_data in workflows.items():
            if workflow_data['sessions']:  # Only create group if it has sessions
                # Split workflow key to get name and time parts
                # Assume format is "workflow-name time" (e.g., "multi-agent sudo-18:49:01")
                parts = workflow_key.split(' ', 1)
                if len(parts) == 2:
                    workflow_name, workflow_time = parts
                else:
                    workflow_name = workflow_key
                    workflow_time = ''

                group = WorkflowGroup(
                    workflow_name=workflow_name,
                    workflow_time=workflow_time,
                    sessions=workflow_data['sessions'],
                )
                workflow_groups.append(group)

        # Sort by creation date (newest first)
        workflow_groups.sort(key=lambda x: x.created_at, reverse=True)
        return workflow_groups

    def get_workflow_messages(self, workflow_group: WorkflowGroup) -> List[Message]:
        """Get all messages for a workflow group, reordered by conversation flow.

        Args:
            workflow_group: The workflow group to get messages for

        Returns:
            List of Message objects ordered by conversation flow rather than timestamp
        """
        all_messages = []

        for session in workflow_group.sessions:
            session_messages = self.get_session_messages(session.session_id)
            all_messages.extend(session_messages)

        # Reorder messages by conversation flow instead of timestamp
        return self._reorder_workflow_messages(all_messages)

    def _reorder_workflow_messages(self, messages: List[Message]) -> List[Message]:
        """Reorder workflow messages by conversation flow rather than timestamp.

        This method reconstructs the logical conversation flow:
        MultiAgent message → Function call → Subagent messages → Function output → repeat

        Args:
            messages: List of messages from all sessions in the workflow

        Returns:
            List of messages reordered by conversation flow
        """
        if not messages:
            return messages

        # Separate MultiAgent and subagent messages by session
        multiagent_messages = []
        subagent_sessions = {}

        for msg in messages:
            if self._is_multiagent_message(msg):
                multiagent_messages.append(msg)
            else:
                # Group subagent messages by their session ID
                session_id = msg.session_id
                if session_id not in subagent_sessions:
                    subagent_sessions[session_id] = []
                subagent_sessions[session_id].append(msg)

        # Sort MultiAgent messages by timestamp
        multiagent_messages.sort(key=lambda x: x.created_at)

        # Sort messages within each subagent session by timestamp
        for session_messages in subagent_sessions.values():
            session_messages.sort(key=lambda x: x.created_at)

        # Map tool names to subagent sessions
        tool_to_session = {}
        for session_id, session_messages in subagent_sessions.items():
            if session_messages:
                raw_agent_name = session_messages[0].raw_agent_name
                if raw_agent_name:
                    # Extract base tool name from agent name
                    base_name = raw_agent_name
                    if base_name.endswith('-multi'):
                        base_name = base_name[:-6]
                    tool_to_session[base_name] = session_messages

        # Reconstruct the conversation flow
        reordered_messages = []
        used_sessions = set()

        for msg in multiagent_messages:
            reordered_messages.append(msg)

            # Check if this is a function call
            if msg.message_data.get('type') == 'function_call':
                tool_name = msg.message_data.get('name')

                # Add the corresponding subagent session if we haven't used it yet
                if tool_name in tool_to_session and tool_name not in used_sessions:
                    subagent_messages = tool_to_session[tool_name]
                    reordered_messages.extend(subagent_messages)
                    used_sessions.add(tool_name)

        # Add any remaining subagent sessions that weren't matched
        for tool_name, session_messages in tool_to_session.items():
            if tool_name not in used_sessions:
                reordered_messages.extend(session_messages)

        return reordered_messages

    def _is_multiagent_message(self, message: Message) -> bool:
        """Determine if a message is from MultiAgent (vs a subagent).

        Args:
            message: The message to check

        Returns:
            True if the message is from MultiAgent, False if from a subagent
        """
        session_id = message.session_id

        # MultiAgent sessions contain 'MultiAgent-' in their session ID
        # Subagent sessions have agent names before the MultiAgent workflow key
        if 'MultiAgent-' in session_id:
            # Check if there's an agent name before 'MultiAgent-'
            multiagent_index = session_id.find('MultiAgent-')
            before_multiagent = session_id[:multiagent_index].rstrip('-')

            # If there's content before 'MultiAgent-', it's a subagent
            return not bool(before_multiagent)

        return False

    def get_session_messages(self, session_id: str) -> List[Message]:
        """Get all messages for a specific session.

        Args:
            session_id: The session ID to get messages for.

        Returns:
            List of Message objects ordered by creation time.
        """
        query = """
        SELECT id, session_id, message_data, created_at
        FROM agent_messages
        WHERE session_id = ?
        ORDER BY created_at ASC
        """

        cursor = self.connection.execute(query, (session_id,))
        messages = []

        for row in cursor.fetchall():
            try:
                message_data = json.loads(row['message_data'])
            except json.JSONDecodeError:
                message_data = {'content': row['message_data'], 'role': 'unknown'}

            message = Message(
                id=row['id'],
                session_id=row['session_id'],
                message_data=message_data,
                created_at=datetime.fromisoformat(row['created_at']),
            )
            messages.append(message)

        return messages

    def search_sessions(self, search_term: str) -> List[Session]:
        """Search sessions by session ID or message content.

        Args:
            search_term: Term to search for.

        Returns:
            List of matching Session objects.
        """
        query = """
        SELECT DISTINCT 
            s.session_id, 
            s.created_at, 
            s.updated_at,
            COUNT(m.id) as message_count
        FROM agent_sessions s
        LEFT JOIN agent_messages m ON s.session_id = m.session_id
        WHERE s.session_id LIKE ? OR m.message_data LIKE ?
        GROUP BY s.session_id, s.created_at, s.updated_at
        ORDER BY s.created_at DESC
        """

        search_pattern = f'%{search_term}%'
        cursor = self.connection.execute(query, (search_pattern, search_pattern))
        sessions = []

        for row in cursor.fetchall():
            session = Session(
                session_id=row['session_id'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                message_count=row['message_count'],
            )
            sessions.append(session)

        return sessions

    def find_tool_calls(
        self, tool_name: Optional[str] = None, session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find tool calls across all sessions or in a specific session.

        Args:
            tool_name: Optional tool name to filter by (e.g., 'create_file').
            session_id: Optional session ID to limit search to.

        Returns:
            List of dictionaries containing tool call information.
        """
        base_query = """
        SELECT m.session_id, m.id, m.message_data, m.created_at, s.created_at as session_created
        FROM agent_messages m
        JOIN agent_sessions s ON m.session_id = s.session_id
        WHERE m.message_data LIKE '%tool_call%'
        """

        params = []
        if session_id:
            base_query += ' AND m.session_id = ?'
            params.append(session_id)

        base_query += ' ORDER BY s.created_at DESC, m.created_at ASC'

        cursor = self.connection.execute(base_query, params)
        tool_calls = []

        for row in cursor.fetchall():
            try:
                message_data = json.loads(row['message_data'])
                if 'tool_calls' in message_data:
                    for tool_call in message_data['tool_calls']:
                        if (
                            tool_name is None
                            or tool_call.get('function', {}).get('name') == tool_name
                        ):
                            tool_calls.append(
                                {
                                    'session_id': row['session_id'],
                                    'message_id': row['id'],
                                    'session_created': row['session_created'],
                                    'message_created': row['created_at'],
                                    'tool_call': tool_call,
                                }
                            )
            except (json.JSONDecodeError, KeyError):
                continue

        return tool_calls

    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the database.

        Returns:
            Dictionary containing database statistics.
        """
        stats = {}

        # Total sessions
        cursor = self.connection.execute('SELECT COUNT(*) FROM agent_sessions')
        stats['total_sessions'] = cursor.fetchone()[0]

        # Total messages
        cursor = self.connection.execute('SELECT COUNT(*) FROM agent_messages')
        stats['total_messages'] = cursor.fetchone()[0]

        # Date range
        cursor = self.connection.execute(
            'SELECT MIN(created_at), MAX(created_at) FROM agent_sessions'
        )
        date_range = cursor.fetchone()
        if date_range[0] and date_range[1]:
            stats['earliest_session'] = datetime.fromisoformat(date_range[0])
            stats['latest_session'] = datetime.fromisoformat(date_range[1])

        # Tool call counts
        tool_calls = self.find_tool_calls()
        tool_counts = {}
        for tc in tool_calls:
            tool_name = tc['tool_call'].get('function', {}).get('name', 'unknown')
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        stats['tool_call_counts'] = tool_counts

        return stats


def get_database_stats(db_path: Union[str, Path]) -> str:
    """Get statistics about the session database.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        Dictionary containing database statistics.
    """
    with SessionDatabase(db_path) as db:
        stats = db.get_database_stats()
    return '\n'.join(
        f'{str(key).replace("_", " ").title()}: {value}' for key, value in stats.items()
    )
