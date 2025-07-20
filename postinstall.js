import { createComposerCommand } from './index.js';

async function postInstall() {
  try {
    console.log('🚀 Setting up Claude Composer command...');
    await createComposerCommand();
    console.log('✅ Claude Composer command installed successfully!');
  } catch (error) {
    console.error('❌ Failed to install Claude Composer command:', error.message);
    process.exit(1);
  }
}

postInstall();