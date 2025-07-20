#!/usr/bin/env node

import { createComposerCommand } from '../index.js';

const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'install':
    await createComposerCommand();
    break;
  case 'help':
  case '--help':
  case '-h':
    console.log(`
Claude Code Composer

Usage:
  claude-code-composer install    Install composer command in current project
  claude-code-composer help       Show this help message

After installation, you can use the '/composer' command in Claude Code.
    `);
    break;
  default:
    console.log('Unknown command. Use "claude-code-composer help" for usage information.');
    process.exit(1);
}
