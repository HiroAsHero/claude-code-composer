"""Command Line Interface for the Agent Collaboration Framework"""

import asyncio
import click
import logging
import os
from pathlib import Path

from .composer_agent import ComposerAgent
from .config import ConfigManager


@click.group()
@click.version_option()
def cli():
    """Agent Collaboration Framework - Multi-agent collaboration for Claude Code"""
    pass


@cli.command()
@click.argument('request', type=str)
@click.option('--workspace', '-w', 
              default='./workspace',
              help='Workspace directory (default: ./workspace)')
@click.option('--config', '-c',
              type=click.Path(exists=True),
              help='Configuration file path')
@click.option('--verbose', '-v', 
              is_flag=True,
              help='Enable verbose logging')
@click.option('--no-confirm', 
              is_flag=True,
              help='Skip user confirmation for generated documentation')
def run(request, workspace, config, verbose, no_confirm):
    """Run the multi-agent collaboration system with the given request"""
    
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Agent Collaboration Framework")
    
    try:
        # Create composer agent
        composer = ComposerAgent(
            workspace=workspace,
            config_path=config,
            verbose=verbose,
            no_confirm=no_confirm
        )
        
        # Run orchestration
        result = asyncio.run(composer.orchestrate(request))
        
        click.echo("\n" + "="*60)
        click.echo("COLLABORATION RESULTS")
        click.echo("="*60)
        click.echo(result)
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        click.echo("\nProcess interrupted by user")
    except Exception as e:
        logger.error(f"Collaboration failed: {str(e)}")
        click.echo(f"\nError: {str(e)}", err=True)
        raise click.ClickException(str(e))


@cli.command()
@click.option('--workspace', '-w',
              default='./workspace',
              help='Workspace directory (default: ./workspace)')
@click.option('--config', '-c',
              type=click.Path(),
              help='Configuration file path')
def init(workspace, config):
    """Initialize a new workspace with default configuration"""
    
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)
    
    # Create default configuration
    config_manager = ConfigManager()
    config_path = config or workspace_path / "config.yaml"
    config_manager.save_config(str(config_path))
    
    # Create directory structure
    dirs_to_create = [
        workspace_path / "docs",
        workspace_path / "agent_developer",
        workspace_path / "agent_qa",
        workspace_path / "agent_designer",
        workspace_path / "agent_architect"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"Workspace initialized at: {workspace_path}")
    click.echo(f"Configuration saved to: {config_path}")


@cli.command()
@click.option('--config', '-c',
              type=click.Path(exists=True),
              help='Configuration file path')
def validate(config):
    """Validate configuration file"""
    
    try:
        config_manager = ConfigManager(config)
        config_manager.validate_config()
        click.echo("Configuration is valid")
    except Exception as e:
        click.echo(f"Configuration validation failed: {str(e)}", err=True)
        raise click.ClickException(str(e))


@cli.command()
@click.option('--config', '-c',
              type=click.Path(exists=True),
              help='Configuration file path')
def show_config(config):
    """Display current configuration"""
    
    config_manager = ConfigManager(config)
    
    click.echo("Current Configuration:")
    click.echo("="*50)
    
    # Show agents
    click.echo("\nAgents:")
    for agent_name, agent_config in config_manager.config["agents"].items():
        click.echo(f"  {agent_name}:")
        click.echo(f"    Role: {agent_config['role']}")
        click.echo(f"    Port: {agent_config['port']}")
        click.echo(f"    Max Parallel Tasks: {agent_config['max_parallel_tasks']}")
        click.echo(f"    Timeout: {agent_config['timeout']}s")
        click.echo(f"    Retry Count: {agent_config['retry_count']}")
        click.echo()
    
    # Show task types
    click.echo("Task Types:")
    for task_type, task_config in config_manager.config["task_types"].items():
        click.echo(f"  {task_type}:")
        click.echo(f"    Agent: {task_config['agent']}")
        click.echo(f"    Priority: {task_config['priority']}")
        click.echo(f"    Dependencies: {task_config['dependencies']}")
        click.echo()
    
    # Show system config
    click.echo("System:")
    system_config = config_manager.config["system"]
    for key, value in system_config.items():
        click.echo(f"  {key}: {value}")


@cli.command()
@click.argument('agent_name', type=str)
@click.option('--port', '-p', 
              type=int,
              default=8000,
              help='Port number for the agent (default: 8000)')
@click.option('--workspace', '-w',
              default='./workspace',
              help='Workspace directory (default: ./workspace)')
@click.option('--role', '-r',
              help='Agent role (defaults to agent name)')
def start_agent(agent_name, port, workspace, role):
    """Start a single sub-agent for testing"""
    
    from .sub_agent import SubAgent
    
    click.echo(f"Starting agent '{agent_name}' on port {port}")
    
    try:
        agent = SubAgent(
            name=agent_name,
            role=role or agent_name,
            port=port,
            workspace=workspace
        )
        
        asyncio.run(agent.start())
        
    except KeyboardInterrupt:
        click.echo(f"\nAgent '{agent_name}' stopped")
    except Exception as e:
        click.echo(f"Failed to start agent: {str(e)}", err=True)
        raise click.ClickException(str(e))


@cli.command()
@click.option('--workspace', '-w',
              default='./workspace',
              help='Workspace directory (default: ./workspace)')
def status(workspace):
    """Show status of the workspace"""
    
    workspace_path = Path(workspace)
    
    if not workspace_path.exists():
        click.echo(f"Workspace does not exist: {workspace_path}")
        return
    
    click.echo(f"Workspace: {workspace_path}")
    click.echo("="*50)
    
    # Check for documentation
    docs_dir = workspace_path / "docs"
    if docs_dir.exists():
        click.echo("\nDocumentation:")
        for doc_file in docs_dir.glob("*.md"):
            click.echo(f"  ✓ {doc_file.name}")
    else:
        click.echo("\nDocumentation: Not found")
    
    # Check for agent workspaces
    click.echo("\nAgent Workspaces:")
    for agent_dir in workspace_path.glob("agent_*"):
        if agent_dir.is_dir():
            file_count = len(list(agent_dir.glob("*")))
            click.echo(f"  ✓ {agent_dir.name} ({file_count} files)")
    
    # Check for configuration
    config_path = workspace_path / "config.yaml"
    if config_path.exists():
        click.echo(f"\nConfiguration: ✓ {config_path}")
    else:
        click.echo("\nConfiguration: Not found")


def main():
    """Main entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()