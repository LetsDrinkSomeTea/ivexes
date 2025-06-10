import re
from time import sleep
from typing import cast

from config.settings import settings
import config.log
from modules.printer.printer import print_result
logger = config.log.get(__name__)
from config.run import get_config

from modules.sandbox.tools import sandbox_tools
from modules.vector_db.tools import cwe_capec_tools
from modules.code_browser.tools import code_browser_tools


from openai import RateLimitError
from agents import Agent, Runner, TResponseInputItem, Tool, trace, MaxTurnsExceeded

tools: list[Tool] = cast(list[Tool], sandbox_tools + cwe_capec_tools + code_browser_tools)

system_msg = \
"""
You are an expert at analyzing codebases and finding vulnerabilities.
You are also an expert at generating proof of concept (PoC) exploits for the vulnerabilities you find.

You are given a diff of a codebase. The diff shows the changes made to the codebase.
Your task is to analyze the diff and find the vulnerability and create a PoC exploit for it.

Do not halucinate or make up any information.
Query the tools you need to find the information you need.

You have access to the following tools:
- `sandbox`: A Kali Linux sandbox environment where you can run commands and test your exploits. The vulnerable version is installed in the sandbox.
- `code_browser`: A tool to browse the codebase and find the relevant files and functions.
- `cwe_capec`: A tool to query the CWE and CAPEC databases for vulnerabilities and exploits.
The tools are different containerized environments.

Dont stop until you a working PoC exploit and verified it in the sandbox.
Always create a file in the sandbox with the PoC exploit, preferably in bash or python.
The vulnerable version is installed in the sandbox.
"""

agent = Agent(
    name="Exploiter",
    instructions=system_msg,
    model=settings.model,
    tools=tools,

)


def main(user_msg: str):
    input_items: list[TResponseInputItem] = []
    workflow_name = f'Ivexes ({settings.trace_name} Single Agent({settings.model}))'
    with trace(workflow_name):
        while True:
            input_items.append({'content': user_msg, 'role': 'user'})
            try:
                result = Runner.run_sync(agent, input_items, max_turns=settings.max_turns, run_config=get_config())
                input_items = print_result(result)
                user_msg = input("User: ")
                if user_msg in ['q', 'quit', 'exit']:
                    exit(0)
            except RateLimitError as e:
                logger.warning(f"Got RateLimitError")
                m = re.search(r'(\d+(?:\.\d+)?)', e.message)
                if m:
                    try_again_in = int(m.group(1))
                    logger.info(f"Sleeping {try_again_in + 1} seconds to avoid rate limit")
                    sleep(try_again_in + 1)
            except MaxTurnsExceeded as e:
                logger.error(f"Max turns exceeded: {e}")
                print("Max turns exceeded, exiting.")
                break
            except Exception as e:
                logger.error(f"Got Exception of type {type(e)=}:\n{e}")
                logger.debug(f"{agent=}\n")


if __name__ == "__main__":
    from modules.code_browser.tools import code_browser
    user_msg = \
f"""
{code_browser.get_diff()}
"""
    main(user_msg)
