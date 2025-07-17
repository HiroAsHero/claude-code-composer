"""Configuration management for the agent collaboration framework"""

import yaml
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentConfig:
    role: str
    max_parallel_tasks: int = 3
    timeout: int = 300
    retry_count: int = 2
    port: int = 8000


@dataclass
class TaskTypeConfig:
    agent: str
    priority: int = 5
    dependencies: list = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class ConfigManager:
    """Manages configuration for the agent collaboration framework"""
    
    DEFAULT_CONFIG = {
        "agents": {
            "developer": {
                "role": "code_implementation",
                "max_parallel_tasks": 3,
                "timeout": 300,
                "retry_count": 2,
                "port": 8001
            },
            "qa": {
                "role": "quality_assurance",
                "max_parallel_tasks": 2,
                "timeout": 180,
                "retry_count": 1,
                "port": 8002
            },
            "designer": {
                "role": "ui_ux_design",
                "max_parallel_tasks": 2,
                "timeout": 240,
                "retry_count": 1,
                "port": 8003
            },
            "architect": {
                "role": "system_architecture",
                "max_parallel_tasks": 1,
                "timeout": 400,
                "retry_count": 2,
                "port": 8004
            }
        },
        "task_types": {
            "requirements_analysis": {
                "agent": "architect",
                "priority": 1,
                "dependencies": []
            },
            "architecture_design": {
                "agent": "architect",
                "priority": 2,
                "dependencies": ["requirements_analysis"]
            },
            "ui_design": {
                "agent": "designer",
                "priority": 3,
                "dependencies": ["requirements_analysis"]
            },
            "code_implementation": {
                "agent": "developer",
                "priority": 4,
                "dependencies": ["architecture_design"]
            },
            "unit_testing": {
                "agent": "qa",
                "priority": 5,
                "dependencies": ["code_implementation"]
            },
            "integration_testing": {
                "agent": "qa",
                "priority": 6,
                "dependencies": ["unit_testing"]
            }
        },
        "system": {
            "workspace": "./workspace",
            "log_level": "INFO",
            "timeout": 3600,
            "composer_port": 8000
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                custom_config = yaml.safe_load(f)
            return self.merge_config(self.DEFAULT_CONFIG, custom_config)
        return self.DEFAULT_CONFIG.copy()
    
    def merge_config(self, base: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """Merge custom configuration with base configuration"""
        result = base.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """Get configuration for a specific agent"""
        agent_config = self.config["agents"].get(agent_name, {})
        return AgentConfig(**agent_config)
    
    def get_task_type_config(self, task_type: str) -> TaskTypeConfig:
        """Get configuration for a specific task type"""
        task_config = self.config["task_types"].get(task_type, {})
        return TaskTypeConfig(**task_config)
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return self.config.get("system", {})
    
    def save_config(self, path: str = None):
        """Save current configuration to file"""
        save_path = path or self.config_path or "config.yaml"
        with open(save_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def validate_config(self) -> bool:
        """Validate configuration structure"""
        required_sections = ["agents", "task_types", "system"]
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
        
        # Validate agent configurations
        for agent_name, agent_config in self.config["agents"].items():
            required_fields = ["role", "port"]
            for field in required_fields:
                if field not in agent_config:
                    raise ValueError(f"Missing required field '{field}' in agent '{agent_name}'")
        
        return True