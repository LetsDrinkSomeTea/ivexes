import asyncio

from config.settings import settings
import config.log
logger = config.log.get(__name__)

from modules.sandbox.tools import sandbox_tools
from modules.vector_db.tools import cwe_capec_tools
from modules.code_browser.tools import code_browser_tools

from modules.code_browser.tools import code_browser
from modules.sandbox.tools import sandbox

from agents import Agent, Runner, ModelSettings

tools = sandbox_tools + cwe_capec_tools + code_browser_tools

system_msg = \
"""
You are an expert at analyzing codebases and finding vulnerabilities.
You are also an expert at generating proof of concept (PoC) exploits for the vulnerabilities you find.

You are given a diff of a codebase. The diff shows the changes made to the codebase.
Your task is to analyze the diff and find the vulnerability and create a PoC exploit for it.

Do not halucinate or make up any information.
Query the tools you need to find the information you need.

Dont stop until you a working PoC exploit and verified it in the sandbox.
"""

model_settings = ModelSettings(
    temperature=0.3,
)

agent = Agent(
    name="Binary Exploiter",
    instructions=system_msg,
    model=settings.model,
    model_settings=model_settings,
    tools=tools
)


async def main(user_msg: str):
    result = await Runner.run(agent, user_msg)
    print(result.final_output)

if __name__ == "__main__":
    user_msg = \
f"""
Start by querying the diff and finding the vulnerability.
"""

    asyncio.run(main(user_msg))

    # Cleanup
    logger.info("Cleaning up...")
    code_browser.container.stop()
    code_browser.container.remove()
    logger.info("Code browser container stopped and removed.")
    sandbox.container.stop()
    sandbox.container.remove()
    logger.info("Sandbox container stopped and removed.")

