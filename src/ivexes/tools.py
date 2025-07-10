from datetime import datetime

from agents.tool import function_tool

from .modules.code_browser.tools import code_browser_tools
from .modules.sandbox.tools import sandbox_tools
from .modules.vector_db.tools import vectordb_tools


@function_tool(strict_mode=True)
def get_current_date():
    """Use this tool to get the current date and time"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


date_tools = [get_current_date]

__all__ = ['code_browser_tools', 'sandbox_tools', 'vectordb_tools', 'date_tools']
