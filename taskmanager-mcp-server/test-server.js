#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

// 최소한의 MCP 서버 구현
const server = new Server(
  {
    name: 'test-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 도구 목록 핸들러
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'hello',
        description: '인사를 합니다',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: '인사할 이름',
            },
          },
        },
      },
    ],
  };
});

// 도구 호출 핸들러
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'hello') {
    return {
      content: [
        {
          type: 'text',
          text: `안녕하세요, ${args.name || '사용자'}님!`,
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// 서버 시작
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Test MCP Server started successfully');
}

main().catch(console.error);