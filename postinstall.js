// 動作する postinstall.js
import { createComposerCommand } from './index.js';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function postInstall() {
  try {
    console.log('🚀 Setting up Claude Code Composer command...');
    
    // プロジェクトルートを特定する方法
    let projectRoot = process.cwd();
    
    // npm install時は、プロジェクトルートがprocess.env.INIT_CWDに保存される
    if (process.env.INIT_CWD) {
      projectRoot = process.env.INIT_CWD;
    } else if (__dirname.includes('node_modules')) {
      // node_modules内にいる場合、プロジェクトルートを特定
      const nodeModulesIndex = __dirname.indexOf('node_modules');
      projectRoot = __dirname.substring(0, nodeModulesIndex);
    }
    
    console.log(`📂 Project root: ${projectRoot}`);
    console.log(`📂 Current working directory: ${process.cwd()}`);
    console.log(`📂 Package directory: ${__dirname}`);
    
    await createComposerCommand(projectRoot);
    console.log('✅ Claude Code Composer command installed successfully!');
  } catch (error) {
    console.error('❌ Failed to install Claude Code Composer command:', error.message);
    console.error('📍 Error details:', {
      message: error.message,
      code: error.code,
      path: error.path
    });
    
    // デバッグ情報を出力
    console.log('🔍 Debug info:');
    console.log('- process.cwd():', process.cwd());
    console.log('- process.env.INIT_CWD:', process.env.INIT_CWD);
    console.log('- __dirname:', __dirname);
    
    // postinstallエラーでインストール全体を失敗させないように
    console.log('⚠️  Automatic installation failed. You can manually install by running:');
    console.log('   npx claude-code-composer install');
    
    // exit(1)だとnpm installが失敗するので、exit(0)で警告のみ
    process.exit(0);
  }
}

postInstall();