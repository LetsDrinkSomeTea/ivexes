"""Export trace data from SQLite database to CSV file.

This script connects to a SQLite database, retrieves trace and span data,
aggregates it, and writes the results to a CSV file.
"""

import sys
import sqlite3
import json
import csv


def export_traces_to_csv(db_path, csv_path):
    """Extract and aggregate trace data from SQLite database and export to CSV."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT id, workflow_name, duration_ms, created_at FROM traces')
    traces = cursor.fetchall()

    with open(csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(
            [
                'workflow_name',
                'created_at',
                'model_name',
                'input_tokens',
                'output_tokens',
                'cached_tokens',
                'reasoning_tokens',
                'trace_duration_ms',
                'duration_generation_ms',
                'duration_function_ms',
                'trace_id',
            ]
        )

        for trace in traces:
            trace_id, workflow_name, trace_duration_ms, created_at = trace
            cursor.execute(
                'SELECT span_data, duration_ms FROM spans WHERE trace_id = ?',
                (trace_id,),
            )
            spans = cursor.fetchall()

            model_name = None
            total_input_tokens = 0
            total_output_tokens = 0
            total_cached_tokens = 0
            total_reasoning_tokens = 0
            duration_generation_ms = 0
            duration_function_ms = 0

            for span in spans:
                span_data_json, span_duration_ms = span
                try:
                    span_data = json.loads(span_data_json)
                    if span_data.get('type') == 'generation':
                        duration_generation_ms += (
                            span_duration_ms if span_duration_ms else 0
                        )
                        if 'model' in span_data:
                            if not model_name and span_data.get('model') != '':
                                model_name = span_data.get('model')
                        if 'usage' in span_data:
                            usage = span_data.get('usage')
                            if usage:
                                total_input_tokens += usage.get('input_tokens', 0) or 0
                                total_output_tokens += (
                                    usage.get('output_tokens', 0) or 0
                                )
                        if 'input' in span_data and isinstance(
                            span_data['input'], list
                        ):
                            for item in span_data['input']:
                                if isinstance(item, dict) and 'usage' in item:
                                    usage = item.get('usage')
                                    if usage:
                                        total_cached_tokens += (
                                            usage.get('cached_tokens', 0) or 0
                                        )
                                        total_reasoning_tokens += (
                                            usage.get('reasoning_tokens', 0) or 0
                                        )
                    elif span_data.get('type') == 'function':
                        duration_function_ms += (
                            span_duration_ms if span_duration_ms else 0
                        )

                except (json.JSONDecodeError, TypeError):
                    continue

            csv_writer.writerow(
                [
                    workflow_name,
                    created_at,
                    model_name,
                    total_input_tokens,
                    total_output_tokens,
                    total_cached_tokens,
                    total_reasoning_tokens,
                    trace_duration_ms,
                    duration_generation_ms,
                    duration_function_ms,
                    trace_id,
                ]
            )

    conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python export_traces.py <database_path> <csv_output_path>')
        sys.exit(1)
    export_traces_to_csv(sys.argv[1], sys.argv[2])
