#!/usr/bin/env node

/**
 * MCP Client - 실제 MCP 서버와 통신하는 클라이언트
 * 각 MCP 서버와 stdio를 통해 통신
 */

import { spawn } from 'child_process';
import { EventEmitter } from 'events';

export class MCPClient extends EventEmitter {
  constructor(serverPath, serverName) {
    super();
    this.serverPath = serverPath;
    this.serverName = serverName;
    this.process = null;
    this.messageId = 0;
    this.pendingRequests = new Map();
    this.isConnected = false;
  }

  async connect() {
    console.log(`🔌 Connecting to ${this.serverName} MCP server...`);
    
    this.process = spawn('node', [this.serverPath], {
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env }
    });

    this.process.stdout.on('data', (data) => {
      const lines = data.toString().split('\n').filter(line => line.trim());
      for (const line of lines) {
        try {
          const message = JSON.parse(line);
          this.handleMessage(message);
        } catch (e) {
          // JSON이 아닌 로그 메시지는 무시
        }
      }
    });

    this.process.stderr.on('data', (data) => {
      console.error(`[${this.serverName}] ${data.toString()}`);
    });

    this.process.on('close', (code) => {
      console.log(`[${this.serverName}] Process exited with code ${code}`);
      this.isConnected = false;
      this.emit('disconnected');
    });

    // 초기화 메시지 전송
    await this.sendMessage({
      jsonrpc: '2.0',
      method: 'initialize',
      params: {
        protocolVersion: '1.0.0',
        capabilities: {},
        clientInfo: {
          name: 'master-orchestrator',
          version: '1.0.0'
        }
      },
      id: this.getNextId()
    });

    this.isConnected = true;
    console.log(`✅ Connected to ${this.serverName}`);
    return true;
  }

  async disconnect() {
    if (this.process) {
      this.process.kill();
      this.process = null;
      this.isConnected = false;
    }
  }

  async callTool(toolName, params) {
    if (!this.isConnected) {
      throw new Error(`Not connected to ${this.serverName}`);
    }

    const id = this.getNextId();
    const request = {
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: params
      },
      id
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });
      this.sendMessage(request);
      
      // 타임아웃 설정
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error(`Request timeout for ${toolName}`));
        }
      }, 30000);
    });
  }

  async listTools() {
    const id = this.getNextId();
    const request = {
      jsonrpc: '2.0',
      method: 'tools/list',
      params: {},
      id
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });
      this.sendMessage(request);
    });
  }

  sendMessage(message) {
    if (this.process && this.process.stdin.writable) {
      this.process.stdin.write(JSON.stringify(message) + '\n');
    }
  }

  handleMessage(message) {
    if (message.id && this.pendingRequests.has(message.id)) {
      const { resolve, reject } = this.pendingRequests.get(message.id);
      this.pendingRequests.delete(message.id);

      if (message.error) {
        reject(new Error(message.error.message));
      } else {
        resolve(message.result);
      }
    } else if (message.method) {
      // 서버에서 온 알림 처리
      this.emit('notification', message);
    }
  }

  getNextId() {
    return ++this.messageId;
  }
}

// MCP 클라이언트 매니저
export class MCPClientManager {
  constructor() {
    this.clients = new Map();
  }

  async connectClient(name, serverPath) {
    const client = new MCPClient(serverPath, name);
    await client.connect();
    this.clients.set(name, client);
    return client;
  }

  getClient(name) {
    return this.clients.get(name);
  }

  async disconnectAll() {
    for (const client of this.clients.values()) {
      await client.disconnect();
    }
    this.clients.clear();
  }
}