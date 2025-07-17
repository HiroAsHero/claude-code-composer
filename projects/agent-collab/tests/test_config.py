"""Tests for configuration management"""

import pytest
import tempfile
import yaml
from pathlib import Path

from agent_collab.config import ConfigManager, AgentConfig, TaskTypeConfig
from agent_collab.exceptions import ConfigurationError


class TestConfigManager:
    """Test ConfigManager class"""
    
    def test_default_config_loading(self):
        """Test loading default configuration"""
        config_manager = ConfigManager()
        assert "agents" in config_manager.config
        assert "task_types" in config_manager.config
        assert "system" in config_manager.config
    
    def test_custom_config_loading(self):
        """Test loading custom configuration"""
        custom_config = {
            "agents": {
                "test_agent": {
                    "role": "test_role",
                    "port": 9000
                }
            },
            "task_types": {
                "test_task": {
                    "agent": "test_agent",
                    "priority": 1
                }
            },
            "system": {
                "workspace": "./test_workspace"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(custom_config, f)
            config_path = f.name
        
        try:
            config_manager = ConfigManager(config_path)
            assert "test_agent" in config_manager.config["agents"]
            assert config_manager.config["agents"]["test_agent"]["role"] == "test_role"
            assert config_manager.config["system"]["workspace"] == "./test_workspace"
        finally:
            Path(config_path).unlink()
    
    def test_config_merging(self):
        """Test merging of default and custom configurations"""
        config_manager = ConfigManager()
        
        base_config = {"a": {"b": 1, "c": 2}, "d": 3}
        custom_config = {"a": {"b": 10, "e": 4}, "f": 5}
        
        merged = config_manager.merge_config(base_config, custom_config)
        
        assert merged["a"]["b"] == 10  # Override
        assert merged["a"]["c"] == 2   # Keep original
        assert merged["a"]["e"] == 4   # Add new
        assert merged["d"] == 3        # Keep original
        assert merged["f"] == 5        # Add new
    
    def test_get_agent_config(self):
        """Test getting agent configuration"""
        config_manager = ConfigManager()
        
        agent_config = config_manager.get_agent_config("developer")
        assert isinstance(agent_config, AgentConfig)
        assert agent_config.role == "code_implementation"
        assert agent_config.port == 8001
    
    def test_get_task_type_config(self):
        """Test getting task type configuration"""
        config_manager = ConfigManager()
        
        task_config = config_manager.get_task_type_config("requirements_analysis")
        assert isinstance(task_config, TaskTypeConfig)
        assert task_config.agent == "architect"
        assert task_config.priority == 1
    
    def test_config_validation_success(self):
        """Test successful configuration validation"""
        config_manager = ConfigManager()
        assert config_manager.validate_config() == True
    
    def test_config_validation_failure(self):
        """Test configuration validation failure"""
        invalid_config = {
            "agents": {
                "test_agent": {
                    "role": "test_role"
                    # Missing required 'port' field
                }
            },
            "task_types": {},
            "system": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            config_path = f.name
        
        try:
            config_manager = ConfigManager(config_path)
            with pytest.raises(ValueError, match="Missing required field 'port'"):
                config_manager.validate_config()
        finally:
            Path(config_path).unlink()
    
    def test_save_config(self):
        """Test saving configuration to file"""
        config_manager = ConfigManager()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            config_manager.save_config(config_path)
            
            # Load and verify
            new_config_manager = ConfigManager(config_path)
            assert new_config_manager.config == config_manager.config
        finally:
            Path(config_path).unlink()


class TestAgentConfig:
    """Test AgentConfig class"""
    
    def test_agent_config_creation(self):
        """Test creating agent configuration"""
        config = AgentConfig(
            role="test_role",
            max_parallel_tasks=5,
            timeout=600,
            retry_count=3,
            port=9000
        )
        
        assert config.role == "test_role"
        assert config.max_parallel_tasks == 5
        assert config.timeout == 600
        assert config.retry_count == 3
        assert config.port == 9000
    
    def test_agent_config_defaults(self):
        """Test agent configuration defaults"""
        config = AgentConfig(role="test_role", port=9000)
        
        assert config.role == "test_role"
        assert config.port == 9000
        assert config.max_parallel_tasks == 3
        assert config.timeout == 300
        assert config.retry_count == 2


class TestTaskTypeConfig:
    """Test TaskTypeConfig class"""
    
    def test_task_type_config_creation(self):
        """Test creating task type configuration"""
        config = TaskTypeConfig(
            agent="test_agent",
            priority=1,
            dependencies=["dep1", "dep2"]
        )
        
        assert config.agent == "test_agent"
        assert config.priority == 1
        assert config.dependencies == ["dep1", "dep2"]
    
    def test_task_type_config_defaults(self):
        """Test task type configuration defaults"""
        config = TaskTypeConfig(agent="test_agent")
        
        assert config.agent == "test_agent"
        assert config.priority == 5
        assert config.dependencies == []
    
    def test_task_type_config_post_init(self):
        """Test task type configuration post-initialization"""
        config = TaskTypeConfig(agent="test_agent", dependencies=None)
        
        assert config.dependencies == []