"""Custom exceptions for the Agent Collaboration Framework"""


class AgentCollabException(Exception):
    """Base exception for all agent collaboration errors"""
    pass


class ConfigurationError(AgentCollabException):
    """Raised when there's an issue with configuration"""
    pass


class AgentError(AgentCollabException):
    """Raised when there's an issue with agent operations"""
    pass


class TaskError(AgentCollabException):
    """Raised when there's an issue with task operations"""
    pass


class CommunicationError(AgentCollabException):
    """Raised when there's an issue with agent communication"""
    pass


class TimeoutError(AgentCollabException):
    """Raised when operations timeout"""
    pass


class DependencyError(TaskError):
    """Raised when task dependencies cannot be resolved"""
    pass


class AgentNotFoundError(AgentError):
    """Raised when a requested agent is not found"""
    pass


class TaskNotFoundError(TaskError):
    """Raised when a requested task is not found"""
    pass


class AgentStartupError(AgentError):
    """Raised when an agent fails to start"""
    pass


class TaskExecutionError(TaskError):
    """Raised when task execution fails"""
    pass