#!/usr/bin/env python3
"""
Example usage of the Agent Collaboration Framework
"""

import asyncio
from pathlib import Path
from agent_collab import ComposerAgent


async def example_web_app():
    """Example: Create a web application"""
    print("Example 1: Web Application Development")
    print("=" * 50)
    
    # Initialize composer agent
    composer = ComposerAgent(
        workspace="./examples/webapp",
        config_path="./examples/config.yaml",
        verbose=True,
        no_confirm=True  # Skip user confirmation for example
    )
    
    # Define the request
    request = """
    Create a Flask web application for task management with the following features:
    - User authentication (login/logout)
    - Task creation and management
    - Task assignment to users
    - Task status tracking
    - Dashboard with task statistics
    - Responsive design
    - RESTful API endpoints
    - Unit and integration tests
    """
    
    try:
        result = await composer.orchestrate(request)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")


async def example_api_service():
    """Example: Create an API service"""
    print("\nExample 2: API Service Development")
    print("=" * 50)
    
    composer = ComposerAgent(
        workspace="./examples/api",
        config_path="./examples/config.yaml",
        verbose=True,
        no_confirm=True
    )
    
    request = """
    Build a REST API service for a library management system:
    - Book catalog management (CRUD operations)
    - User management and authentication
    - Book search and filtering
    - User reviews and ratings
    - Borrowing system
    - Database integration
    - API documentation
    - Comprehensive testing
    """
    
    try:
        result = await composer.orchestrate(request)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")


async def example_data_pipeline():
    """Example: Create a data processing pipeline"""
    print("\nExample 3: Data Pipeline Development")
    print("=" * 50)
    
    composer = ComposerAgent(
        workspace="./examples/pipeline",
        config_path="./examples/config.yaml",
        verbose=True,
        no_confirm=True
    )
    
    request = """
    Implement a data processing pipeline with the following components:
    - CSV file ingestion and validation
    - Data transformation and cleaning
    - Statistical analysis and reporting
    - Data export to multiple formats
    - Error handling and logging
    - Configuration management
    - Performance optimization
    - Monitoring and alerting
    """
    
    try:
        result = await composer.orchestrate(request)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all examples"""
    print("Agent Collaboration Framework Examples")
    print("=" * 60)
    
    # Create examples directory
    examples_dir = Path("./examples")
    examples_dir.mkdir(exist_ok=True)
    
    # Run examples
    await example_web_app()
    await example_api_service()
    await example_data_pipeline()
    
    print("\n" + "=" * 60)
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())