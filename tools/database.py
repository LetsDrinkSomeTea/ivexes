"""Database utilities for accessing SQLite session data."""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any


@dataclass
class Session:
    """Represents a session from the database."""

    session_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


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

    def __post_init__(self):
        """Parse message data after initialization."""
        if isinstance(self.message_data, dict):
            self.role = self.message_data.get('role')
            self.content = self.message_data.get('content')
            self.tool_calls = self.message_data.get('tool_calls')


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

    def __del__(self):
        """Destructor to ensure database connection is closed."""
        self.close()

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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
