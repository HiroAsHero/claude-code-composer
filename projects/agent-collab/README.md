# Agent Collaboration Framework

A multi-agent collaboration framework for Claude Code that enables multiple AI agents to work together on software development tasks.

## Overview

The Agent Collaboration Framework orchestrates multiple specialized AI agents working collaboratively on software development tasks. It follows a hub-and-spoke architecture with a central Composer Agent coordinating multiple specialized Sub-Agents, each running in its own process.

## Architecture

### Components

- **Composer Agent**: Central orchestrator that manages the entire collaboration process
- **Sub-Agents**: Specialized agents for different tasks (Developer, QA, Designer, Architect)
- **Task Manager**: Handles task assignment, dependency resolution, and execution tracking
- **Configuration Manager**: Manages system and agent configurations

### Process Flow

1. User provides a project request
2. Composer Agent generates project documentation (requirements, design, tasks)
3. User reviews and approves the documentation
4. Composer Agent spawns Sub-Agents in separate processes
5. Task Manager assigns tasks to appropriate Sub-Agents based on dependencies
6. Sub-Agents execute tasks and report results back to Composer Agent
7. Composer Agent aggregates results and provides final summary

## Installation

### From Source

```bash
git clone <repository-url>
cd agent-collab
pip install -e .
```

### From PyPI (when available)

```bash
pip install agent-collab
```

## Quick Start

### 1. Initialize a workspace

```bash
agent-collab init --workspace ./my-project
```

### 2. Run a collaboration session

```bash
agent-collab run "Create a web application for managing tasks" --workspace ./my-project
```

### 3. Check status

```bash
agent-collab status --workspace ./my-project
```

## Configuration

The framework uses YAML configuration files. A default configuration is created when initializing a workspace.

### Example Configuration

```yaml
agents:
  developer:
    role: "code_implementation"
    max_parallel_tasks: 3
    timeout: 300
    retry_count: 2
    port: 8001
  qa:
    role: "quality_assurance"
    max_parallel_tasks: 2
    timeout: 180
    retry_count: 1
    port: 8002
  designer:
    role: "ui_ux_design"
    max_parallel_tasks: 2
    timeout: 240
    retry_count: 1
    port: 8003
  architect:
    role: "system_architecture"
    max_parallel_tasks: 1
    timeout: 400
    retry_count: 2
    port: 8004

task_types:
  requirements_analysis:
    agent: "architect"
    priority: 1
    dependencies: []
  architecture_design:
    agent: "architect"
    priority: 2
    dependencies: ["requirements_analysis"]
  ui_design:
    agent: "designer"
    priority: 3
    dependencies: ["requirements_analysis"]
  code_implementation:
    agent: "developer"
    priority: 4
    dependencies: ["architecture_design"]
  unit_testing:
    agent: "qa"
    priority: 5
    dependencies: ["code_implementation"]

system:
  workspace: "./workspace"
  log_level: "INFO"
  timeout: 3600
  composer_port: 8000
```

## CLI Commands

### Main Commands

- `agent-collab run <request>`: Start a collaboration session
- `agent-collab init`: Initialize a new workspace
- `agent-collab status`: Show workspace status
- `agent-collab validate`: Validate configuration
- `agent-collab show-config`: Display current configuration

### Options

- `--workspace, -w`: Specify workspace directory
- `--config, -c`: Specify configuration file path
- `--verbose, -v`: Enable verbose logging
- `--no-confirm`: Skip user confirmation for generated documentation

### Testing Commands

- `agent-collab start-agent <name>`: Start a single agent for testing

## Agent Roles

### Developer Agent
- Implements code based on specifications
- Focuses on clean, maintainable code
- Handles error handling and testing setup

### QA Agent
- Creates and runs tests
- Validates functionality
- Performs quality assurance checks

### Designer Agent
- Creates UI/UX designs
- Handles user interface specifications
- Considers accessibility and usability

### Architect Agent
- Designs system architecture
- Handles requirements analysis
- Makes technology stack decisions

## Task Management

Tasks are automatically parsed from generated documentation and assigned to appropriate agents based on:

- Task type and agent specialization
- Priority levels
- Dependency relationships
- Agent availability

### Task Format

Tasks in the documentation follow this format:

```markdown
- [ ] **task_name** - Description (Priority: 1, Agent: architect, Dependencies: other_task)
```

## Error Handling

The framework includes comprehensive error handling:

- **Task-level**: Retry mechanisms with exponential backoff
- **Agent-level**: Health monitoring and automatic restart
- **System-level**: Graceful shutdown and error reporting

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

```bash
black agent_collab/
flake8 agent_collab/
```

### Type Checking

```bash
mypy agent_collab/
```

## Examples

### Example 1: Web Application

```bash
agent-collab run "Create a Flask web application with user authentication and a task management system" --workspace ./webapp
```

### Example 2: API Service

```bash
agent-collab run "Build a REST API service for managing a library catalog with book search and user reviews" --workspace ./api
```

### Example 3: Data Pipeline

```bash
agent-collab run "Implement a data processing pipeline that reads CSV files, processes them, and generates reports" --workspace ./pipeline
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure the configured ports are available
2. **Agent startup failures**: Check logs for specific error messages
3. **Task dependencies**: Verify task dependency chains are not circular
4. **Configuration errors**: Use `agent-collab validate` to check configuration

### Logging

Enable verbose logging for debugging:

```bash
agent-collab run "..." --verbose
```

Log files are stored in the workspace directory under `logs/`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Documentation: <docs-url>