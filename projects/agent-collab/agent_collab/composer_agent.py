"""Composer Agent - Central orchestrator for multi-agent collaboration"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiohttp
import logging
from datetime import datetime

from .config import ConfigManager, AgentConfig
from .task_manager import TaskManager


class ComposerAgent:
    """Central orchestrator responsible for managing the multi-agent collaboration"""
    
    def __init__(self, workspace: str, config_path: str = None, verbose: bool = False, no_confirm: bool = False):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.config_manager = ConfigManager(config_path)
        self.verbose = verbose
        self.no_confirm = no_confirm
        self.agents = {}
        self.agent_processes = {}
        self.task_manager = TaskManager(self)
        
        # Setup logging
        self.setup_logging()
        
        # Create workspace subdirectories
        self.docs_dir = self.workspace / "docs"
        self.docs_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"ComposerAgent initialized with workspace: {self.workspace}")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config_manager.get_system_config().get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def orchestrate(self, user_request: str) -> str:
        """Main orchestration method"""
        try:
            self.logger.info("Starting orchestration process")
            
            # Step 1: Generate project documentation
            await self.generate_requirements_docs(user_request)
            
            # Step 2: Get user confirmation
            if not self.no_confirm:
                if not await self.get_user_confirmation():
                    return "Process cancelled by user"
            
            # Step 3: Spawn sub-agents
            await self.spawn_sub_agents()
            
            # Step 4: Assign and monitor tasks
            result = await self.assign_and_monitor_tasks()
            
            # Step 5: Cleanup
            await self.cleanup_agents()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {str(e)}")
            await self.cleanup_agents()
            raise
    
    async def generate_requirements_docs(self, user_request: str) -> None:
        """Generate project documentation based on user request"""
        self.logger.info("Generating project documentation")
        
        # Generate requirements document
        requirements_content = await self.generate_requirements(user_request)
        requirements_path = self.docs_dir / "requirements.md"
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
        
        # Generate design document
        design_content = await self.generate_design(user_request)
        design_path = self.docs_dir / "design.md"
        with open(design_path, 'w') as f:
            f.write(design_content)
        
        # Generate task list
        tasks_content = await self.generate_task_list(user_request)
        tasks_path = self.docs_dir / "tasks.md"
        with open(tasks_path, 'w') as f:
            f.write(tasks_content)
        
        self.logger.info("Documentation generated successfully")
    
    async def generate_requirements(self, user_request: str) -> str:
        """Generate requirements document"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# Project Requirements

Generated on: {timestamp}

## User Request
{user_request}

## Functional Requirements
- The system should fulfill the user's request as specified
- All components should work together seamlessly
- Error handling should be robust and user-friendly
- The solution should be scalable and maintainable

## Technical Requirements
- Code should follow best practices and conventions
- Comprehensive testing should be implemented
- Documentation should be clear and complete
- Performance should be optimized for the target use case

## Acceptance Criteria
- All specified functionality is implemented
- Tests pass successfully
- Code is well-documented
- Performance meets requirements
"""
    
    async def generate_design(self, user_request: str) -> str:
        """Generate design document"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# System Design

Generated on: {timestamp}

## Overview
This document outlines the system design for the requested project.

## Architecture
- Component-based architecture
- Modular design for maintainability
- Clear separation of concerns
- Scalable and extensible structure

## Components
### Core Components
- Main application logic
- Data processing modules
- User interface components
- Configuration management

### Supporting Components
- Error handling system
- Logging and monitoring
- Testing framework
- Documentation system

## Implementation Strategy
1. Start with core functionality
2. Implement supporting features
3. Add comprehensive testing
4. Optimize performance
5. Complete documentation
"""
    
    async def generate_task_list(self, user_request: str) -> str:
        """Generate task list"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# Task List

Generated on: {timestamp}

## Architecture Tasks
- [ ] **requirements_analysis** - Analyze and document system requirements (Priority: 1, Agent: architect)
- [ ] **architecture_design** - Design system architecture and components (Priority: 2, Agent: architect, Dependencies: requirements_analysis)

## Design Tasks
- [ ] **ui_design** - Create user interface designs (Priority: 3, Agent: designer, Dependencies: requirements_analysis)

## Development Tasks
- [ ] **core_implementation** - Implement core functionality (Priority: 4, Agent: developer, Dependencies: architecture_design)
- [ ] **feature_implementation** - Implement additional features (Priority: 5, Agent: developer, Dependencies: core_implementation)
- [ ] **integration** - Integrate all components (Priority: 6, Agent: developer, Dependencies: feature_implementation, ui_design)

