"""Tests for task manager"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from agent_collab.task_manager import TaskManager
from agent_collab.composer_agent import ComposerAgent


class TestTaskManager:
    """Test TaskManager class"""
    
    @pytest.fixture
    def mock_composer(self):
        """Create a mock composer agent"""
        composer = Mock(spec=ComposerAgent)
        composer.docs_dir = Mock()
        composer.agents = {
            "developer": {"port": 8001},
            "qa": {"port": 8002},
            "architect": {"port": 8003}
        }
        return composer
    
    @pytest.fixture
    def task_manager(self, mock_composer):
        """Create a task manager instance"""
        return TaskManager(mock_composer)
    
    def test_parse_tasks_markdown(self, task_manager):
        """Test parsing tasks from markdown"""
        markdown_content = """
        # Task List
        
        ## Development Tasks
        - [ ] **setup_project** - Setup project structure (Priority: 1, Agent: developer)
        - [ ] **implement_api** - Implement REST API (Priority: 2, Agent: developer, Dependencies: setup_project)
        - [ ] **create_tests** - Create unit tests (Priority: 3, Agent: qa, Dependencies: implement_api)
        """
        
        tasks = task_manager.parse_tasks_markdown(markdown_content)
        
        assert len(tasks) == 3
        
        # Check first task
        assert tasks[0]["title"] == "setup_project"
        assert tasks[0]["description"] == "Setup project structure"
        assert tasks[0]["agent"] == "developer"
        assert tasks[0]["priority"] == 1
        assert tasks[0]["dependencies"] == []
        
        # Check second task
        assert tasks[1]["title"] == "implement_api"
        assert tasks[1]["description"] == "Implement REST API"
        assert tasks[1]["agent"] == "developer"
        assert tasks[1]["priority"] == 2
        assert tasks[1]["dependencies"] == ["setup_project"]
        
        # Check third task
        assert tasks[2]["title"] == "create_tests"
        assert tasks[2]["description"] == "Create unit tests"
        assert tasks[2]["agent"] == "qa"
        assert tasks[2]["priority"] == 3
        assert tasks[2]["dependencies"] == ["implement_api"]
    
    def test_sort_tasks_by_dependencies(self, task_manager):
        """Test sorting tasks by dependencies"""
        tasks = [
            {
                "title": "task_c",
                "dependencies": ["task_a", "task_b"],
                "priority": 1
            },
            {
                "title": "task_a",
                "dependencies": [],
                "priority": 2
            },
            {
                "title": "task_b",
                "dependencies": ["task_a"],
                "priority": 1
            }
        ]
        
        task_manager.tasks = tasks
        sorted_tasks = task_manager.sort_tasks_by_dependencies()
        
        # Should be sorted by dependencies first, then by priority
        task_titles = [task["title"] for task in sorted_tasks]
        assert task_titles == ["task_a", "task_b", "task_c"]
    
    def test_can_assign_task(self, task_manager):
        """Test checking if task can be assigned"""
        task_manager.tasks = [
            {"id": "task_1", "title": "task_a", "dependencies": []},
            {"id": "task_2", "title": "task_b", "dependencies": ["task_a"]},
            {"id": "task_3", "title": "task_c", "dependencies": ["task_a", "task_b"]}
        ]
        
        task_manager.task_status = {
            "task_1": {"status": "completed"},
            "task_2": {"status": "in_progress"},
            "task_3": {"status": "not_started"}
        }
        
        # Task with no dependencies should be assignable
        task_no_deps = {"dependencies": []}
        assert task_manager.can_assign_task(task_no_deps) == True
        
        # Task with completed dependencies should be assignable
        task_completed_deps = {"dependencies": ["task_a"]}
        assert task_manager.can_assign_task(task_completed_deps) == True
        
        # Task with incomplete dependencies should not be assignable
        task_incomplete_deps = {"dependencies": ["task_a", "task_b"]}
        assert task_manager.can_assign_task(task_incomplete_deps) == False
    
    def test_all_tasks_completed(self, task_manager):
        """Test checking if all tasks are completed"""
        task_manager.task_status = {
            "task_1": {"status": "completed"},
            "task_2": {"status": "completed"},
            "task_3": {"status": "completed"}
        }
        
        assert task_manager.all_tasks_completed() == True
        
        task_manager.task_status["task_2"]["status"] = "in_progress"
        assert task_manager.all_tasks_completed() == False
    
    @pytest.mark.asyncio
    async def test_get_task_status_summary(self, task_manager):
        """Test getting task status summary"""
        task_manager.tasks = [
            {"id": "task_1", "title": "Task 1", "agent": "developer", "result": "Done"},
            {"id": "task_2", "title": "Task 2", "agent": "qa", "result": ""},
            {"id": "task_3", "title": "Task 3", "agent": "architect", "result": ""}
        ]
        
        task_manager.task_status = {
            "task_1": {"status": "completed"},
            "task_2": {"status": "in_progress"},
            "task_3": {"status": "not_started"}
        }
        
        summary = await task_manager.get_task_status_summary()
        
        assert summary["total_tasks"] == 3
        assert summary["completed"] == 1
        assert summary["in_progress"] == 1
        assert summary["not_started"] == 1
        assert summary["failed"] == 0
        assert len(summary["tasks"]) == 3
    
    @pytest.mark.asyncio
    async def test_load_tasks_from_file(self, task_manager):
        """Test loading tasks from file"""
        mock_file_content = """
        - [ ] **test_task** - Test description (Priority: 1, Agent: developer)
        """
        
        # Mock file operations
        task_manager.composer_agent.docs_dir = Mock()
        mock_file = Mock()
        mock_file.exists.return_value = True
        task_manager.composer_agent.docs_dir.__truediv__.return_value = mock_file
        
        with patch("builtins.open", mock_open_read_data=mock_file_content):
            tasks = await task_manager.load_tasks_from_file()
        
        assert len(tasks) == 1
        assert tasks[0]["title"] == "test_task"
        assert tasks[0]["agent"] == "developer"
    
    @pytest.mark.asyncio
    async def test_send_task_to_agent(self, task_manager):
        """Test sending task to agent"""
        task = {
            "id": "test_task_1",
            "title": "Test Task",
            "description": "Test description",
            "agent": "developer",
            "priority": 1
        }
        
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"status": "completed", "result": "Task completed"}
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            await task_manager.send_task_to_agent("developer", task)
            
            # Verify task status was updated
            assert task_manager.task_status["test_task_1"]["status"] == "completed"
            assert task["result"] == "Task completed"


def mock_open_read_data(data):
    """Helper function to mock file reading"""
    from unittest.mock import mock_open
    return mock_open(read_data=data)