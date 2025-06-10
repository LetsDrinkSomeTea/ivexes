from agents import RunItem
from agents.items import HandoffCallItem, HandoffOutputItem, ItemHelpers, MessageOutputItem, ReasoningItem, ToolCallItem, ToolCallOutputItem
from agents.result import RunResult

def print_result(result: RunResult):
    """Prints the result of a run and returns the input list for the next run."""
    print_items(result.new_items)
    return result.to_input_list()

def print_items(items: list[RunItem]):
    for item in items:
        if isinstance(item, MessageOutputItem):
            print(f'{"Agent":=^40}\n{ItemHelpers.text_message_output(item)}\n{"="*40}')
        if isinstance(item, ToolCallItem):
            print(f'{"Tool Call":=^40}\n{item.raw_item}\n{"="*40}')
        if isinstance(item, ToolCallOutputItem):
            print(f'{"Tool Output":=^40}\n{item.output}\n{"="*40}')
        if isinstance(item, HandoffCallItem):
            print(f'{"Handoff Call":=^40}\n{item.raw_item}\n{"="*40}')
        if isinstance(item, HandoffOutputItem):
            print(f'{"Handoff Output":=^40}\n{item.source_agent} -> {item.target_agent}\n{"="*40}')
        if isinstance(item, ReasoningItem):
            print(f'{"Reasoning":=^40}\n{item.raw_item}\n{"="*40}')



