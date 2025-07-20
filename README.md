# Claude Composer
This package adds Claude code commands `/composer` and will enable you composing multiple agents simultanously.

## Quick start
```
npm i claude-code-composer
claude
/composer 'ex:create memo app'
```

## Installation

```
npm i claude-code-composer
```

The command will be automatically installed in your `.claude/commands` directory during the post-install process.

## Manual Installation

If you need to reinstall or install in a different project:
```
npx claude-composer install
```

## What it creates
- `.claude/commands/composer.md` - The command documentation and specification

## Usage in Claude Code

After installation, you can use the `/composer` command in Claude Code:

\`\`\`
composer init
composer build --verbose
composer deploy --dry-run
\`\`\`

## Customization

You can edit the `.claude/commands/composer.md` file to customize the command behavior and documentation according to your project needs.
