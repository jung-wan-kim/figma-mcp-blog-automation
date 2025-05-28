#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

class SupabaseMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'supabase-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Supabase 클라이언트 초기화
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_ANON_KEY;

    if (supabaseUrl && supabaseKey) {
      this.supabase = createClient(supabaseUrl, supabaseKey);
    } else {
      console.warn('Supabase 자격 증명이 없습니다. 시뮬레이션 모드로 실행됩니다.');
      this.supabase = null;
    }

    this.setupHandlers();
  }

  setupHandlers() {
    // 도구 목록 핸들러
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'save-workflow-state',
          description: '워크플로우 실행 상태를 저장합니다',
          inputSchema: {
            type: 'object',
            properties: {
              workflowId: {
                type: 'string',
                description: '워크플로우 ID',
              },
              status: {
                type: 'string',
                description: '상태 (running, completed, failed)',
                enum: ['running', 'completed', 'failed'],
              },
              metadata: {
                type: 'object',
                description: '추가 메타데이터',
              },
            },
            required: ['workflowId', 'status'],
          },
        },
        {
          name: 'get-workflow-history',
          description: '워크플로우 실행 이력을 조회합니다',
          inputSchema: {
            type: 'object',
            properties: {
              limit: {
                type: 'number',
                description: '조회할 항목 수 (기본값: 10)',
                default: 10,
              },
              status: {
                type: 'string',
                description: '필터링할 상태',
                enum: ['running', 'completed', 'failed'],
              },
            },
          },
        },
        {
          name: 'save-component-metadata',
          description: '컴포넌트 메타데이터를 저장합니다',
          inputSchema: {
            type: 'object',
            properties: {
              componentId: {
                type: 'string',
                description: '컴포넌트 ID',
              },
              name: {
                type: 'string',
                description: '컴포넌트 이름',
              },
              figmaData: {
                type: 'object',
                description: 'Figma 관련 데이터',
              },
              generatedFiles: {
                type: 'array',
                items: { type: 'string' },
                description: '생성된 파일 목록',
              },
            },
            required: ['componentId', 'name'],
          },
        },
        {
          name: 'get-component-metadata',
          description: '컴포넌트 메타데이터를 조회합니다',
          inputSchema: {
            type: 'object',
            properties: {
              componentId: {
                type: 'string',
                description: '컴포넌트 ID',
              },
            },
            required: ['componentId'],
          },
        },
        {
          name: 'save-design-tokens',
          description: '디자인 토큰을 저장합니다',
          inputSchema: {
            type: 'object',
            properties: {
              tokens: {
                type: 'object',
                description: '디자인 토큰 객체',
              },
              version: {
                type: 'string',
                description: '버전 정보',
              },
            },
            required: ['tokens'],
          },
        },
      ],
    }));

    // 도구 호출 핸들러
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'save-workflow-state':
          return await this.saveWorkflowState(args);
        case 'get-workflow-history':
          return await this.getWorkflowHistory(args);
        case 'save-component-metadata':
          return await this.saveComponentMetadata(args);
        case 'get-component-metadata':
          return await this.getComponentMetadata(args);
        case 'save-design-tokens':
          return await this.saveDesignTokens(args);
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  async saveWorkflowState({ workflowId, status, metadata = {} }) {
    try {
      if (this.supabase) {
        // 실제 Supabase 저장
        const { data, error } = await this.supabase
          .from('workflow_states')
          .insert({
            workflow_id: workflowId,
            status,
            metadata,
            created_at: new Date().toISOString(),
          });

        if (error) throw error;

        return {
          content: [
            {
              type: 'text',
              text: `워크플로우 상태 저장 완료: ${workflowId} (${status})`,
            },
          ],
        };
      } else {
        // 시뮬레이션 모드
        console.log('Simulating workflow state save:', { workflowId, status, metadata });
        return {
          content: [
            {
              type: 'text',
              text: `[시뮬레이션] 워크플로우 상태 저장: ${workflowId} (${status})`,
            },
          ],
        };
      }
    } catch (error) {
      return this.errorResponse(`워크플로우 상태 저장 실패: ${error.message}`);
    }
  }

  async getWorkflowHistory({ limit = 10, status }) {
    try {
      if (this.supabase) {
        // 실제 Supabase 조회
        let query = this.supabase
          .from('workflow_states')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(limit);

        if (status) {
          query = query.eq('status', status);
        }

        const { data, error } = await query;

        if (error) throw error;

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(data, null, 2),
            },
          ],
        };
      } else {
        // 시뮬레이션 모드
        const mockHistory = [
          {
            workflow_id: 'wf_001',
            status: 'completed',
            created_at: '2025-05-28T10:00:00Z',
            metadata: { duration: '45s', steps: 5 },
          },
          {
            workflow_id: 'wf_002',
            status: 'failed',
            created_at: '2025-05-28T09:30:00Z',
            metadata: { error: 'GitHub API rate limit', steps: 3 },
          },
        ];

        return {
          content: [
            {
              type: 'text',
              text: `[시뮬레이션] 워크플로우 이력:\n${JSON.stringify(mockHistory, null, 2)}`,
            },
          ],
        };
      }
    } catch (error) {
      return this.errorResponse(`워크플로우 이력 조회 실패: ${error.message}`);
    }
  }

  async saveComponentMetadata({ componentId, name, figmaData = {}, generatedFiles = [] }) {
    try {
      const metadata = {
        component_id: componentId,
        name,
        figma_data: figmaData,
        generated_files: generatedFiles,
        updated_at: new Date().toISOString(),
      };

      if (this.supabase) {
        // 실제 Supabase 저장 (upsert)
        const { data, error } = await this.supabase
          .from('component_metadata')
          .upsert(metadata, { onConflict: 'component_id' });

        if (error) throw error;

        return {
          content: [
            {
              type: 'text',
              text: `컴포넌트 메타데이터 저장 완료: ${name} (${componentId})`,
            },
          ],
        };
      } else {
        // 시뮬레이션 모드
        console.log('Simulating component metadata save:', metadata);
        return {
          content: [
            {
              type: 'text',
              text: `[시뮬레이션] 컴포넌트 메타데이터 저장: ${name} (${componentId})`,
            },
          ],
        };
      }
    } catch (error) {
      return this.errorResponse(`컴포넌트 메타데이터 저장 실패: ${error.message}`);
    }
  }

  async getComponentMetadata({ componentId }) {
    try {
      if (this.supabase) {
        // 실제 Supabase 조회
        const { data, error } = await this.supabase
          .from('component_metadata')
          .select('*')
          .eq('component_id', componentId)
          .single();

        if (error) throw error;

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(data, null, 2),
            },
          ],
        };
      } else {
        // 시뮬레이션 모드
        const mockData = {
          component_id: componentId,
          name: 'Button',
          figma_data: {
            nodeId: 'comp_001',
            lastModified: '2025-05-28T08:00:00Z',
          },
          generated_files: [
            'src/components/generated/Button.tsx',
            'src/components/generated/Button.test.tsx',
          ],
          updated_at: '2025-05-28T10:00:00Z',
        };

        return {
          content: [
            {
              type: 'text',
              text: `[시뮬레이션] 컴포넌트 메타데이터:\n${JSON.stringify(mockData, null, 2)}`,
            },
          ],
        };
      }
    } catch (error) {
      return this.errorResponse(`컴포넌트 메타데이터 조회 실패: ${error.message}`);
    }
  }

  async saveDesignTokens({ tokens, version = '1.0.0' }) {
    try {
      const tokenData = {
        tokens,
        version,
        created_at: new Date().toISOString(),
      };

      if (this.supabase) {
        // 실제 Supabase 저장
        const { data, error } = await this.supabase
          .from('design_tokens')
          .insert(tokenData);

        if (error) throw error;

        return {
          content: [
            {
              type: 'text',
              text: `디자인 토큰 저장 완료 (버전: ${version})`,
            },
          ],
        };
      } else {
        // 시뮬레이션 모드
        console.log('Simulating design tokens save:', tokenData);
        return {
          content: [
            {
              type: 'text',
              text: `[시뮬레이션] 디자인 토큰 저장 완료 (버전: ${version})`,
            },
          ],
        };
      }
    } catch (error) {
      return this.errorResponse(`디자인 토큰 저장 실패: ${error.message}`);
    }
  }

  errorResponse(message) {
    return {
      content: [
        {
          type: 'text',
          text: `오류: ${message}`,
        },
      ],
      isError: true,
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Supabase MCP Server started successfully');
  }
}

const server = new SupabaseMCPServer();
server.run().catch(console.error);