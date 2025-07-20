# Claude Composer Command

This package adds a `composer` command to your Claude Code environment by creating a `composer.md` file in the `.claude/commands` directory.

## Installation

\`\`\`bash
npm install claude-composer-command
\`\`\`

The command will be automatically installed in your `.claude/commands` directory during the post-install process.

## Manual Installation

If you need to reinstall or install in a different project:

\`\`\`bash
npx claude-composer install
\`\`\`

## What it creates

- `.claude/commands/composer.md` - The command documentation and specification

## Usage in Claude Code

After installation, you can use the `composer` command in Claude Code:

\`\`\`
composer init
composer build --verbose
composer deploy --dry-run
\`\`\`

## Customization

You can edit the `.claude/commands/composer.md` file to customize the command behavior and documentation according to your project needs.
