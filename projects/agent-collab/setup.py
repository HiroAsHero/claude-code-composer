from setuptools import setup, find_packages

setup(
    name="agent-collab",
    version="0.1.0",
    description="Multi-agent collaboration framework for Claude Code",
    author="Agent Collaboration Team",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "aiofiles>=0.8.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "asyncio",
        "subprocess",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "agent-collab=agent_collab.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)