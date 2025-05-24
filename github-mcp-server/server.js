import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { Octokit } from '@octokit/rest';
import dotenv from 'dotenv';

dotenv.config();

const server = new Server({
  name: "github-mcp-server",
  version: "1.0.0",
}, {
  capabilities: {
    tools: {}
  }
});

// GitHub API 클라이언트 초기화
const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN || 'demo_token'
});

// 브랜치 생성 도구
server.setRequestHandler("tools/create-branch", async (request) => {
  const { repository, branchName, baseBranch = 'main' } = request.params;
  
  try {
    const [owner, repo] = repository.split('/');
    console.log(`🌿 Creating branch: ${branchName} from ${baseBranch}`);
    
    // 베이스 브랜치의 최신 커밋 SHA 가져오기
    const { data: baseRef } = await octokit.rest.git.getRef({
      owner,
      repo,
      ref: `heads/${baseBranch}`
    });
    
    // 새 브랜치 생성
    const { data: newBranch } = await octokit.rest.git.createRef({
      owner,
      repo,
      ref: `refs/heads/${branchName}`,
      sha: baseRef.object.sha
    });
    
    return {
      success: true,
      branchName,
      sha: newBranch.object.sha,
      url: `https://github.com/${repository}/tree/${branchName}`
    };
  } catch (error) {
    console.error('❌ Branch creation failed:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
});

// Pull Request 생성 도구
server.setRequestHandler("tools/create-pull-request", async (request) => {
  const { 
    repository, 
    title, 
    description, 
    head, 
    base = 'main',
    reviewers = [],
    labels = []
  } = request.params;
  
  try {
    const [owner, repo] = repository.split('/');
    console.log(`📝 Creating PR: ${title}`);
    
    // Pull Request 생성
    const { data: pr } = await octokit.rest.pulls.create({
      owner,
      repo,
      title,
      body: description,
      head,
      base
    });
    
    // 리뷰어 할당
    if (reviewers.length > 0) {
      await octokit.rest.pulls.requestReviewers({
        owner,
        repo,
        pull_number: pr.number,
        reviewers
      });
    }
    
    // 라벨 추가
    if (labels.length > 0) {
      await octokit.rest.issues.addLabels({
        owner,
        repo,
        issue_number: pr.number,
        labels
      });
    }
    
    return {
      success: true,
      prNumber: pr.number,
      prUrl: pr.html_url,
      prId: pr.id
    };
  } catch (error) {
    console.error('❌ PR creation failed:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
});

// 파일 업로드 및 커밋 도구
server.setRequestHandler("tools/commit-files", async (request) => {
  const { repository, branch, files, message } = request.params;
  
  try {
    const [owner, repo] = repository.split('/');
    console.log(`💾 Committing ${files.length} files to ${branch}`);
    
    // 현재 브랜치의 최신 커밋 정보 가져오기
    const { data: currentBranch } = await octokit.rest.repos.getBranch({
      owner,
      repo,
      branch
    });
    
    // 각 파일에 대해 블롭 생성
    const blobs = await Promise.all(
      files.map(async (file) => {
        const { data: blob } = await octokit.rest.git.createBlob({
          owner,
          repo,
          content: Buffer.from(file.content).toString('base64'),
          encoding: 'base64'
        });
        return {
          path: file.path,
          mode: '100644',
          type: 'blob',
          sha: blob.sha
        };
      })
    );
    
    // 새 트리 생성
    const { data: newTree } = await octokit.rest.git.createTree({
      owner,
      repo,
      base_tree: currentBranch.commit.commit.tree.sha,
      tree: blobs
    });
    
    // 새 커밋 생성
    const { data: newCommit } = await octokit.rest.git.createCommit({
      owner,
      repo,
      message,
      tree: newTree.sha,
      parents: [currentBranch.commit.sha]
    });
    
    // 브랜치 참조 업데이트
    await octokit.rest.git.updateRef({
      owner,
      repo,
      ref: `heads/${branch}`,
      sha: newCommit.sha
    });
    
    return {
      success: true,
      commitSha: newCommit.sha,
      commitUrl: newCommit.html_url
    };
  } catch (error) {
    console.error('❌ File commit failed:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
});

// 저장소 정보 조회 도구
server.setRequestHandler("tools/get-repository-info", async (request) => {
  const { repository } = request.params;
  
  try {
    const [owner, repo] = repository.split('/');
    
    const { data: repoInfo } = await octokit.rest.repos.get({
      owner,
      repo
    });
    
    return {
      success: true,
      name: repoInfo.name,
      fullName: repoInfo.full_name,
      defaultBranch: repoInfo.default_branch,
      url: repoInfo.html_url,
      private: repoInfo.private
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
});

// 서버 시작
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.log('🐙 GitHub MCP Server running...');
}

main().catch(console.error);
