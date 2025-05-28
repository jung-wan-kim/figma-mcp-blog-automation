#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import yaml from 'js-yaml';
import fs from 'fs/promises';
import path from 'path';

class TaskManagerMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'taskmanager-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.workflowStates = new Map();
    this.setupHandlers();
  }

  setupHandlers() {
    // 워크플로우 실행 핸들러
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'execute-workflow',
          description: '워크플로우 파일을 실행합니다',
          inputSchema: {
            type: 'object',
            properties: {
              workflowPath: {
                type: 'string',
                description: '워크플로우 YAML 파일 경로',
              },
              input: {
                type: 'object',
                description: '워크플로우 입력 파라미터',
              },
            },
            required: ['workflowPath'],
          },
        },
        {
          name: 'get-workflow-status',
          description: '워크플로우 실행 상태를 조회합니다',
          inputSchema: {
            type: 'object',
            properties: {
              workflowId: {
                type: 'string',
                description: '워크플로우 ID',
              },
            },
            required: ['workflowId'],
          },
        },
        {
          name: 'list-workflows',
          description: '사용 가능한 워크플로우 목록을 조회합니다',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
      ],
    }));

    // 워크플로우 실행
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'execute-workflow':
          return await this.executeWorkflow(args);
        case 'get-workflow-status':
          return await this.getWorkflowStatus(args);
        case 'list-workflows':
          return await this.listWorkflows();
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  async executeWorkflow({ workflowPath, input = {} }) {
    try {
      console.log(`🎯 Executing workflow: ${workflowPath}`);

      // 워크플로우 파일 읽기
      const workflowContent = await fs.readFile(workflowPath, 'utf8');
      const workflow = yaml.load(workflowContent);

      console.log(`📋 Workflow loaded: ${workflow.name}`);

      // 작업 실행 컨텍스트
      const context = {
        workflowId: Date.now().toString(),
        input,
        results: {},
        timestamp: new Date().toISOString(),
      };

      // 워크플로우 상태 저장
      this.workflowStates.set(context.workflowId, {
        status: 'running',
        workflow: workflow.name,
        startTime: context.timestamp,
        steps: [],
      });

      // 단계별 실행
      for (const step of workflow.steps) {
        console.log(`⚡ Executing step: ${step.name}`);

        try {
          // MCP 서버 호출 시뮬레이션
          const result = await this.executeMCPAction(step, context);

          context.results[step.id] = result;

          this.workflowStates.get(context.workflowId).steps.push({
            name: step.name,
            status: 'completed',
            result: result,
          });

          console.log(`✅ Step completed: ${step.name}`);
        } catch (stepError) {
          console.error(`❌ Step failed: ${step.name}`, stepError);

          this.workflowStates.get(context.workflowId).steps.push({
            name: step.name,
            status: 'failed',
            error: stepError.message,
          });

          if (!step.continueOnError) {
            throw stepError;
          }
        }
      }

      // 워크플로우 완료
      const state = this.workflowStates.get(context.workflowId);
      state.status = 'completed';
      state.endTime = new Date().toISOString();

      return {
        content: [
          {
            type: 'text',
            text: `Workflow '${workflow.name}' completed successfully with ${workflow.steps.length} steps`,
          },
        ],
      };
    } catch (error) {
      console.error('Workflow execution failed:', error);
      return {
        content: [
          {
            type: 'text',
            text: `Workflow execution failed: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  async getWorkflowStatus({ workflowId }) {
    const state = this.workflowStates.get(workflowId);

    if (!state) {
      return {
        content: [
          {
            type: 'text',
            text: `Workflow ${workflowId} not found`,
          },
        ],
        isError: true,
      };
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(
            {
              workflowId,
              ...state,
            },
            null,
            2
          ),
        },
      ],
    };
  }

  async listWorkflows() {
    const workflowDir = path.join(process.cwd(), 'workflows');

    try {
      const files = await fs.readdir(workflowDir);
      const workflows = [];

      for (const file of files) {
        if (file.endsWith('.yaml') || file.endsWith('.yml')) {
          const content = await fs.readFile(
            path.join(workflowDir, file),
            'utf8'
          );
          const workflow = yaml.load(content);

          workflows.push({
            file,
            name: workflow.name,
            description: workflow.description,
            steps: workflow.steps.length,
          });
        }
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(workflows, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Failed to list workflows: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  async executeMCPAction(step, context) {
    const { mcp, action, params = {} } = step;

    // 실제 구현에서는 각 MCP 서버와 통신
    // 현재는 시뮬레이션

    switch (mcp) {
      case 'figma-mcp':
        return this.simulateFigmaMCP(action, params);

      case 'github-mcp':
        return this.simulateGitHubMCP(action, params);

      case 'nextjs-mcp':
        return this.simulateNextJSMCP(action, params);

      default:
        throw new Error(`Unknown MCP server: ${mcp}`);
    }
  }

  simulateFigmaMCP(action, params) {
    switch (action) {
      case 'detect-changes':
        return {
          changes: ['Button component updated', 'Color tokens changed'],
          timestamp: new Date().toISOString(),
        };

      case 'extract-components':
        return {
          components: [
            { name: 'Button', type: 'component' },
            { name: 'Card', type: 'component' },
          ],
        };

      default:
        return { simulated: true, action, params };
    }
  }

  simulateGitHubMCP(action, params) {
    switch (action) {
      case 'create-branch':
        return {
          branch: params.branchName || 'feature/auto-update',
          created: true,
        };

      case 'create-pr':
        return {
          pr: {
            number: 123,
            title: params.title || 'Auto-generated updates',
            url: 'https://github.com/example/repo/pull/123',
          },
        };

      default:
        return { simulated: true, action, params };
    }
  }

  simulateNextJSMCP(action, params) {
    switch (action) {
      case 'generate-components':
        return {
          generated: ['Button.tsx', 'Card.tsx'],
          path: 'src/components/generated',
        };

      case 'update-styles':
        return {
          updated: ['globals.css', 'tailwind.config.js'],
        };

      default:
        return { simulated: true, action, params };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('TaskManager MCP Server started');
  }
}

const server = new TaskManagerMCPServer();
server.run().catch(console.error);