# Agent Collaboration Framework Examples

This directory contains examples demonstrating how to use the Agent Collaboration Framework.

## Files

- `config.yaml`: Example configuration file
- `example_usage.py`: Python script with usage examples
- `README.md`: This file

## Running Examples

### 1. Web Application Example

```bash
agent-collab run "Create a Flask web application for task management with user authentication" --workspace ./examples/webapp --config ./examples/config.yaml
```

### 2. API Service Example

```bash
agent-collab run "Build a REST API service for library management with book search and user reviews" --workspace ./examples/api --config ./examples/config.yaml
```

### 3. Data Pipeline Example

```bash
agent-collab run "Implement a data processing pipeline that reads CSV files and generates reports" --workspace ./examples/pipeline --config ./examples/config.yaml
```

### 4. Run All Examples with Python

```bash
python examples/example_usage.py
```

## Example Configuration

The `config.yaml` file contains a standard configuration with:

- 4 agents (developer, qa, designer, architect)
- 8 task types with proper dependencies
- System settings for workspace and logging

## Expected Output

Each example will:

1. Generate project documentation (requirements, design, tasks)
2. Start specialized agents
3. Assign tasks based on dependencies
4. Execute tasks in parallel where possible
5. Provide aggregated results

## Customization

You can customize the examples by:

- Modifying the configuration in `config.yaml`
- Changing the request descriptions
- Adjusting agent roles and capabilities
- Adding new task types

## Troubleshooting

If you encounter issues:

1. Ensure all ports in the configuration are available
2. Check that Claude Code is properly installed
3. Verify workspace permissions
4. Review log files for detailed error information

## Next Steps

After running the examples, you can:

1. Examine the generated documentation in each workspace
2. Review the agent-specific outputs
3. Customize the configuration for your use case
4. Create your own collaboration scenarios