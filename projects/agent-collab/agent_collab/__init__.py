"""Agent Collaboration Framework for Claude Code"""

__version__ = "0.1.0"
__author__ = "Agent Collaboration Team"

from .composer_agent import ComposerAgent
from .sub_agent import SubAgent
from .task_manager import TaskManager

__all__ = ["ComposerAgent", "SubAgent", "TaskManager"]