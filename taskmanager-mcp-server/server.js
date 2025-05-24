import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import yaml from 'js-yaml';
import fs from 'fs/promises';
import { spawn } from 'child_process';

const server = new Server({
  name: "taskmanager-mcp-server",
  version: "1.0.0",
}, {
  capabilities: {
    tools: {}
  }
});

// 워크플로우 실행 도구
server.setRequestHandler("tools/execute-workflow", async (request) => {
  const { workflowPath, input = {} } = request.params;
  
  try {
    console.log(`🎯 Executing workflow: ${workflowPath}`);
    
    // 워크플로우 파일 읽기
    const workflowContent = await fs.readFile(workflowPath, 'utf8');
    const workflow = yaml.load(workflowContent);
    
    console.log(`📋 Workflow loaded: ${workflow.name}`);
    
    // 작업 실행 컨텍스트
    const context = {
      input,
      results: {},
      timestamp: new Date().toISOString()
    };
    
    // 순차적으로 작업 실행 (의존성 고려한 실제 구현은 Phase 2에서)
    for (const task of workflow.tasks) {
      console.log(`⚡ Executing task: ${task.id}`);
      
      try {
        const result = await executeTask(task, context);
        context.results[task.id] = result;
        console.log(`✅ Task ${task.id} completed`);
      } catch (error) {
        console.error(`❌ Task ${task.id} failed:`, error.message);
        throw error;
      }
    }
    
    return {
      success: true,
      workflow: workflow.name,
      completedTasks: Object.keys(context.results),
      results: context.results
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      workflow: workflowPath
    };
  }
});

// 개별 작업 실행 함수
async function executeTask(task, context) {
  if (task.mcp === 'terminal-mcp') {
    // Terminal MCP 시뮬레이션 (실제로는 별도 MCP 서버 호출)
    return await executeTerminalCommand(task.params.command);
  }
  
  throw new Error(`Unknown MCP server: ${task.mcp}`);
}

// 터미널 명령어 실행
function executeTerminalCommand(command) {
  return new Promise((resolve, reject) => {
    const process = spawn('bash', ['-c', command], {
      cwd: process.cwd(),
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let stdout = '';
    let stderr = '';
    
    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    process.on('close', (code) => {
      if (code === 0) {
        resolve({
          success: true,
          output: stdout.trim(),
          exitCode: code
        });
      } else {
        reject(new Error(`Command failed with code ${code}: ${stderr}`));
      }
    });
    
    process.on('error', (error) => {
      reject(error);
    });
  });
}

// 서버 시작
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.log('🎯 TaskManager MCP Server running...');
}

main().catch(console.error);
