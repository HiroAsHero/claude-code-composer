"""Utility functions for the Agent Collaboration Framework"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import json
import yaml
from datetime import datetime


class RetryHandler:
    """Handles retry logic with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    async def retry_async(self, func: Callable, *args, **kwargs) -> Any:
        """Retry an async function with exponential backoff"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    await asyncio.sleep(delay)
        
        raise last_exception


class FileManager:
    """Manages file operations for the framework"""
    
    @staticmethod
    def ensure_directory(path: Path) -> None:
        """Ensure a directory exists"""
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def read_file(path: Path) -> str:
        """Read content from a file"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def write_file(path: Path, content: str) -> None:
        """Write content to a file"""
        FileManager.ensure_directory(path.parent)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def read_json(path: Path) -> Dict[str, Any]:
        """Read JSON from a file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_json(path: Path, data: Dict[str, Any]) -> None:
        """Write JSON to a file"""
        FileManager.ensure_directory(path.parent)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def read_yaml(path: Path) -> Dict[str, Any]:
        """Read YAML from a file"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def write_yaml(path: Path, data: Dict[str, Any]) -> None:
        """Write YAML to a file"""
        FileManager.ensure_directory(path.parent)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


class Logger:
    """Enhanced logging utilities"""
    
    @staticmethod
    def setup_logger(name: str, level: str = "INFO", log_file: Optional[Path] = None) -> logging.Logger:
        """Setup a logger with the given configuration"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            FileManager.ensure_directory(log_file.parent)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger


class Timer:
    """Timer utility for measuring execution time"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def start(self) -> None:
        """Start the timer"""
        self.start_time = time.time()
    
    def stop(self) -> float:
        """Stop the timer and return elapsed time"""
        if self.start_time is None:
            raise ValueError("Timer not started")
        
        self.end_time = time.time()
        return self.elapsed_time
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time"""
        if self.start_time is None:
            return 0.0
        
        end_time = self.end_time or time.time()
        return end_time - self.start_time
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class ProgressTracker:
    """Track progress of operations"""
    
    def __init__(self, total_items: int, name: str = "Progress"):
        self.total_items = total_items
        self.name = name
        self.completed_items = 0
        self.start_time = time.time()
    
    def update(self, items: int = 1) -> None:
        """Update progress"""
        self.completed_items += items
    
    @property
    def progress_percentage(self) -> float:
        """Get progress percentage"""
        if self.total_items == 0:
            return 100.0
        return (self.completed_items / self.total_items) * 100
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time"""
        return time.time() - self.start_time
    
    @property
    def estimated_time_remaining(self) -> float:
        """Estimate time remaining"""
        if self.completed_items == 0:
            return 0.0
        
        time_per_item = self.elapsed_time / self.completed_items
        remaining_items = self.total_items - self.completed_items
        return time_per_item * remaining_items
    
    def __str__(self) -> str:
        return f"{self.name}: {self.completed_items}/{self.total_items} ({self.progress_percentage:.1f}%)"


class ValidationUtils:
    """Utility functions for validation"""
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number"""
        return 1024 <= port <= 65535
    
    @staticmethod
    def validate_agent_name(name: str) -> bool:
        """Validate agent name"""
        return bool(name and name.isalnum())
    
    @staticmethod
    def validate_workspace(workspace: str) -> bool:
        """Validate workspace path"""
        try:
            path = Path(workspace)
            return path.is_absolute() or path.is_dir()
        except:
            return False
    
    @staticmethod
    def validate_config_structure(config: Dict[str, Any]) -> List[str]:
        """Validate configuration structure and return list of errors"""
        errors = []
        
        # Check required sections
        required_sections = ["agents", "task_types", "system"]
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate agents section
        if "agents" in config:
            if not isinstance(config["agents"], dict):
                errors.append("'agents' section must be a dictionary")
            else:
                for agent_name, agent_config in config["agents"].items():
                    if not isinstance(agent_config, dict):
                        errors.append(f"Agent '{agent_name}' config must be a dictionary")
                        continue
                    
                    # Check required fields
                    required_fields = ["role", "port"]
                    for field in required_fields:
                        if field not in agent_config:
                            errors.append(f"Agent '{agent_name}' missing required field: {field}")
                    
                    # Validate port
                    if "port" in agent_config:
                        if not ValidationUtils.validate_port(agent_config["port"]):
                            errors.append(f"Agent '{agent_name}' has invalid port: {agent_config['port']}")
        
        return errors


class TaskUtils:
    """Utility functions for task operations"""
    
    @staticmethod
    def generate_task_id() -> str:
        """Generate a unique task ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"task_{timestamp}_{int(time.time() * 1000) % 10000}"
    
    @staticmethod
    def normalize_task_title(title: str) -> str:
        """Normalize task title for consistency"""
        return title.strip().lower().replace(' ', '_')
    
    @staticmethod
    def parse_dependencies(dep_string: str) -> List[str]:
        """Parse dependencies from a string"""
        if not dep_string or dep_string.strip().lower() in ['none', 'null', '']:
            return []
        
        deps = [dep.strip() for dep in dep_string.split(',')]
        return [dep for dep in deps if dep]
    
    @staticmethod
    def format_task_summary(task: Dict[str, Any]) -> str:
        """Format task summary for display"""
        status_emoji = {
            'not_started': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'failed': '❌'
        }
        
        status = task.get('status', 'unknown')
        emoji = status_emoji.get(status, '❓')
        
        return f"{emoji} {task.get('title', 'Unknown')} ({task.get('agent', 'Unknown')})"


class NetworkUtils:
    """Utility functions for network operations"""
    
    @staticmethod
    def is_port_available(port: int, host: str = 'localhost') -> bool:
        """Check if a port is available"""
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0
        except:
            return False
    
    @staticmethod
    def find_available_port(start_port: int = 8000, max_port: int = 9000) -> Optional[int]:
        """Find an available port in the given range"""
        for port in range(start_port, max_port + 1):
            if NetworkUtils.is_port_available(port):
                return port
        return None