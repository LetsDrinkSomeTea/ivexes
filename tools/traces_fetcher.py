#!/usr/bin/env python3
"""OpenAI Traces and Spans Fetcher.

Fetches all traces and their spans from OpenAI API and stores them in SQLite.
"""

import sys
import requests
import sqlite3
import json
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OpenAITracesFetcher:
    """Fetches traces and spans from OpenAI API and stores them in SQLite database."""

    def __init__(
        self,
        bearer_token: str,
        organization: str,
        project: str,
        db_path: str = 'traces.sqlite',
    ):
        """Initialize the fetcher with authentication details.

        Args:
            bearer_token: Your OpenAI session bearer token
            organization: Your OpenAI organization ID
            project: Your OpenAI project ID
            db_path: Path to SQLite database file
        """
        self.bearer_token = bearer_token
        self.organization = organization
        self.project = project
        self.db_path = db_path

        # Create a session to handle compression and connection pooling
        self.session = requests.Session()

        # Base headers for all requests
        self.headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'de-DE,de;q=0.9',
            'authorization': f'Bearer {bearer_token}',
            'openai-beta': 'traces=v1',
            'openai-organization': organization,
            'openai-project': project,
            'origin': 'https://platform.openai.com',
            'referer': 'https://platform.openai.com/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        }

        # Update session headers
        self.session.headers.update(self.headers)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create traces table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                id TEXT PRIMARY KEY,
                object TEXT,
                created_at TEXT,
                duration_ms INTEGER,
                first_5_agents TEXT,
                group_id TEXT,
                handoff_count INTEGER,
                tool_count INTEGER,
                workflow_name TEXT,
                metadata TEXT,
                fetched_at TEXT
            )
        """)

        # Create spans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spans (
                id TEXT PRIMARY KEY,
                trace_id TEXT,
                object TEXT,
                created_at TEXT,
                duration_ms INTEGER,
                ended_at TEXT,
                error TEXT,
                parent_id TEXT,
                span_data TEXT,
                speech_group_output TEXT,
                started_at TEXT,
                fetched_at TEXT,
                FOREIGN KEY (trace_id) REFERENCES traces(id)
            )
        """)

        # Create indexes for better performance
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_spans_trace_id ON spans(trace_id)'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_spans_parent_id ON spans(parent_id)'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_traces_created_at ON traces(created_at)'
        )

        conn.commit()
        conn.close()
        logger.info(f'Database initialized at {self.db_path}')

    def fetch_traces(
        self, after: Optional[str] = None, limit: Optional[int] = None
    ) -> tuple:
        """Fetch traces from OpenAI API.

        Args:
            after: Trace ID to start after (for pagination)
            limit: Maximum number of traces to fetch

        Returns:
            API response as dictionary
        """
        url = 'https://api.openai.com/v1/dashboard/traces'
        params: dict[str, Any] = {
            'include[]': [
                'first_5_agents',
                'tool_count',
                'handoff_count',
                'duration_ms',
            ]
        }

        if after:
            params['after'] = after

        response = self.session.get(url, params=params)

        # Debug logging
        logger.debug(f'Response status code: {response.status_code}')
        logger.debug(f'Response headers: {response.headers}')
        logger.debug(
            f'Content-Encoding: {response.headers.get("Content-Encoding", "none")}'
        )

        # Check for common error responses
        if response.status_code == 401:
            logger.error('Authentication failed - check your bearer token')
            logger.error(f'Response: {response.text[:500]}')
            raise ValueError('Authentication failed')
        elif response.status_code == 403:
            logger.error('Forbidden - check your organization and project IDs')
            logger.error(f'Response: {response.text[:500]}')
            raise ValueError('Access forbidden')
        elif response.status_code != 200:
            logger.error(f'Unexpected status code: {response.status_code}')
            logger.error(f'Response: {response.text[:500]}')
            response.raise_for_status()

        # Check for empty response
        if not response.text:
            logger.error('Empty response received')
            raise ValueError('Empty response from API')

        # Try to parse JSON
        try:
            response_json = response.json()
            data = response_json.get('data', [])
            if limit:
                data = data[:limit]
            return (
                data,
                response_json.get('has_more', False),
                response_json.get('last_id', None),
            )
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse JSON response: {e}')
            logger.error(f'Response content (first 500 chars): {response.text[:500]}')
            # Check if it's HTML
            if response.text.strip().startswith('<'):
                logger.error('Response appears to be HTML instead of JSON')
            raise

    def fetch_spans(self, trace_id: str, after: Optional[str] = None) -> Dict:
        """Fetch spans for a specific trace.

        Args:
            trace_id: The trace ID to fetch spans for
            after: Span ID to start after (for pagination)

        Returns:
            API response as dictionary
        """
        url = f'https://api.openai.com/v1/dashboard/traces/{trace_id}/spans'
        params = {'include[]': ['duration_ms', 'speech_group_output'], 'order': 'asc'}

        if after:
            params['after'] = after

        response = self.session.get(url, params=params)

        # Debug logging
        logger.debug(f'Response status code: {response.status_code}')

        # Check for errors
        if response.status_code != 200:
            logger.error(
                f'Error fetching spans for trace {trace_id}: {response.status_code}'
            )
            logger.debug(f'Response: {response.text[:500]}')
            response.raise_for_status()

        # Check for empty response
        if not response.text:
            logger.error(f'Empty response for spans of trace {trace_id}')
            raise ValueError('Empty response from API')

        # Try to parse JSON
        try:
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse JSON response for spans: {e}')
            logger.error(f'Response content (first 500 chars): {response.text[:500]}')
            raise

    def fetch_all_spans(self, trace_id: str) -> List[Dict]:
        """Fetch all spans for a given trace ID, handling pagination.

        Args:
            trace_id: The trace ID to fetch spans for

        Returns:
            List of all spans for the trace
        """
        spans: list[dict] = []
        response = self.fetch_spans(trace_id=trace_id)
        spans.extend(response.get('data', []))

        while response.get('has_more', False):
            logger.info(f'Fetching more spans for trace {trace_id}...')
            response = self.fetch_spans(
                trace_id=trace_id, after=response.get('last_id')
            )
            spans.extend(response.get('data', []))

        return spans

    def save_trace(self, trace: Dict):
        """Save a single trace to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO traces 
            (id, object, created_at, duration_ms, first_5_agents, group_id, 
             handoff_count, tool_count, workflow_name, metadata, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                trace.get('id'),
                trace.get('object'),
                trace.get('created_at'),
                trace.get('duration_ms'),
                json.dumps(trace.get('first_5_agents', [])),
                trace.get('group_id'),
                trace.get('handoff_count'),
                trace.get('tool_count'),
                trace.get('workflow_name'),
                json.dumps(trace.get('metadata', {})),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def save_spans(self, trace_id: str, spans: List[Dict]):
        """Save spans for a trace to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for span in spans:
            cursor.execute(
                """
                INSERT OR REPLACE INTO spans 
                (id, trace_id, object, created_at, duration_ms, ended_at, 
                 error, parent_id, span_data, speech_group_output, started_at, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    span.get('id'),
                    trace_id,
                    span.get('object'),
                    span.get('created_at'),
                    span.get('duration_ms'),
                    span.get('ended_at'),
                    json.dumps(span.get('error')) if span.get('error') else None,
                    span.get('parent_id'),
                    json.dumps(span.get('span_data', {})),
                    json.dumps(span.get('speech_group_output'))
                    if span.get('speech_group_output')
                    else None,
                    span.get('started_at'),
                    datetime.now().isoformat(),
                ),
            )

        conn.commit()
        conn.close()

    def fetch_all_data(
        self, limit: Optional[int] = None, rate_limit_delay: float = 0.5
    ):
        """Fetch all traces and their spans, handling pagination.

        Args:
            rate_limit_delay: Delay between API calls to avoid rate limiting
            limit: Maximum number of traces to fetch (for testing)
        """
        logger.info(
            f'Starting to fetch {limit if limit else "all"} traces and spans...'
        )

        after = None
        total_traces = 0
        total_spans = 0

        while True:
            try:
                # Fetch traces
                logger.info(f'Fetching traces (after={after})...')
                traces, has_more, last_id = self.fetch_traces(after, limit)

                if not traces:
                    logger.info('No more traces to fetch')
                    break

                # Process each trace
                for trace in traces:
                    trace_id = trace.get('id')
                    logger.info(f'Processing trace {trace_id}')

                    # Save trace
                    self.save_trace(trace)
                    total_traces += 1

                    # Fetch and save spans for this trace
                    try:
                        time.sleep(rate_limit_delay)  # Rate limiting
                        spans = self.fetch_all_spans(trace_id)

                        self.save_spans(trace_id, spans)
                        total_spans += len(spans)
                        logger.info(
                            f'  - Saved {len(spans)} spans for trace {trace_id}'
                        )

                    except requests.exceptions.HTTPError as e:
                        logger.error(
                            f'  - Error fetching spans for trace {trace_id}: {e}'
                        )
                        continue

                # Check if there are more traces
                if has_more and not limit:
                    after = last_id
                    logger.info(f'More traces available, continuing with after={after}')
                    time.sleep(rate_limit_delay)  # Rate limiting
                else:
                    logger.info('No more traces available')
                    break

            except requests.exceptions.RequestException as e:
                logger.error(f'Error fetching traces: {e}')
                break
            except Exception as e:
                logger.error(f'Unexpected error: {e}')
                break

        logger.info(
            f'Finished! Total traces: {total_traces}, Total spans: {total_spans}'
        )

    def get_statistics(self):
        """Get statistics about the fetched data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get counts
        cursor.execute('SELECT COUNT(*) FROM traces')
        trace_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM spans')
        span_count = cursor.fetchone()[0]

        # Get date range
        cursor.execute(
            'SELECT MIN(created_at), MAX(created_at) FROM traces WHERE created_at IS NOT NULL'
        )
        date_range = cursor.fetchone()

        conn.close()

        return {
            'total_traces': trace_count,
            'total_spans': span_count,
            'earliest_trace': date_range[0],
            'latest_trace': date_range[1],
        }


def main():
    """Main function to run the fetcher."""
    # Configuration - REPLACE THESE WITH YOUR ACTUAL VALUES
    # You can find these values in your browser's developer tools when logged into platform.openai.com

    # From your authorization header: Bearer sess-...
    BEARER_TOKEN = 'sess-KORTNYvXwjghDxPCmcIqWIdo9J48yuPNBeZboI2G'
    ORGANIZATION = 'org-cfz7E1qZcHSPDa23eB3PDtr0'
    PROJECT = 'proj_WNfnNLTU3QzQnHmafPBkH05N'

    parser = argparse.ArgumentParser(description='OpenAI Traces Fetcher')
    parser.add_argument(
        '-l',
        '--limit',
        type=int,
        help='only the n newest traces to fetch',
        default=None,
    )
    args = parser.parse_args()

    # Check if credentials are set
    if 'YOUR_SESSION_TOKEN_HERE' in BEARER_TOKEN:
        print('ERROR: Please update the BEARER_TOKEN with your actual session token')
        print("You can find this in your browser's developer tools:")
        print('1. Open platform.openai.com in your browser')
        print('2. Open Developer Tools (F12)')
        print('3. Go to Network tab')
        print('4. Look for any API request to api.openai.com')
        print("5. Find the 'authorization' header - copy the value after 'Bearer '")
        return

    # Create fetcher instance
    fetcher = OpenAITracesFetcher(
        bearer_token=BEARER_TOKEN,
        organization=ORGANIZATION,
        project=PROJECT,
        db_path='traces.db',
    )

    try:
        # Fetch all data
        try:
            fetcher.fetch_all_data(rate_limit_delay=0.5, limit=args.limit)
        except KeyboardInterrupt:
            print('Aborted')

        # Print statistics
        stats = fetcher.get_statistics()
        print('\nFetch complete! Statistics:')
        print(f'Total traces: {stats["total_traces"]}')
        print(f'Total spans: {stats["total_spans"]}')
        print(f'Date range: {stats["earliest_trace"]} to {stats["latest_trace"]}')

    except ValueError as e:
        print(f'\nError: {e}')
        print('\nTroubleshooting tips:')
        print("1. Make sure you're logged into platform.openai.com")
        print('2. Session tokens expire - get a fresh one from your browser')
        print('3. Verify your organization and project IDs are correct')
    except Exception as e:
        print(f'\nUnexpected error: {e}')


if __name__ == '__main__':
    main()
