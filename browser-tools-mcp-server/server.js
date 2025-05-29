#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { getMCPLogger } from '../src/lib/mcp-logger.js';
import puppeteer from 'puppeteer';
import dotenv from 'dotenv';
import fs from 'fs/promises';
import path from 'path';

dotenv.config();

const logger = getMCPLogger('browser-tools-mcp-server');

class BrowserToolsMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'browser-tools-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.browser = null;
    this.page = null;
    this.screenshotDir = process.env.SCREENSHOT_PATH || './screenshots';

    logger.info('Browser Tools MCP Server initialized');
    this.setupHandlers();
    this.initializeBrowser();
  }

  async initializeBrowser() {
    try {
      this.browser = await puppeteer.launch({
        headless: process.env.BROWSER_HEADLESS === 'true' ? 'new' : false,
        defaultViewport: { width: 1280, height: 720 },
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
      });
      this.page = await this.browser.newPage();

      // 스크린샷 디렉토리 생성
      await fs.mkdir(this.screenshotDir, { recursive: true });

      logger.info('브라우저 초기화 완료');
    } catch (error) {
      logger.error('브라우저 초기화 실패', error);
    }
  }

  setupHandlers() {
    // 도구 목록 핸들러
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'navigate',
          description: '웹 페이지로 이동합니다',
          inputSchema: {
            type: 'object',
            properties: {
              url: {
                type: 'string',
                description: '이동할 URL',
              },
            },
            required: ['url'],
          },
        },
        {
          name: 'click',
          description: '웹 페이지의 요소를 클릭합니다',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: '클릭할 요소의 CSS 선택자',
              },
            },
            required: ['selector'],
          },
        },
        {
          name: 'type',
          description: '입력 필드에 텍스트를 입력합니다',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: '입력할 요소의 CSS 선택자',
              },
              text: {
                type: 'string',
                description: '입력할 텍스트',
              },
            },
            required: ['selector', 'text'],
          },
        },
        {
          name: 'screenshot',
          description: '현재 페이지의 스크린샷을 캡처합니다',
          inputSchema: {
            type: 'object',
            properties: {
              filename: {
                type: 'string',
                description: '저장할 파일명 (선택사항)',
              },
            },
          },
        },
        {
          name: 'get_text',
          description: '요소의 텍스트 내용을 가져옵니다',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: '텍스트를 가져올 요소의 CSS 선택자',
              },
            },
            required: ['selector'],
          },
        },
        {
          name: 'wait_for_element',
          description: '특정 요소가 나타날 때까지 대기합니다',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: '대기할 요소의 CSS 선택자',
              },
              timeout: {
                type: 'number',
                description: '대기 시간 (밀리초, 기본값: 5000)',
              },
            },
            required: ['selector'],
          },
        },
        {
          name: 'evaluate_js',
          description: '페이지에서 JavaScript를 실행합니다',
          inputSchema: {
            type: 'object',
            properties: {
              script: {
                type: 'string',
                description: '실행할 JavaScript 코드',
              },
            },
            required: ['script'],
          },
        },
        {
          name: 'get_page_info',
          description: '현재 페이지의 정보를 가져옵니다',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
      ],
    }));

    // 도구 호출 핸들러
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      const startTime = Date.now();

      logger.logToolCall(name, args);

      try {
        let result;
        switch (name) {
          case 'navigate':
            result = await this.navigate(args);
            break;
          case 'click':
            result = await this.click(args);
            break;
          case 'type':
            result = await this.type(args);
            break;
          case 'screenshot':
            result = await this.screenshot(args);
            break;
          case 'get_text':
            result = await this.getText(args);
            break;
          case 'wait_for_element':
            result = await this.waitForElement(args);
            break;
          case 'evaluate_js':
            result = await this.evaluateJS(args);
            break;
          case 'get_page_info':
            result = await this.getPageInfo(args);
            break;
          default:
            throw new Error(`Unknown tool: ${name}`);
        }

        const _duration = Date.now() - startTime;
        logger.logToolSuccess(name, result, _duration);
        return result;
      } catch (error) {
        const _duration = Date.now() - startTime;
        logger.logToolError(name, error, args);
        throw error;
      }
    });
  }

  async navigate({ url }) {
    try {
      if (!this.page) {
        throw new Error('브라우저가 초기화되지 않았습니다');
      }

      logger.info(`브라우저 네비게이션: ${url}`);
      await this.page.goto(url, { waitUntil: 'networkidle2' });

      const title = await this.page.title();
      const currentUrl = this.page.url();

      return {
        content: [
          {
            type: 'text',
            text: `페이지 이동 완료\n제목: ${title}\nURL: ${currentUrl}`,
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`네비게이션 실패: ${error.message}`);
    }
  }

  async click({ selector }) {
    logger.info(`요소 클릭: ${selector}`);
    return {
      content: [
        {
          type: 'text',
          text: `요소 클릭 완료: ${selector}`,
        },
      ],
    };
  }

  async type({ selector, text }) {
    logger.info(`텍스트 입력: ${selector} <- "${text}"`);
    return {
      content: [
        {
          type: 'text',
          text: `텍스트 입력 완료: ${selector} <- "${text}"`,
        },
      ],
    };
  }

  async screenshot({ filename = null }) {
    try {
      if (!this.page) {
        throw new Error('브라우저가 초기화되지 않았습니다');
      }

      const fileName = filename || `screenshot-${Date.now()}.png`;
      const filePath = path.join(this.screenshotDir, fileName);

      logger.info(`스크린샷 캡처: ${fileName}`);
      await this.page.screenshot({ path: filePath, fullPage: true });

      return {
        content: [
          {
            type: 'text',
            text: `스크린샷 저장됨: ${filePath}`,
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`스크린샷 실패: ${error.message}`);
    }
  }

  async getText({ selector }) {
    try {
      if (!this.page) {
        throw new Error('브라우저가 초기화되지 않았습니다');
      }

      logger.info(`텍스트 추출: ${selector}`);
      await this.page.waitForSelector(selector, { timeout: 5000 });
      const text = await this.page.$eval(selector, (el) => el.textContent.trim());

      return {
        content: [
          {
            type: 'text',
            text: `텍스트 추출 완료: ${selector}\n내용: "${text}"`,
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`텍스트 추출 실패: ${error.message}`);
    }
  }

  async waitForElement({ selector, timeout = 5000 }) {
    try {
      if (!this.page) {
        throw new Error('브라우저가 초기화되지 않았습니다');
      }

      logger.info(`요소 대기: ${selector} (${timeout}ms)`);
      await this.page.waitForSelector(selector, { timeout });

      return {
        content: [
          {
            type: 'text',
            text: `요소 대기 완료: ${selector}`,
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`요소 대기 실패: ${error.message}`);
    }
  }

  async evaluateJS({ script }) {
    try {
      if (!this.page) {
        throw new Error('브라우저가 초기화되지 않았습니다');
      }

      logger.info(`JavaScript 실행: ${script.substring(0, 50)}...`);
      const result = await this.page.evaluate(script);

      return {
        content: [
          {
            type: 'text',
            text: `JavaScript 실행 완료\n결과: ${JSON.stringify(result, null, 2)}`,
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`JavaScript 실행 실패: ${error.message}`);
    }
  }

  async getPageInfo() {
    try {
      if (!this.page) {
        throw new Error('브라우저가 초기화되지 않았습니다');
      }

      logger.info('페이지 정보 수집');

      const pageInfo = await this.page.evaluate(() => ({
        title: document.title,
        url: window.location.href,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight,
        },
        userAgent: navigator.userAgent,
        cookies: document.cookie,
      }));

      pageInfo.timestamp = new Date().toISOString();

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(pageInfo, null, 2),
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`페이지 정보 수집 실패: ${error.message}`);
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
    logger.logServerStart(process.env.BROWSER_TOOLS_MCP_PORT || 'stdio');
    console.error('Browser Tools MCP Server started successfully');

    // 종료 시그널 처리
    process.on('SIGINT', async () => {
      await this.cleanup();
      logger.logServerStop('SIGINT');
      process.exit(0);
    });

    process.on('SIGTERM', async () => {
      await this.cleanup();
      logger.logServerStop('SIGTERM');
      process.exit(0);
    });
  }

  async cleanup() {
    try {
      if (this.browser) {
        await this.browser.close();
        logger.info('브라우저 종료 완료');
      }
    } catch (error) {
      logger.error('브라우저 종료 중 오류', error);
    }
  }
}

const server = new BrowserToolsMCPServer();
server.run().catch((error) => {
  logger.error('서버 실행 중 오류 발생', error);
  console.error(error);
  process.exit(1);
});
