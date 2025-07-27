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
        """Extract agent name from session_id for workflow context."""
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
        """Get all messages for a workflow group, merged and sorted by creation time.

        Args:
            workflow_group: The workflow group to get messages for

        Returns:
            List of Message objects sorted by creation time across all sessions
        """
        all_messages = []

        for session in workflow_group.sessions:
            session_messages = self.get_session_messages(session.session_id)
            all_messages.extend(session_messages)

        # Sort all messages by creation time
        all_messages.sort(key=lambda x: x.created_at)
        return all_messages

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
