#!/usr/bin/env node
/**
 * MCP 서버 통합 테스트 스크립트
 * 모든 MCP 서버들이 올바르게 연동되는지 확인합니다.
 */

import { spawn } from 'child_process';
import fs from 'fs/promises';
import path from 'path';

const PROJECT_ROOT = '/Users/jung-wankim/Project/vibe';

// MCP 서버 목록
const MCP_SERVERS = [
  {
    name: 'TaskManager',
    path: path.join(PROJECT_ROOT, 'taskmanager-mcp-server'),
    testCommand: 'npm start',
    expectedLog: 'TaskManager MCP Server started',
  },
  {
    name: 'Figma',
    path: path.join(PROJECT_ROOT, 'figma-mcp-server'),
    testCommand: 'npm start',
    expectedLog: 'Figma MCP Server started',
  },
  {
    name: 'GitHub',
    path: path.join(PROJECT_ROOT, 'github-mcp-server'),
    testCommand: 'npm start',
    expectedLog: 'GitHub MCP Server started',
  },
  {
    name: 'Supabase',
    path: path.join(PROJECT_ROOT, 'supabase-mcp-server'),
    testCommand: 'npm start',
    expectedLog: 'Supabase MCP Server started',
  },
  {
    name: 'Dashboard',
    path: path.join(PROJECT_ROOT, 'dashboard-mcp-server'),
    testCommand: 'npm start',
    expectedLog: 'Dashboard MCP Server started',
  },
];

// 워크플로우 테스트 시나리오
const TEST_WORKFLOW = {
  name: 'test-integration-workflow',
  description: 'MCP 서버 통합 테스트 워크플로우',
  steps: [
    {
      id: 'detect-changes',
      name: 'Figma 변경사항 감지',
      mcp: 'figma-mcp',
      action: 'detect-changes',
      params: {},
    },
    {
      id: 'extract-components',
      name: '컴포넌트 추출',
      mcp: 'figma-mcp',
      action: 'extract-components',
      params: {},
    },
    {
      id: 'create-branch',
      name: 'GitHub 브랜치 생성',
      mcp: 'github-mcp',
      action: 'create-branch',
      params: {
        branchName: 'test/mcp-integration',
      },
    },
    {
      id: 'save-state',
      name: '워크플로우 상태 저장',
      mcp: 'supabase-mcp',
      action: 'save-workflow-state',
      params: {
        status: 'completed',
      },
    },
    {
      id: 'update-metrics',
      name: '대시보드 메트릭 업데이트',
      mcp: 'dashboard-mcp',
      action: 'update-workflow-metrics',
      params: {
        status: 'completed',
      },
    },
  ],
};

// 색상 코드
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// MCP 서버 시작 테스트
async function testMCPServer(server) {
  return new Promise((resolve) => {
    log(`\n테스트 중: ${server.name} MCP Server`, 'blue');
    
    const child = spawn(server.testCommand, {
      cwd: server.path,
      shell: true,
      stdio: 'pipe',
    });

    let output = '';
    let errorOutput = '';
    const timeout = setTimeout(() => {
      child.kill();
      resolve({
        name: server.name,
        success: false,
        error: '타임아웃 - 서버가 시작되지 않았습니다',
      });
    }, 5000);

    child.stdout.on('data', (data) => {
      output += data.toString();
    });

    child.stderr.on('data', (data) => {
      errorOutput += data.toString();
      if (errorOutput.includes(server.expectedLog)) {
        clearTimeout(timeout);
        child.kill();
        resolve({
          name: server.name,
          success: true,
        });
      }
    });

    child.on('error', (error) => {
      clearTimeout(timeout);
      resolve({
        name: server.name,
        success: false,
        error: error.message,
      });
    });
  });
}

// 워크플로우 파일 생성
async function createTestWorkflow() {
  const workflowPath = path.join(PROJECT_ROOT, 'workflows', 'test-integration.yaml');
  
  const yamlContent = `name: ${TEST_WORKFLOW.name}
description: ${TEST_WORKFLOW.description}

steps:
${TEST_WORKFLOW.steps.map(step => `  - id: ${step.id}
    name: ${step.name}
    mcp: ${step.mcp}
    action: ${step.action}
    params: ${JSON.stringify(step.params)}`).join('\n')}
`;

  await fs.writeFile(workflowPath, yamlContent);
  return workflowPath;
}

// 메인 테스트 함수
async function runIntegrationTest() {
  log('\n🧪 MCP 서버 통합 테스트 시작\n', 'bright');

  const results = [];

  // 1. 각 MCP 서버 테스트
  log('1️⃣  개별 MCP 서버 테스트', 'yellow');
  for (const server of MCP_SERVERS) {
    const result = await testMCPServer(server);
    results.push(result);
    
    if (result.success) {
      log(`✅ ${result.name}: 성공`, 'green');
    } else {
      log(`❌ ${result.name}: 실패 - ${result.error}`, 'red');
    }
  }

  // 2. 워크플로우 통합 테스트
  log('\n2️⃣  워크플로우 통합 테스트', 'yellow');
  try {
    const workflowPath = await createTestWorkflow();
    log(`✅ 테스트 워크플로우 생성: ${workflowPath}`, 'green');
  } catch (error) {
    log(`❌ 워크플로우 생성 실패: ${error.message}`, 'red');
  }

  // 3. 결과 요약
  log('\n📊 테스트 결과 요약', 'bright');
  const successCount = results.filter(r => r.success).length;
  const failCount = results.filter(r => !r.success).length;
  
  log(`성공: ${successCount}/${results.length}`, 'green');
  if (failCount > 0) {
    log(`실패: ${failCount}/${results.length}`, 'red');
  }

  // 4. 프로젝트 구조 확인
  log('\n📁 프로젝트 구조 확인', 'yellow');
  const mcpDirs = await fs.readdir(PROJECT_ROOT);
  const mcpServers = mcpDirs.filter(dir => dir.endsWith('-mcp-server'));
  log(`발견된 MCP 서버: ${mcpServers.length}개`, 'blue');
  mcpServers.forEach(server => {
    log(`  - ${server}`, 'blue');
  });

  log('\n✨ 통합 테스트 완료\n', 'bright');
}

// 테스트 실행
runIntegrationTest().catch(console.error);