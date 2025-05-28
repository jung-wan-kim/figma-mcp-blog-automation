#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

class Context7MCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'context7-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.context7ApiKey = process.env.CONTEXT7_API_KEY;
    this.context7BaseUrl = process.env.CONTEXT7_BASE_URL || 'https://api.context7.com';
    
    this.setupHandlers();
    this.setupErrorHandling();
  }

  setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error('[Context7 MCP Server Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupHandlers() {
    // 도구 목록 핸들러
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'context7_search',
          description: 'Search for relevant context in Context7',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'Search query'
              },
              filters: {
                type: 'object',
                description: 'Optional filters for search',
                properties: {
                  type: { type: 'string' },
                  tags: { 
                    type: 'array',
                    items: { type: 'string' }
                  },
                  date_from: { type: 'string' },
                  date_to: { type: 'string' }
                }
              }
            },
            required: ['query']
          }
        },
        {
          name: 'context7_create',
          description: 'Create a new context entry in Context7',
          inputSchema: {
            type: 'object',
            properties: {
              title: {
                type: 'string',
                description: 'Title of the context'
              },
              content: {
                type: 'string',
                description: 'Content of the context'
              },
              type: {
                type: 'string',
                description: 'Type of context (e.g., note, code, reference)'
              },
              tags: {
                type: 'array',
                items: { type: 'string' },
                description: 'Tags for the context'
              },
              metadata: {
                type: 'object',
                description: 'Additional metadata'
              }
            },
            required: ['title', 'content']
          }
        },
        {
          name: 'context7_update',
          description: 'Update an existing context entry',
          inputSchema: {
            type: 'object',
            properties: {
              id: {
                type: 'string',
                description: 'Context ID to update'
              },
              updates: {
                type: 'object',
                properties: {
                  title: { type: 'string' },
                  content: { type: 'string' },
                  tags: { 
                    type: 'array',
                    items: { type: 'string' }
                  },
                  metadata: { type: 'object' }
                }
              }
            },
            required: ['id', 'updates']
          }
        },
        {
          name: 'context7_get',
          description: 'Get a specific context entry by ID',
          inputSchema: {
            type: 'object',
            properties: {
              id: {
                type: 'string',
                description: 'Context ID'
              }
            },
            required: ['id']
          }
        },
        {
          name: 'context7_delete',
          description: 'Delete a context entry',
          inputSchema: {
            type: 'object',
            properties: {
              id: {
                type: 'string',
                description: 'Context ID to delete'
              }
            },
            required: ['id']
          }
        },
        {
          name: 'context7_link',
          description: 'Create a link between two context entries',
          inputSchema: {
            type: 'object',
            properties: {
              source_id: {
                type: 'string',
                description: 'Source context ID'
              },
              target_id: {
                type: 'string',
                description: 'Target context ID'
              },
              relationship: {
                type: 'string',
                description: 'Type of relationship'
              }
            },
            required: ['source_id', 'target_id']
          }
        }
      ]
    }));

    // 도구 실행 핸들러
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'context7_search':
            return await this.searchContext(args);
          case 'context7_create':
            return await this.createContext(args);
          case 'context7_update':
            return await this.updateContext(args);
          case 'context7_get':
            return await this.getContext(args);
          case 'context7_delete':
            return await this.deleteContext(args);
          case 'context7_link':
            return await this.linkContexts(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [{
            type: 'text',
            text: `Error: ${error.message}`
          }],
          isError: true,
        };
      }
    });
  }

  async makeRequest(method, endpoint, data = null) {
    if (!this.context7ApiKey) {
      throw new Error('Context7 API key not configured. Please set CONTEXT7_API_KEY in .env file');
    }

    try {
      const config = {
        method,
        url: `${this.context7BaseUrl}${endpoint}`,
        headers: {
          'Authorization': `Bearer ${this.context7ApiKey}`,
          'Content-Type': 'application/json'
        }
      };

      if (data) {
        config.data = data;
      }

      const response = await axios(config);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(`Context7 API error: ${error.response.status} - ${error.response.data.message || error.response.statusText}`);
      }
      throw error;
    }
  }

  async searchContext({ query, filters }) {
    try {
      const searchParams = { query, ...filters };
      const results = await this.makeRequest('POST', '/api/context/search', searchParams);
      
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(results, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Error searching context: ${error.message}`
        }],
        isError: true
      };
    }
  }

  async createContext({ title, content, type = 'note', tags = [], metadata = {} }) {
    try {
      const contextData = {
        title,
        content,
        type,
        tags,
        metadata,
        created_at: new Date().toISOString()
      };

      const result = await this.makeRequest('POST', '/api/context', contextData);
      
      return {
        content: [{
          type: 'text',
          text: `Context created successfully with ID: ${result.id}`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Error creating context: ${error.message}`
        }],
        isError: true
      };
    }
  }

  async updateContext({ id, updates }) {
    try {
      const result = await this.makeRequest('PUT', `/api/context/${id}`, updates);
      
      return {
        content: [{
          type: 'text',
          text: `Context ${id} updated successfully`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Error updating context: ${error.message}`
        }],
        isError: true
      };
    }
  }

  async getContext({ id }) {
    try {
      const result = await this.makeRequest('GET', `/api/context/${id}`);
      
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Error getting context: ${error.message}`
        }],
        isError: true
      };
    }
  }

  async deleteContext({ id }) {
    try {
      await this.makeRequest('DELETE', `/api/context/${id}`);
      
      return {
        content: [{
          type: 'text',
          text: `Context ${id} deleted successfully`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Error deleting context: ${error.message}`
        }],
        isError: true
      };
    }
  }

  async linkContexts({ source_id, target_id, relationship = 'related' }) {
    try {
      const linkData = {
        source_id,
        target_id,
        relationship
      };

      await this.makeRequest('POST', '/api/context/link', linkData);
      
      return {
        content: [{
          type: 'text',
          text: `Link created between ${source_id} and ${target_id} with relationship: ${relationship}`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Error creating link: ${error.message}`
        }],
        isError: true
      };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Context7 MCP Server running on stdio');
  }
}

const server = new Context7MCPServer();
server.run().catch((error) => {
  console.error('Failed to start Context7 MCP Server:', error);
  process.exit(1);
});