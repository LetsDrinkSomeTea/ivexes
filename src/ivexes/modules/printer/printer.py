from agents import RunItem
from agents.items import HandoffCallItem, HandoffOutputItem, ItemHelpers, MessageOutputItem, ReasoningItem, ToolCallItem, ToolCallOutputItem
from agents.result import RunResult, RunResultStreaming
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputItemAddedEvent, ResponseOutputItemDoneEvent, ResponseTextDeltaEvent
import json
import time

from ivexes.modules.printer.components import banner
TIME_STRING = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def print_and_write_to_file(text: str, truncate: bool = True, end="\n"):
    lines = text.splitlines()
    if truncate and len(lines) > 10:
        lines = lines [:10] + [f'... truncated {len(lines) - 10} lines']
    print('\n'.join(lines), end=end)
    with open(f'output-{TIME_STRING}.txt', 'a') as f:
        f.write(text + end)


def print_result(result: RunResult):
    """Prints the result of a run and returns the input list for the next run."""
    print_items(result.new_items)
    return result.to_input_list()

def print_items(items: list[RunItem]):
    for item in items:
        if isinstance(item, MessageOutputItem):
            print_and_write_to_file(f'{"Agent":=^80}\n{ItemHelpers.text_message_output(item)}\n')
        if isinstance(item, ToolCallItem):
            ret_val = item.raw_item
            if isinstance(ret_val, ResponseFunctionToolCall):
                formatted_args = ', '.join(f'{k}={repr(v)}' for k, v in json.loads(ret_val.arguments).items())
                ret_val = f'{ret_val.name}({formatted_args})'
            print_and_write_to_file(f'{"Tool Call":=^80}\n{ret_val}\n')
        if isinstance(item, ToolCallOutputItem):
            print_and_write_to_file(f'{"Tool Output":=^80}\n{item.output}\n')
        if isinstance(item, HandoffCallItem):
            print_and_write_to_file(f'{"Handoff Call":=^80}\n{item.raw_item}\n')
        if isinstance(item, HandoffOutputItem):
            print_and_write_to_file(f'{"Handoff Output":=^80}\n{item.source_agent} -> {item.target_agent}\n')
        if isinstance(item, ReasoningItem):
            print_and_write_to_file(f'{"Reasoning":=^80}\n{item.raw_item}\n')

async def stream_result(result: RunResultStreaming):
    async for event in result.stream_events():
        if event.type == "raw_response_event":
            continue
        elif event.type == "agent_updated_stream_event":
            continue
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                ret_val = event.item.raw_item
                if isinstance(ret_val, ResponseFunctionToolCall):
                    formatted_args = ', '.join(f'{k}={repr(v)}' for k, v in json.loads(ret_val.arguments).items())
                    ret_val = f'{ret_val.name}({formatted_args})'
                print_and_write_to_file(f'[{result.current_turn}]{"Tool Call":=^80}\n{ret_val}\n')
            elif event.item.type == "tool_call_output_item":
                print_and_write_to_file(f'[{result.current_turn}]{"Tool Output":=^80}\n{(event.item.output)}\n')
            elif event.item.type == "message_output_item":
                print_and_write_to_file(f'[{result.current_turn}]{"Agent":=^80}\n{ItemHelpers.text_message_output(event.item)}\n')
            else:
                print_and_write_to_file(f'[{result.current_turn}]{f"Unknown Item {event.item.type}":=^80}\n{event.item}\n')
    return result.to_input_list()

def print_banner(
    model: str,
    temperature: float,
    max_turns: int,
    program_name: str
) -> None:
    print_and_write_to_file(
        banner(model=model,
               temperature=temperature,
               max_turns=max_turns,
               program_name=program_name
               ),
        truncate=False
    )

