"""Agent classes for IVEXES system.

This module provides agent classes that encapsulate the complexity of different
agent types including HTB challenges, MVP, single agent, and multi-agent workflows.
"""

from .base import BaseAgent
from .default_agent import DefaultAgent as DefaultAgent
from .htb_challenge import HTBChallengeAgent
from .mvp import MVPAgent
from .single_agent import SingleAgent
from .multi_agent import (
    MultiAgent,
    MultiAgentContext,
    agent_as_tool,
    create_shared_memory_tools,
)

__all__ = [
    'BaseAgent',
    'DefaultAgent',
    'HTBChallengeAgent',
    'MVPAgent',
    'SingleAgent',
    'MultiAgent',
    'MultiAgentContext',
    'agent_as_tool',
    'create_shared_memory_tools',
]
