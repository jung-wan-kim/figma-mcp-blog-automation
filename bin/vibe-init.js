#!/usr/bin/env node

/**
 * Vibe CLI - 프로젝트 초기화 명령어
 * 
 * 사용법:
 * npm run init                 # 대화형 선택
 * npm run init:figma          # Figma 연동
 * npm run init:markdown       # Markdown 파일 기반
 * npm run init:template       # 템플릿 기반
 */

import { ProjectInitializer } from '../src/core/project-initializer.js';

console.log(`
██╗   ██╗██╗██████╗ ███████╗
██║   ██║██║██╔══██╗██╔════╝
██║   ██║██║██████╔╝█████╗  
╚██╗ ██╔╝██║██╔══██╗██╔══╝  
 ╚████╔╝ ██║██████╔╝███████╗
  ╚═══╝  ╚═╝╚═════╝ ╚══════╝

Figma → React 자동화 시스템
`);

// 명령행 인수 처리
const args = process.argv.slice(2);
let initMethod = null;

if (args.includes('--figma')) {
  initMethod = 'figma';
} else if (args.includes('--markdown')) {
  initMethod = 'markdown';
} else if (args.includes('--template')) {
  initMethod = 'template';
}

try {
  const initializer = new ProjectInitializer();
  
  if (initMethod) {
    // 특정 방법으로 바로 시작
    console.log(`선택된 초기화 방법: ${getMethodName(initMethod)}\n`);
    const result = await initializer.initMethods[initMethod].initialize();
    await initializer.generateProjectStructure(result);
    await showCompletion();
  } else {
    // 대화형 선택
    await initializer.start();
  }
} catch (error) {
  console.error('\n❌ 초기화 실패:', error.message);
  
  if (error.code === 'MODULE_NOT_FOUND') {
    console.log('\n💡 해결 방법:');
    console.log('1. npm install');
    console.log('2. npm run setup');
  }
  
  process.exit(1);
}

function getMethodName(method) {
  const names = {
    figma: '🎨 Figma 연동',
    markdown: '📝 Markdown 기반',
    template: '📋 템플릿 기반'
  };
  return names[method];
}

async function showCompletion() {
  console.log('\n🎉 프로젝트 초기화 완료!');
  console.log('\n🚀 다음 단계:');
  console.log('1. npm run dev - 개발 서버 시작');
  console.log('2. npm run dashboard:server - 대시보드 시작');  
  console.log('3. npm run test:integration - 통합 테스트');
}