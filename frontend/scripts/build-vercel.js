#!/usr/bin/env node

/**
 * Vercel专用构建脚本
 * 确保路径别名正确解析
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Starting Vercel build process...');

// 1. 确认环境
console.log('Environment:', process.env.NODE_ENV || 'production');
console.log('Current directory:', process.cwd());

// 2. 检查关键文件
const requiredFiles = [
  'package.json',
  'webpack.config.js',
  'tsconfig.json',
  'src/lib/utils.ts'
];

console.log('\n📋 Checking required files...');
requiredFiles.forEach(file => {
  if (!fs.existsSync(file)) {
    console.error(`❌ Missing required file: ${file}`);
    process.exit(1);
  }
  console.log(`✅ Found: ${file}`);
});

// 3. 运行构建
console.log('\n📦 Building project...');
try {
  execSync('npx webpack --mode production', { stdio: 'inherit' });
  console.log('\n✅ Build completed successfully!');
} catch (error) {
  console.error('\n❌ Build failed:', error.message);
  process.exit(1);
}

// 4. 验证输出
const distPath = path.join(process.cwd(), 'dist');
if (fs.existsSync(distPath)) {
  const files = fs.readdirSync(distPath);
  console.log(`\n✅ Output files generated: ${files.length}`);
  files.forEach(file => console.log(`  - ${file}`));
} else {
  console.error('\n❌ dist directory not found');
  process.exit(1);
}

console.log('\n🎉 Vercel build script completed!');