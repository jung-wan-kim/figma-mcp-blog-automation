#!/usr/bin/env node
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🧪 Testing Context7 MCP Server...\n');

const serverPath = join(__dirname, 'server.js');
const server = spawn('node', [serverPath], {
  stdio: ['pipe', 'pipe', 'inherit']
});

server.stdout.on('data', (data) => {
  console.log('Server output:', data.toString());
});

// Test tool listing
setTimeout(() => {
  console.log('\n📋 Testing ListTools request...');
  const listToolsRequest = {
    jsonrpc: '2.0',
    method: 'tools/list',
    id: 1
  };
  
  server.stdin.write(JSON.stringify(listToolsRequest) + '\n');
}, 1000);

// Test context7_search
setTimeout(() => {
  console.log('\n🔍 Testing context7_search...');
  const searchRequest = {
    jsonrpc: '2.0',
    method: 'tools/call',
    params: {
      name: 'context7_search',
      arguments: {
        query: 'test search',
        filters: {
          type: 'note',
          tags: ['test']
        }
      }
    },
    id: 2
  };
  
  server.stdin.write(JSON.stringify(searchRequest) + '\n');
}, 2000);

// Test context7_create
setTimeout(() => {
  console.log('\n➕ Testing context7_create...');
  const createRequest = {
    jsonrpc: '2.0',
    method: 'tools/call',
    params: {
      name: 'context7_create',
      arguments: {
        title: 'Test Context',
        content: 'This is a test context entry',
        type: 'note',
        tags: ['test', 'example'],
        metadata: {
          source: 'test-server'
        }
      }
    },
    id: 3
  };
  
  server.stdin.write(JSON.stringify(createRequest) + '\n');
}, 3000);

// Cleanup
setTimeout(() => {
  console.log('\n✅ All tests completed!');
  server.kill();
  process.exit(0);
}, 4000);

server.on('error', (error) => {
  console.error('❌ Server error:', error);
  process.exit(1);
});