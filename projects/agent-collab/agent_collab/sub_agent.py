"""Sub-Agent - Specialized agent for executing specific types of tasks"""

import asyncio
import json
import subprocess
import tempfile
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from aiohttp import web
import aiohttp
import argparse
import signal
import sys


class SubAgent:
    """Specialized agent responsible for executing specific types of tasks"""
    
    def __init__(self, name: str, role: str, port: int, workspace: str):
        self.name = name
        self.role = role
        self.port = port
        self.workspace = Path(workspace)
        self.current_task = None
        self.task_results = []
        self.status = "idle"
        
        # Setup logging
        self.setup_logging()
        
        # Create agent-specific workspace
        self.agent_workspace = self.workspace / f"agent_{name}"
        self.agent_workspace.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"SubAgent {name} initialized with role {role}")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format=f'%(asctime)s - {self.name} - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f"SubAgent.{self.name}")
    
    async def start(self) -> None:
        """Start the sub-agent HTTP server"""
        app = web.Application()
        app.router.add_get('/health', self.health_check)
        app.router.add_get('/status', self.get_status)
        app.router.add_post('/task', self.execute_task)
        app.router.add_get('/results', self.get_results)
        
        self.logger.info(f"Starting sub-agent server on port {self.port}")
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        self.logger.info(f"Sub-agent {self.name} is ready and listening on port {self.port}")
        
        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            self.logger.info("Shutting down sub-agent")
            await runner.cleanup()
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "agent": self.name})
    
    async def get_status(self, request):
        """Get current agent status"""
        return web.json_response({
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "current_task": self.current_task,
            "completed_tasks": len(self.task_results)
        })
    
    async def execute_task(self, request):
        """Execute a task assigned by the composer agent"""
        try:
            task_data = await request.json()
            self.logger.info(f"Received task: {task_data.get('title', 'Unknown')}")
            
            self.current_task = task_data
            self.status = "working"
            
            # Execute the task based on role
            result = await self.process_task(task_data)
            
            # Store result
            self.task_results.append({
                "task": task_data,
                "result": result,
                "status": "completed"
            })
            
            self.current_task = None
            self.status = "idle"
            
            return web.json_response({
                "status": "completed",
                "result": result
            })
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            self.status = "error"
            return web.json_response({
                "status": "failed",
                "error": str(e)
            }, status=500)
    
    async def get_results(self, request):
        """Get all task results"""
        return web.json_response({
            "agent": self.name,
            "results": self.task_results
        })
    
    async def process_task(self, task: Dict[str, Any]) -> str:
        """Process a task based on the agent's role"""
        task_type = task.get("type", "")
        description = task.get("description", "")
        
        if self.role == "code_implementation":
            return await self.handle_development_task(task)
        elif self.role == "quality_assurance":
            return await self.handle_qa_task(task)
        elif self.role == "ui_ux_design":
            return await self.handle_design_task(task)
        elif self.role == "system_architecture":
            return await self.handle_architecture_task(task)
        else:
            return await self.handle_generic_task(task)
    
    async def handle_development_task(self, task: Dict[str, Any]) -> str:
        """Handle development-related tasks"""
        task_description = task.get("description", "")
        
        # Create a prompt for Claude Code
        prompt = f"""
Task: {task.get('title', 'Development Task')}
Description: {task_description}

Please implement the requested functionality. Focus on:
1. Writing clean, maintainable code
2. Following best practices
3. Adding appropriate error handling
4. Including relevant comments
5. Ensuring the code is testable
"""
        
        result = await self.claude_code_execute(prompt)
        
        # Save result to workspace
        result_file = self.agent_workspace / f"task_{task.get('id', 'unknown')}_result.md"
        with open(result_file, 'w') as f:
            f.write(f"# Development Task Result\n\n{result}")
        
        return result
    
    async def handle_qa_task(self, task: Dict[str, Any]) -> str:
        """Handle quality assurance tasks"""
        task_description = task.get("description", "")
        
        prompt = f"""
Task: {task.get('title', 'QA Task')}
Description: {task_description}

Please create comprehensive tests for the functionality. Include:
1. Unit tests for individual components
2. Integration tests for component interactions
3. Edge case testing
4. Error handling validation
5. Performance considerations
6. Test documentation
"""
        
        result = await self.claude_code_execute(prompt)
        
        result_file = self.agent_workspace / f"task_{task.get('id', 'unknown')}_tests.md"
        with open(result_file, 'w') as f:
            f.write(f"# QA Task Result\n\n{result}")
        
        return result
    
    async def handle_design_task(self, task: Dict[str, Any]) -> str:
        """Handle UI/UX design tasks"""
        task_description = task.get("description", "")
        
        prompt = f"""
Task: {task.get('title', 'Design Task')}
Description: {task_description}

Please create UI/UX designs focusing on:
1. User experience and usability
2. Visual design and aesthetics
3. Responsive design principles
4. Accessibility considerations
5. Design system consistency
6. User interface specifications
"""
        
        result = await self.claude_code_execute(prompt)
        
        result_file = self.agent_workspace / f"task_{task.get('id', 'unknown')}_design.md"
        with open(result_file, 'w') as f:
            f.write(f"# Design Task Result\n\n{result}")
        
        return result
    
    async def handle_architecture_task(self, task: Dict[str, Any]) -> str:
        """Handle system architecture tasks"""
        task_description = task.get("description", "")
        
        prompt = f"""
Task: {task.get('title', 'Architecture Task')}
Description: {task_description}

Please design the system architecture considering:
1. System components and their relationships
2. Data flow and processing patterns
3. Scalability and performance requirements
4. Security considerations
5. Technology stack recommendations
6. Deployment and infrastructure needs
"""
        
        result = await self.claude_code_execute(prompt)
        
        result_file = self.agent_workspace / f"task_{task.get('id', 'unknown')}_architecture.md"
        with open(result_file, 'w') as f:
            f.write(f"# Architecture Task Result\n\n{result}")
        
        return result
    
    async def handle_generic_task(self, task: Dict[str, Any]) -> str:
        """Handle generic tasks"""
        task_description = task.get("description", "")
        
        prompt = f"""
Task: {task.get('title', 'Generic Task')}
Description: {task_description}

Please complete this task with attention to:
1. Understanding the requirements clearly
2. Providing a comprehensive solution
3. Considering edge cases and limitations
4. Documenting the approach and results
5. Ensuring quality and completeness
"""
        
        result = await self.claude_code_execute(prompt)
        
        result_file = self.agent_workspace / f"task_{task.get('id', 'unknown')}_generic.md"
        with open(result_file, 'w') as f:
            f.write(f"# Generic Task Result\n\n{result}")
        
        return result
    
    async def claude_code_execute(self, prompt: str) -> str:
        """Execute a task using Claude Code"""
        try:
            # Create a temporary file with the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            # Execute Claude Code with the prompt
            cmd = ['claude-code', '--prompt', prompt_file, '--workspace', str(self.agent_workspace)]
            
            self.logger.info(f"Executing Claude Code for task")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.agent_workspace)
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up temporary file
            os.unlink(prompt_file)
            
            if process.returncode == 0:
                return stdout.decode('utf-8')
            else:
                error_msg = stderr.decode('utf-8')
                self.logger.error(f"Claude Code execution failed: {error_msg}")
                return f"Task execution failed: {error_msg}"
                
        except Exception as e:
            self.logger.error(f"Failed to execute Claude Code: {str(e)}")
            return f"Failed to execute task: {str(e)}"


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    sys.exit(0)


async def main():
    """Main function to run the sub-agent"""
    parser = argparse.ArgumentParser(description="Sub-Agent for multi-agent collaboration")
    parser.add_argument("--name", required=True, help="Agent name")
    parser.add_argument("--role", help="Agent role")
    parser.add_argument("--port", type=int, required=True, help="Port number")
    parser.add_argument("--workspace", required=True, help="Workspace directory")
    
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start the sub-agent
    agent = SubAgent(args.name, args.role or args.name, args.port, args.workspace)
    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())