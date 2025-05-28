#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import dotenv from 'dotenv';
import fs from 'fs/promises';
import path from 'path';

dotenv.config();

class FigmaMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'figma-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.figmaToken = process.env.FIGMA_TOKEN || '';
    this.figmaFileKey = process.env.FIGMA_FILE_KEY || '';
    this.baseURL = 'https://api.figma.com/v1';
    
    this.setupHandlers();
  }

  setupHandlers() {
    // 도구 목록 핸들러
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'detect-design-changes',
          description: 'Figma 파일의 디자인 변경사항을 감지합니다',
          inputSchema: {
            type: 'object',
            properties: {
              fileKey: {
                type: 'string',
                description: 'Figma 파일 키 (선택사항, 환경변수 사용)',
              },
              lastChecked: {
                type: 'string',
                description: '마지막 확인 시간 (ISO 8601)',
              },
            },
          },
        },
        {
          name: 'extract-components',
          description: 'Figma 파일에서 컴포넌트 정보를 추출합니다',
          inputSchema: {
            type: 'object',
            properties: {
              fileKey: {
                type: 'string',
                description: 'Figma 파일 키 (선택사항)',
              },
            },
          },
        },
        {
          name: 'extract-design-tokens',
          description: 'Figma 파일에서 디자인 토큰을 추출합니다',
          inputSchema: {
            type: 'object',
            properties: {
              fileKey: {
                type: 'string',
                description: 'Figma 파일 키 (선택사항)',
              },
            },
          },
        },
        {
          name: 'generate-component-json',
          description: '컴포넌트 정보를 JSON으로 변환합니다',
          inputSchema: {
            type: 'object',
            properties: {
              componentId: {
                type: 'string',
                description: '컴포넌트 ID',
              },
              fileKey: {
                type: 'string',
                description: 'Figma 파일 키 (선택사항)',
              },
            },
            required: ['componentId'],
          },
        },
      ],
    }));

    // 도구 호출 핸들러
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'detect-design-changes':
          return await this.detectDesignChanges(args);
        case 'extract-components':
          return await this.extractComponents(args);
        case 'extract-design-tokens':
          return await this.extractDesignTokens(args);
        case 'generate-component-json':
          return await this.generateComponentJSON(args);
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  async detectDesignChanges({ fileKey, lastChecked }) {
    try {
      const key = fileKey || this.figmaFileKey;
      
      if (!key) {
        return this.errorResponse('Figma 파일 키가 필요합니다');
      }

      if (!this.figmaToken) {
        return this.errorResponse('Figma API 토큰이 설정되지 않았습니다. FIGMA_TOKEN 환경변수를 설정하세요.');
      }

      // Figma API로 파일 정보 가져오기
      const response = await axios.get(
        `${this.baseURL}/files/${key}`,
        {
          headers: {
            'X-Figma-Token': this.figmaToken,
          },
        }
      );

      const fileData = response.data;
      const currentModified = fileData.lastModified;
      
      // 변경사항 분석
      const hasChanges = lastChecked ? new Date(currentModified) > new Date(lastChecked) : true;
      
      // 컴포넌트 목록 가져오기
      const components = [];
      if (fileData.components) {
        Object.entries(fileData.components).forEach(([id, component]) => {
          components.push({
            id,
            name: component.name,
            description: component.description || '',
          });
        });
      }

      const changes = {
        hasChanges,
        lastModified: currentModified,
        fileName: fileData.name,
        version: fileData.version,
        componentsCount: components.length,
        components: components.slice(0, 10), // 상위 10개만
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(changes, null, 2),
          },
        ],
      };
    } catch (error) {
      if (error.response?.status === 403) {
        return this.errorResponse('Figma API 접근 권한이 없습니다. 토큰을 확인하세요.');
      }
      return this.errorResponse(`변경사항 감지 실패: ${error.message}`);
    }
  }

  async extractComponents({ fileKey }) {
    try {
      const key = fileKey || this.figmaFileKey;
      
      if (!key) {
        return this.errorResponse('Figma 파일 키가 필요합니다');
      }

      if (!this.figmaToken) {
        return this.errorResponse('Figma API 토큰이 설정되지 않았습니다');
      }

      // Figma API로 파일 정보 가져오기
      const response = await axios.get(
        `${this.baseURL}/files/${key}`,
        {
          headers: {
            'X-Figma-Token': this.figmaToken,
          },
        }
      );

      const fileData = response.data;
      const components = [];

      // 컴포넌트 정보 추출
      if (fileData.components) {
        for (const [id, component] of Object.entries(fileData.components)) {
          // 컴포넌트 노드 정보 가져오기
          const nodeResponse = await axios.get(
            `${this.baseURL}/files/${key}/nodes?ids=${id}`,
            {
              headers: {
                'X-Figma-Token': this.figmaToken,
              },
            }
          );

          const nodeData = nodeResponse.data.nodes[id];
          const document = nodeData.document;

          components.push({
            id,
            name: component.name,
            type: document.type,
            description: component.description || '',
            containingFrame: component.containing_frame || null,
            properties: {
              width: document.absoluteBoundingBox?.width,
              height: document.absoluteBoundingBox?.height,
              fills: document.fills,
              strokes: document.strokes,
              effects: document.effects,
            },
          });
        }
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(components, null, 2),
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`컴포넌트 추출 실패: ${error.message}`);
    }
  }

  async extractDesignTokens({ fileKey }) {
    try {
      const key = fileKey || this.figmaFileKey;
      
      if (!key) {
        return this.errorResponse('Figma 파일 키가 필요합니다');
      }

      if (!this.figmaToken) {
        return this.errorResponse('Figma API 토큰이 설정되지 않았습니다');
      }

      // Figma API로 스타일 정보 가져오기
      const response = await axios.get(
        `${this.baseURL}/files/${key}`,
        {
          headers: {
            'X-Figma-Token': this.figmaToken,
          },
        }
      );

      const fileData = response.data;
      const tokens = {
        colors: {},
        typography: {},
        effects: {},
      };

      // 스타일 정보 추출
      if (fileData.styles) {
        for (const [styleId, style] of Object.entries(fileData.styles)) {
          if (style.styleType === 'FILL') {
            // 색상 스타일 추출
            const nodeResponse = await axios.get(
              `${this.baseURL}/files/${key}/nodes?ids=${style.node_id}`,
              {
                headers: {
                  'X-Figma-Token': this.figmaToken,
                },
              }
            );
            
            const nodeData = nodeResponse.data.nodes[style.node_id];
            if (nodeData?.document?.fills?.[0]?.color) {
              const color = nodeData.document.fills[0].color;
              tokens.colors[style.name] = `rgba(${Math.round(color.r * 255)}, ${Math.round(color.g * 255)}, ${Math.round(color.b * 255)}, ${color.a})`;
            }
          } else if (style.styleType === 'TEXT') {
            // 텍스트 스타일 추출
            tokens.typography[style.name] = {
              styleType: 'TEXT',
              description: style.description || '',
            };
          } else if (style.styleType === 'EFFECT') {
            // 효과 스타일 추출
            tokens.effects[style.name] = {
              styleType: 'EFFECT',
              description: style.description || '',
            };
          }
        }
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(tokens, null, 2),
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`디자인 토큰 추출 실패: ${error.message}`);
    }
  }

  async generateComponentJSON({ componentId, fileKey }) {
    try {
      const key = fileKey || this.figmaFileKey;
      
      if (!key) {
        return this.errorResponse('Figma 파일 키가 필요합니다');
      }

      // 실제 구현에서는 Figma API로 컴포넌트 상세 정보 조회
      // 현재는 시뮬레이션
      const componentJSON = {
        meta: {
          id: componentId,
          name: 'Button',
          type: 'component',
          generatedAt: new Date().toISOString(),
          figmaFile: key,
        },
        component: {
          name: 'Button',
          props: {
            children: {
              type: 'ReactNode',
              required: true,
            },
            variant: {
              type: 'enum',
              values: ['primary', 'secondary', 'outline'],
              default: 'primary',
            },
            size: {
              type: 'enum',
              values: ['small', 'medium', 'large'],
              default: 'medium',
            },
            onClick: {
              type: 'function',
              required: false,
            },
            disabled: {
              type: 'boolean',
              default: false,
            },
          },
          styles: {
            base: 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2',
            variants: {
              primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
              secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-500',
              outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white focus:ring-blue-500',
            },
            sizes: {
              small: 'px-3 py-1.5 text-sm',
              medium: 'px-4 py-2 text-base',
              large: 'px-6 py-3 text-lg',
            },
            disabled: 'opacity-50 cursor-not-allowed hover:bg-current',
          },
        },
      };

      // JSON 파일 저장
      const outputPath = path.join(process.cwd(), 'figma-components', `${componentId}.json`);
      await fs.mkdir(path.dirname(outputPath), { recursive: true });
      await fs.writeFile(outputPath, JSON.stringify(componentJSON, null, 2));

      return {
        content: [
          {
            type: 'text',
            text: `컴포넌트 JSON 생성 완료: ${outputPath}\n\n${JSON.stringify(componentJSON, null, 2)}`,
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`컴포넌트 JSON 생성 실패: ${error.message}`);
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
    console.error('Figma MCP Server started successfully');
  }
}

const server = new FigmaMCPServer();
server.run().catch(console.error);