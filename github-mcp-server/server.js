#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { Octokit } from '@octokit/rest';
import dotenv from 'dotenv';

dotenv.config();

class GitHubMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'github-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // GitHub API 클라이언트 초기화
    this.octokit = new Octokit({
      auth: process.env.GITHUB_TOKEN,
    });

    this.setupHandlers();
  }

  setupHandlers() {
    // 도구 목록 핸들러
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'create-branch',
          description: 'GitHub 저장소에 새 브랜치를 생성합니다',
          inputSchema: {
            type: 'object',
            properties: {
              repository: {
                type: 'string',
                description: '저장소 이름 (owner/repo)',
              },
              branchName: {
                type: 'string',
                description: '생성할 브랜치 이름',
              },
              baseBranch: {
                type: 'string',
                description: '기준 브랜치 (기본값: main)',
                default: 'main',
              },
            },
            required: ['repository', 'branchName'],
          },
        },
        {
          name: 'create-pull-request',
          description: 'Pull Request를 생성합니다',
          inputSchema: {
            type: 'object',
            properties: {
              repository: {
                type: 'string',
                description: '저장소 이름 (owner/repo)',
              },
              title: {
                type: 'string',
                description: 'PR 제목',
              },
              description: {
                type: 'string',
                description: 'PR 설명',
              },
              head: {
                type: 'string',
                description: '소스 브랜치',
              },
              base: {
                type: 'string',
                description: '대상 브랜치 (기본값: main)',
                default: 'main',
              },
              reviewers: {
                type: 'array',
                items: { type: 'string' },
                description: '리뷰어 목록',
              },
              labels: {
                type: 'array',
                items: { type: 'string' },
                description: '라벨 목록',
              },
            },
            required: ['repository', 'title', 'head'],
          },
        },
        {
          name: 'commit-files',
          description: '파일을 커밋합니다',
          inputSchema: {
            type: 'object',
            properties: {
              repository: {
                type: 'string',
                description: '저장소 이름 (owner/repo)',
              },
              branch: {
                type: 'string',
                description: '커밋할 브랜치',
              },
              files: {
                type: 'array',
                description: '커밋할 파일 목록',
                items: {
                  type: 'object',
                  properties: {
                    path: { type: 'string' },
                    content: { type: 'string' },
                  },
                  required: ['path', 'content'],
                },
              },
              message: {
                type: 'string',
                description: '커밋 메시지',
              },
            },
            required: ['repository', 'branch', 'files', 'message'],
          },
        },
        {
          name: 'get-repository-info',
          description: '저장소 정보를 조회합니다',
          inputSchema: {
            type: 'object',
            properties: {
              repository: {
                type: 'string',
                description: '저장소 이름 (owner/repo)',
              },
            },
            required: ['repository'],
          },
        },
      ],
    }));

    // 도구 호출 핸들러
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'create-branch':
          return await this.createBranch(args);
        case 'create-pull-request':
          return await this.createPullRequest(args);
        case 'commit-files':
          return await this.commitFiles(args);
        case 'get-repository-info':
          return await this.getRepositoryInfo(args);
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  async createBranch({ repository, branchName, baseBranch = 'main' }) {
    try {
      const [owner, repo] = repository.split('/');
      console.log(`🌿 Creating branch: ${branchName} from ${baseBranch}`);

      // 베이스 브랜치의 최신 커밋 SHA 가져오기
      const { data: baseRef } = await this.octokit.rest.git.getRef({
        owner,
        repo,
        ref: `heads/${baseBranch}`,
      });

      // 새 브랜치 생성
      const { data: newBranch } = await this.octokit.rest.git.createRef({
        owner,
        repo,
        ref: `refs/heads/${branchName}`,
        sha: baseRef.object.sha,
      });

      return {
        content: [
          {
            type: 'text',
            text: `브랜치 생성 성공: ${branchName}\nURL: https://github.com/${repository}/tree/${branchName}`,
          },
        ],
      };
    } catch (error) {
      console.error('❌ Branch creation failed:', error.message);
      return this.errorResponse(`브랜치 생성 실패: ${error.message}`);
    }
  }

  async createPullRequest({
    repository,
    title,
    description = '',
    head,
    base = 'main',
    reviewers = [],
    labels = [],
  }) {
    try {
      const [owner, repo] = repository.split('/');
      console.log(`📝 Creating PR: ${title}`);

      // Pull Request 생성
      const { data: pr } = await this.octokit.rest.pulls.create({
        owner,
        repo,
        title,
        body: description,
        head,
        base,
      });

      // 리뷰어 할당
      if (reviewers.length > 0) {
        await this.octokit.rest.pulls.requestReviewers({
          owner,
          repo,
          pull_number: pr.number,
          reviewers,
        });
      }

      // 라벨 추가
      if (labels.length > 0) {
        await this.octokit.rest.issues.addLabels({
          owner,
          repo,
          issue_number: pr.number,
          labels,
        });
      }

      return {
        content: [
          {
            type: 'text',
            text: `Pull Request 생성 성공\n\nPR #${pr.number}: ${title}\nURL: ${pr.html_url}`,
          },
        ],
      };
    } catch (error) {
      console.error('❌ PR creation failed:', error.message);
      return this.errorResponse(`PR 생성 실패: ${error.message}`);
    }
  }

  async commitFiles({ repository, branch, files, message }) {
    try {
      const [owner, repo] = repository.split('/');
      console.log(`💾 Committing ${files.length} files to ${branch}`);

      // 현재 브랜치의 최신 커밋 정보 가져오기
      const { data: currentBranch } = await this.octokit.rest.repos.getBranch({
        owner,
        repo,
        branch,
      });

      // 각 파일에 대해 블롭 생성
      const blobs = await Promise.all(
        files.map(async (file) => {
          const { data: blob } = await this.octokit.rest.git.createBlob({
            owner,
            repo,
            content: Buffer.from(file.content).toString('base64'),
            encoding: 'base64',
          });
          return {
            path: file.path,
            mode: '100644',
            type: 'blob',
            sha: blob.sha,
          };
        })
      );

      // 새 트리 생성
      const { data: newTree } = await this.octokit.rest.git.createTree({
        owner,
        repo,
        base_tree: currentBranch.commit.commit.tree.sha,
        tree: blobs,
      });

      // 새 커밋 생성
      const { data: newCommit } = await this.octokit.rest.git.createCommit({
        owner,
        repo,
        message,
        tree: newTree.sha,
        parents: [currentBranch.commit.sha],
      });

      // 브랜치 참조 업데이트
      await this.octokit.rest.git.updateRef({
        owner,
        repo,
        ref: `heads/${branch}`,
        sha: newCommit.sha,
      });

      return {
        content: [
          {
            type: 'text',
            text: `커밋 성공\n\n커밋 SHA: ${newCommit.sha}\n커밋 메시지: ${message}\n파일 수: ${files.length}`,
          },
        ],
      };
    } catch (error) {
      console.error('❌ File commit failed:', error.message);
      return this.errorResponse(`파일 커밋 실패: ${error.message}`);
    }
  }

  async getRepositoryInfo({ repository }) {
    try {
      const [owner, repo] = repository.split('/');

      const { data: repoInfo } = await this.octokit.rest.repos.get({
        owner,
        repo,
      });

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(
              {
                name: repoInfo.name,
                fullName: repoInfo.full_name,
                defaultBranch: repoInfo.default_branch,
                url: repoInfo.html_url,
                private: repoInfo.private,
                description: repoInfo.description,
              },
              null,
              2
            ),
          },
        ],
      };
    } catch (error) {
      return this.errorResponse(`저장소 정보 조회 실패: ${error.message}`);
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
    console.error('GitHub MCP Server started successfully');
  }
}

const server = new GitHubMCPServer();
server.run().catch(console.error);
