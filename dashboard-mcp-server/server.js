#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { WebSocketServer } from 'ws';
import dotenv from 'dotenv';

dotenv.config();

class DashboardMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'dashboard-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // 메트릭 저장소
    this.metrics = {
      workflows: {
        total: 0,
        running: 0,
        completed: 0,
        failed: 0,
      },
      components: {
        total: 0,
        generated: 0,
        updated: 0,
      },
      performance: {
        avgWorkflowTime: 0,
        successRate: 0,
        lastUpdated: new Date().toISOString(),
      },
    };

    // 알림 큐
    this.notifications = [];

    // WebSocket 서버 설정 (옵션)
    this.wsPort = process.env.WS_PORT || 3001;
    this.wss = null;

    this.setupHandlers();
  }

  setupHandlers() {
    // 도구 목록 핸들러
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'update-workflow-metrics',
          description: '워크플로우 메트릭을 업데이트합니다',
          inputSchema: {
            type: 'object',
            properties: {
              status: {
                type: 'string',
                description: '워크플로우 상태',
                enum: ['started', 'completed', 'failed'],
              },
              workflowId: {
                type: 'string',
                description: '워크플로우 ID',
              },
              duration: {
                type: 'number',
                description: '실행 시간 (초)',
              },
            },
            required: ['status', 'workflowId'],
          },
        },
        {
          name: 'update-component-metrics',
          description: '컴포넌트 메트릭을 업데이트합니다',
          inputSchema: {
            type: 'object',
            properties: {
              action: {
                type: 'string',
                description: '액션 타입',
                enum: ['generated', 'updated', 'deleted'],
              },
              componentName: {
                type: 'string',
                description: '컴포넌트 이름',
              },
              count: {
                type: 'number',
                description: '영향받은 컴포넌트 수',
                default: 1,
              },
            },
            required: ['action', 'componentName'],
          },
        },
        {
          name: 'get-dashboard-metrics',
          description: '현재 대시보드 메트릭을 조회합니다',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'send-notification',
          description: '알림을 생성하고 전송합니다',
          inputSchema: {
            type: 'object',
            properties: {
              type: {
                type: 'string',
                description: '알림 타입',
                enum: ['info', 'success', 'warning', 'error'],
              },
              title: {
                type: 'string',
                description: '알림 제목',
              },
              message: {
                type: 'string',
                description: '알림 메시지',
              },
              metadata: {
                type: 'object',
                description: '추가 메타데이터',
              },
            },
            required: ['type', 'title', 'message'],
          },
        },
        {
          name: 'get-notifications',
          description: '최근 알림을 조회합니다',
          inputSchema: {
            type: 'object',
            properties: {
              limit: {
                type: 'number',
                description: '조회할 알림 수',
                default: 10,
              },
            },
          },
        },
        {
          name: 'start-websocket-server',
          description: 'WebSocket 서버를 시작합니다',
          inputSchema: {
            type: 'object',
            properties: {
              port: {
                type: 'number',
                description: 'WebSocket 포트',
              },
            },
          },
        },
      ],
    }));

    // 도구 호출 핸들러
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'update-workflow-metrics':
          return await this.updateWorkflowMetrics(args);
        case 'update-component-metrics':
          return await this.updateComponentMetrics(args);
        case 'get-dashboard-metrics':
          return await this.getDashboardMetrics();
        case 'send-notification':
          return await this.sendNotification(args);
        case 'get-notifications':
          return await this.getNotifications(args);
        case 'start-websocket-server':
          return await this.startWebSocketServer(args);
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  async updateWorkflowMetrics({ status, workflowId, duration }) {
    try {
      if (status === 'started') {
        this.metrics.workflows.running++;
      } else if (status === 'completed') {
        this.metrics.workflows.running--;
        this.metrics.workflows.completed++;
        this.metrics.workflows.total++;

        // 평균 실행 시간 업데이트
        if (duration) {
          const totalCompleted = this.metrics.workflows.completed;
          const currentAvg = this.metrics.performance.avgWorkflowTime;
          this.metrics.performance.avgWorkflowTime = 
            (currentAvg * (totalCompleted - 1) + duration) / totalCompleted;
        }
      } else if (status === 'failed') {
        this.metrics.workflows.running--;
        this.metrics.workflows.failed++;
        this.metrics.workflows.total++;
      }

      // 성공률 계산
      if (this.metrics.workflows.total > 0) {
        this.metrics.performance.successRate = 
          (this.metrics.workflows.completed / this.metrics.workflows.total) * 100;
      }

      this.metrics.performance.lastUpdated = new Date().toISOString();

      // WebSocket으로 실시간 업데이트 전송
      this.broadcastUpdate('workflow-metrics', this.metrics.workflows);

      return {
        content: [
          {
            type: 'text',
            text: `워크플로우 메트릭 업데이트 완료: ${workflowId} (${status})`,
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`메트릭 업데이트 실패: ${error.message}`);
    }
  }

  async updateComponentMetrics({ action, componentName, count = 1 }) {
    try {
      this.metrics.components.total += count;

      if (action === 'generated') {
        this.metrics.components.generated += count;
      } else if (action === 'updated') {
        this.metrics.components.updated += count;
      }

      this.metrics.performance.lastUpdated = new Date().toISOString();

      // WebSocket으로 실시간 업데이트 전송
      this.broadcastUpdate('component-metrics', this.metrics.components);

      return {
        content: [
          {
            type: 'text',
            text: `컴포넌트 메트릭 업데이트 완료: ${componentName} (${action})`,
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`메트릭 업데이트 실패: ${error.message}`);
    }
  }

  async getDashboardMetrics() {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(this.metrics, null, 2),
        },
      ],
    };
  }

  async sendNotification({ type, title, message, metadata = {} }) {
    try {
      const notification = {
        id: Date.now().toString(),
        type,
        title,
        message,
        metadata,
        timestamp: new Date().toISOString(),
      };

      // 알림 저장 (최대 100개)
      this.notifications.unshift(notification);
      if (this.notifications.length > 100) {
        this.notifications = this.notifications.slice(0, 100);
      }

      // WebSocket으로 실시간 알림 전송
      this.broadcastUpdate('notification', notification);

      return {
        content: [
          {
            type: 'text',
            text: `알림 전송 완료: ${title}`,
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`알림 전송 실패: ${error.message}`);
    }
  }

  async getNotifications({ limit = 10 }) {
    const recentNotifications = this.notifications.slice(0, limit);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(recentNotifications, null, 2),
        },
      ],
    };
  }

  async startWebSocketServer({ port }) {
    try {
      const wsPort = port || this.wsPort;
      
      if (this.wss) {
        return {
          content: [
            {
              type: 'text',
              text: `WebSocket 서버가 이미 실행 중입니다 (포트: ${wsPort})`,
            },
          ],
        };
      }

      this.wss = new WebSocketServer({ port: wsPort });

      this.wss.on('connection', (ws) => {
        console.log('새로운 WebSocket 클라이언트 연결됨');

        // 초기 메트릭 전송
        ws.send(JSON.stringify({
          type: 'initial-metrics',
          data: this.metrics,
        }));

        ws.on('message', (message) => {
          console.log('클라이언트 메시지:', message.toString());
        });

        ws.on('close', () => {
          console.log('WebSocket 클라이언트 연결 종료');
        });
      });

      return {
        content: [
          {
            type: 'text',
            text: `WebSocket 서버 시작됨 (포트: ${wsPort})`,
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`WebSocket 서버 시작 실패: ${error.message}`);
    }
  }

  broadcastUpdate(type, data) {
    if (this.wss) {
      const message = JSON.stringify({ type, data, timestamp: new Date().toISOString() });
      
      this.wss.clients.forEach((client) => {
        if (client.readyState === 1) { // WebSocket.OPEN
          client.send(message);
        }
      });
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
    console.error('Dashboard MCP Server started successfully');
  }
}

const server = new DashboardMCPServer();
server.run().catch(console.error);