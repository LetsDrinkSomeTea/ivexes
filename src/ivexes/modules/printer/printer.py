from agents import RunItem
from agents.items import HandoffCallItem, HandoffOutputItem, ItemHelpers, MessageOutputItem, ReasoningItem, ToolCallItem, ToolCallOutputItem
from agents.result import RunResult
import ivexes.config.log as log
logger = log.get(__name__)

def print_result(result: RunResult):
    """Prints the result of a run and returns the input list for the next run."""
    print_items(result.new_items)
    return result.to_input_list()

def print_items(items: list[RunItem]):
    for item in items:
        if isinstance(item, MessageOutputItem):
            print(f'{"Agent":=^80}\n{ItemHelpers.text_message_output(item)}\n')
        if isinstance(item, ToolCallItem):
            print(f'{"Tool Call":=^80}\n{item.raw_item}\n')
        if isinstance(item, ToolCallOutputItem):
            print(f'{"Tool Output":=^80}\n{item.output}\n')
        if isinstance(item, HandoffCallItem):
            print(f'{"Handoff Call":=^80}\n{item.raw_item}\n')
        if isinstance(item, HandoffOutputItem):
            print(f'{"Handoff Output":=^80}\n{item.source_agent} -> {item.target_agent}\n')
        if isinstance(item, ReasoningItem):
            print(f'{"Reasoning":=^80}\n{item.raw_item}\n')

