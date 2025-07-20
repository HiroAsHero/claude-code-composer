import fs from 'fs/promises';
import path from 'path';

export async function createComposerCommand(projectRoot = process.cwd()) {
  const claudeDir = path.join(projectRoot, '.claude');
  const commandsDir = path.join(claudeDir, 'commands');
  const composerFile = path.join(commandsDir, 'composer.md');

  // .claude/commands ディレクトリを作成
  await fs.mkdir(commandsDir, { recursive: true });

  // composer.md の内容
  const composerContent = `---
allowed-tools: [Read, Bash, Glob, TodoWrite, Edit]
description: "Compose multiple agents and execute tasks"
---

# /composer - Project building with several agents

## Purpose
Build, compile, and package projects with comprehensive error handling and optimization by coordinating multiple Claude Code agents.

## Usage
\`\`\`bash
/composer <project_description>
\`\`\`

Example:
\`\`\`bash
/composer create memo app
/composer build todo application with database
\`\`\`

## Role
You are the Composer Agent. You function as a coordinating agent that distributes tasks, provides context, and defines roles for multiple Claude Code Agents.

## Overview
Execute the following steps to realize the project specified in $ARGUMENTS.

## Execution Steps

1. **Project Confirmation**
   - Clarify user requirements and confirm project overview

2. **Directory Preparation**
   - Create \`.composer-agents\` directory if it doesn't exist
   \`\`\`bash
   mkdir -p .composer-agents
   \`\`\`

3. **Check Existing Files**
   - Check existing requirement definition files using Read tool
   \`\`\`bash
   # Check existence and read existing files
   ls .composer-agents/
   \`\`\`

4. **Create/Check Requirements Definition**
   - Check existence of \`requirements.md\` (attempt to read with Read tool)
   - Create new if it doesn't exist, confirm content if it exists
   - Confirm content with user and proceed to next step after approval

5. **Create/Check Design Document**
   - Check existence of \`design.md\` (attempt to read with Read tool)
   - Create new if it doesn't exist, confirm content if it exists
   - Confirm content with user and proceed to next step after approval

6. **Create/Check Task Division**
   - Check existence of \`tasks.md\` (attempt to read with Read tool)
   - Create new if it doesn't exist, confirm content if it exists
   - Assign integer numbers to each task
   - Confirm content with user and proceed to next step after approval

7. **Launch Sub-agents**
   - Launch multiple terminals according to the number of tasks in \`tasks.md\`
   - Automatically start Claude Code agents in each terminal

## Rules

- **File Operation Order**: Always read files with Read tool before using Edit/TodoWrite tools

- **Information Certainty**: When there are uncertain points or insufficient information, clearly state "There is not enough information to evaluate this reliably"

- **Evidence Documentation**: Always document evidence or sources when making judgments

- **Respect Existing Files**: If requirement definition files (\`requirements.md\`, \`design.md\`, \`tasks.md\`) already exist, utilize the existing ones

- **File Protection**: Do not rewrite requirement definition files unless explicitly instructed

- **Error Handling**: Maintain comprehensive error handling and reporting

- **Command Execution**: Use Bash for executing build commands

- **Communication**: Get user confirmation at each step and obtain approval before proceeding

## File Structure
\`\`\`
project-root/
├── .composer-agents/
│   ├── requirements.md  # Requirements definition
│   ├── design.md        # Design document
│   └── tasks.md         # Task division
└── [project files]
\`\`\`
`;

  // ファイルを作成
  await fs.writeFile(composerFile, composerContent, 'utf-8');
  
  console.log(`✅ composer.mdを作成しました: ${composerFile}`);
  return composerFile;
}
