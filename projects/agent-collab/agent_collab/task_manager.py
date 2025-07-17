"""Task Manager - Handles task assignment, dependency resolution, and execution tracking"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import aiohttp
import logging


class TaskManager:
    """Handles task assignment, dependency resolution, and execution tracking"""
    
    def __init__(self, composer_agent):
        self.composer_agent = composer_agent
        self.tasks = []
        self.task_status = {}
        self.logger = logging.getLogger(__name__)
    
    async def load_tasks_from_file(self) -> List[Dict[str, Any]]:
        """Load tasks from the task list file"""
        tasks_file = self.composer_agent.docs_dir / "tasks.md"
        
        if not tasks_file.exists():
            self.logger.error("Tasks file not found")
            return []
        
        with open(tasks_file, 'r') as f:
            content = f.read()
        
        self.tasks = self.parse_tasks_markdown(content)
        self.logger.info(f"Loaded {len(self.tasks)} tasks from file")
        
        return self.tasks
    
    def parse_tasks_markdown(self, content: str) -> List[Dict[str, Any]]:
        """Parse tasks from markdown content"""
        tasks = []
        
        # Find all task lines (lines starting with - [ ])
        task_pattern = r'- \[ \] \*\*([^*]+)\*\* - ([^(]+)\(([^)]+)\)'
        
        for match in re.finditer(task_pattern, content):
            task_title = match.group(1).strip()
            task_description = match.group(2).strip()
            task_metadata = match.group(3).strip()
            
            # Parse metadata
            priority = 5  # default priority
            agent = "developer"  # default agent
            dependencies = []
            
            # Extract priority
            priority_match = re.search(r'Priority:\s*(\d+)', task_metadata)
            if priority_match:
                priority = int(priority_match.group(1))
            
            # Extract agent
            agent_match = re.search(r'Agent:\s*(\w+)', task_metadata)
            if agent_match:
                agent = agent_match.group(1)
            
            # Extract dependencies
            deps_match = re.search(r'Dependencies:\s*([^,)]+)', task_metadata)
            if deps_match:
                deps_str = deps_match.group(1).strip()
                if deps_str and deps_str != "none":
                    dependencies = [dep.strip() for dep in deps_str.split(',')]
            
            task = {
                "id": f"task_{len(tasks) + 1}",
                "title": task_title,
                "description": task_description,
                "agent": agent,
                "priority": priority,
                "dependencies": dependencies,
                "status": "not_started",
                "result": None
            }
            
            tasks.append(task)
        
        return tasks
    
    async def assign_tasks(self) -> None:
        """Assign tasks to appropriate agents based on dependencies"""
        if not self.tasks:
            self.logger.warning("No tasks to assign")
            return
        
        # Sort tasks by dependencies and priority
        sorted_tasks = self.sort_tasks_by_dependencies()
        
        # Initialize task status tracking
        for task in sorted_tasks:
            self.task_status[task["id"]] = {
                "status": "not_started",
                "assigned_agent": task["agent"],
                "start_time": None,
                "completion_time": None
            }
        
        # Assign tasks in dependency order
        for task in sorted_tasks:
            if self.can_assign_task(task):
                await self.send_task_to_agent(task["agent"], task)
                self.task_status[task["id"]]["status"] = "assigned"
                self.logger.info(f"Assigned task '{task['title']}' to agent '{task['agent']}'")
            else:
                self.logger.info(f"Task '{task['title']}' waiting for dependencies")
    
    def sort_tasks_by_dependencies(self) -> List[Dict[str, Any]]:
        """Sort tasks by dependencies using topological sort"""
        # Create a mapping of task titles to tasks
        task_map = {task["title"]: task for task in self.tasks}
        
        # Build dependency graph
        in_degree = {}
        graph = {}
        
        for task in self.tasks:
            task_title = task["title"]
            in_degree[task_title] = 0
            graph[task_title] = []
        
        for task in self.tasks:
            task_title = task["title"]
            for dep in task["dependencies"]:
                if dep in task_map:
                    graph[dep].append(task_title)
                    in_degree[task_title] += 1
        
        # Topological sort
        queue = []
        for task_title in in_degree:
            if in_degree[task_title] == 0:
                queue.append(task_title)
        
        sorted_tasks = []
        while queue:
            # Sort by priority within the same dependency level
            queue.sort(key=lambda x: task_map[x]["priority"])
            
            current = queue.pop(0)
            sorted_tasks.append(task_map[current])
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return sorted_tasks
    
    def can_assign_task(self, task: Dict[str, Any]) -> bool:
        """Check if a task can be assigned (all dependencies completed)"""
        for dep in task["dependencies"]:
            # Find dependency task
            dep_task = next((t for t in self.tasks if t["title"] == dep), None)
            if not dep_task:
                continue
            
            dep_status = self.task_status.get(dep_task["id"], {}).get("status", "not_started")
            if dep_status != "completed":
                return False
        
        return True
    
    async def send_task_to_agent(self, agent_name: str, task: Dict[str, Any]) -> None:
        """Send a task to a specific agent"""
        try:
            # Get agent port from composer
            agent_info = self.composer_agent.agents.get(agent_name)
            if not agent_info:
                self.logger.error(f"Agent {agent_name} not found")
                return
            
            port = agent_info["port"]
            
            # Prepare task data
            task_data = {
                "id": task["id"],
                "title": task["title"],
                "description": task["description"],
                "type": task.get("type", "generic"),
                "priority": task["priority"]
            }
            
            # Send task to agent
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://localhost:{port}/task",
                    json=task_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info(f"Task sent successfully to {agent_name}")
                        
                        # Update task status
                        self.task_status[task["id"]]["status"] = "in_progress"
                        
                        # If task completed immediately, update status
                        if result.get("status") == "completed":
                            self.task_status[task["id"]]["status"] = "completed"
                            task["result"] = result.get("result", "")
                            
                            # Check if any waiting tasks can now be assigned
                            await self.check_and_assign_waiting_tasks()
                    else:
                        self.logger.error(f"Failed to send task to {agent_name}: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error sending task to {agent_name}: {str(e)}")
    
    async def check_and_assign_waiting_tasks(self) -> None:
        """Check for tasks that can now be assigned after dependencies are met"""
        for task in self.tasks:
            task_status = self.task_status.get(task["id"], {})
            if task_status.get("status") == "not_started" and self.can_assign_task(task):
                await self.send_task_to_agent(task["agent"], task)
                self.task_status[task["id"]]["status"] = "assigned"
                self.logger.info(f"Assigned waiting task '{task['title']}' to agent '{task['agent']}'")
    
    def all_tasks_completed(self) -> bool:
        """Check if all tasks have been completed"""
        for task_id, status in self.task_status.items():
            if status.get("status") != "completed":
                return False
        return True
    
    async def get_task_status_summary(self) -> Dict[str, Any]:
        """Get a summary of task execution status"""
        summary = {
            "total_tasks": len(self.tasks),
            "completed": 0,
            "in_progress": 0,
            "not_started": 0,
            "failed": 0,
            "tasks": []
        }
        
        for task in self.tasks:
            task_status = self.task_status.get(task["id"], {})
            status = task_status.get("status", "not_started")
            
            if status == "completed":
                summary["completed"] += 1
            elif status == "in_progress":
                summary["in_progress"] += 1
            elif status == "not_started":
                summary["not_started"] += 1
            elif status == "failed":
                summary["failed"] += 1
            
            summary["tasks"].append({
                "id": task["id"],
                "title": task["title"],
                "agent": task["agent"],
                "status": status,
                "result": task.get("result", "")
            })
        
        return summary
    
    async def wait_for_all_tasks_completion(self, timeout: int = 3600) -> bool:
        """Wait for all tasks to complete with timeout"""
        start_time = asyncio.get_event_loop().time()
        
        while not self.all_tasks_completed():
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > timeout:
                self.logger.error("Task execution timed out")
                return False
            
            await asyncio.sleep(2)
            
            # Update task status by checking with agents
            await self.update_task_status()
        
        return True
    
    async def update_task_status(self) -> None:
        """Update task status by checking with agents"""
        for task in self.tasks:
            task_status = self.task_status.get(task["id"], {})
            if task_status.get("status") == "in_progress":
                agent_name = task["agent"]
                agent_info = self.composer_agent.agents.get(agent_name)
                
                if agent_info:
                    try:
                        port = agent_info["port"]
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f"http://localhost:{port}/status") as response:
                                if response.status == 200:
                                    status_data = await response.json()
                                    current_task = status_data.get("current_task")
                                    
                                    # If agent is idle, task might be completed
                                    if not current_task or status_data.get("status") == "idle":
                                        # Check for results
                                        async with session.get(f"http://localhost:{port}/results") as result_response:
                                            if result_response.status == 200:
                                                result_data = await result_response.json()
                                                results = result_data.get("results", [])
                                                
                                                # Find our task result
                                                for result in results:
                                                    if result.get("task", {}).get("id") == task["id"]:
                                                        self.task_status[task["id"]]["status"] = "completed"
                                                        task["result"] = result.get("result", "")
                                                        self.logger.info(f"Task '{task['title']}' completed")
                                                        break
                    except Exception as e:
                        self.logger.warning(f"Failed to update status for task {task['id']}: {e}")