## Testing Tasks
- [ ] **unit_testing** - Create and run unit tests (Priority: 7, Agent: qa, Dependencies: core_implementation)
- [ ] **integration_testing** - Create and run integration tests (Priority: 8, Agent: qa, Dependencies: integration)
- [ ] **system_testing** - Perform system-level testing (Priority: 9, Agent: qa, Dependencies: integration_testing)

## Documentation Tasks
- [ ] **documentation** - Create comprehensive documentation (Priority: 10, Agent: developer, Dependencies: system_testing)
"""
    
    async def get_user_confirmation(self) -> bool:
        """Get user confirmation for the generated documentation"""
        print("\n" + "="*60)
        print("GENERATED DOCUMENTATION")
        print("="*60)
        
        # Display requirements
        req_path = self.docs_dir / "requirements.md"
        if req_path.exists():
            print("\nREQUIREMENTS:")
            with open(req_path, 'r') as f:
                print(f.read())
        
        # Display design
        design_path = self.docs_dir / "design.md"
        if design_path.exists():
            print("\nDESIGN:")
            with open(design_path, 'r') as f:
                print(f.read())
        
        # Display tasks
        tasks_path = self.docs_dir / "tasks.md"
        if tasks_path.exists():
            print("\nTASKS:")
            with open(tasks_path, 'r') as f:
                print(f.read())
        
        print("\n" + "="*60)
        response = input("Do you want to proceed with this plan? (y/n): ")
        return response.lower() in ['y', 'yes']
    
    async def spawn_sub_agents(self) -> None:
        """Spawn sub-agents in separate terminals"""
        self.logger.info("Spawning sub-agents")
        
        agent_configs = self.config_manager.config["agents"]
        
        for agent_name, config in agent_configs.items():
            self.logger.info(f"Spawning agent: {agent_name}")
            
            # Create agent instance info
            agent_info = {
                "name": agent_name,
                "role": config["role"],
                "port": config["port"],
                "status": "starting",
                "workspace": str(self.workspace)
            }
            
            # Start agent process
            process = await self.start_agent_process(agent_name, config["port"])
            
            self.agents[agent_name] = agent_info
            self.agent_processes[agent_name] = process
            
            # Wait for agent to be ready
            await self.wait_for_agent_ready(agent_name, config["port"])
            
            self.agents[agent_name]["status"] = "ready"
            self.logger.info(f"Agent {agent_name} is ready")
    
    async def start_agent_process(self, agent_name: str, port: int) -> subprocess.Popen:
        """Start an agent process"""
        cmd = [
            "python", "-m", "agent_collab.sub_agent",
            "--name", agent_name,
            "--port", str(port),
            "--workspace", str(self.workspace)
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return process
    
    async def wait_for_agent_ready(self, agent_name: str, port: int, timeout: int = 30) -> None:
        """Wait for an agent to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://localhost:{port}/health") as response:
                        if response.status == 200:
                            return
            except:
                pass
            
            await asyncio.sleep(1)
        
        raise TimeoutError(f"Agent {agent_name} failed to start within {timeout} seconds")
    
    async def assign_and_monitor_tasks(self) -> str:
        """Assign tasks to agents and monitor execution"""
        self.logger.info("Starting task assignment and monitoring")
        
        # Load and assign tasks
        await self.task_manager.load_tasks_from_file()
        await self.task_manager.assign_tasks()
        
        # Monitor task execution
        results = []
        while not self.task_manager.all_tasks_completed():
            await asyncio.sleep(2)
            
            # Check agent status
            for agent_name in self.agents:
                status = await self.get_agent_status(agent_name)
                if status:
                    self.agents[agent_name]["status"] = status.get("status", "unknown")
        
        # Collect final results
        for agent_name in self.agents:
            agent_results = await self.get_agent_results(agent_name)
            if agent_results:
                results.append(f"Agent {agent_name}: {agent_results}")
        
        return "\n".join(results) if results else "All tasks completed successfully"
    
    async def get_agent_status(self, agent_name: str) -> Optional[Dict]:
        """Get status from an agent"""
        try:
            port = self.agents[agent_name]["port"]
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/status") as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            self.logger.warning(f"Failed to get status from {agent_name}: {e}")
        return None
    
    async def get_agent_results(self, agent_name: str) -> Optional[str]:
        """Get results from an agent"""
        try:
            port = self.agents[agent_name]["port"]
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/results") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", "")
        except Exception as e:
            self.logger.warning(f"Failed to get results from {agent_name}: {e}")
        return None
    
    async def cleanup_agents(self) -> None:
        """Clean up agent processes"""
        self.logger.info("Cleaning up agent processes")
        
        for agent_name, process in self.agent_processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        self.agent_processes.clear()
        self.agents.clear()
        self.logger.info("Agent cleanup completed")