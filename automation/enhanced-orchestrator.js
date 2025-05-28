#!/usr/bin/env node

/**
 * Enhanced Master Orchestrator - 실제 MCP 서버와 통신
 * 
 * Figma → TaskManager → GitHub → Supabase → Dashboard 완전 자동화
 */

import { MCPClientManager } from './mcp-client.js';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class EnhancedMasterOrchestrator {
  constructor() {
    this.clientManager = new MCPClientManager();
    this.workflowState = {
      currentStep: null,
      results: {},
      startTime: null,
      endTime: null
    };
  }

  async initialize() {
    console.log('🎯 Initializing Enhanced Master Orchestrator...');
    
    try {
      // 각 MCP 서버 연결
      await this.clientManager.connectClient(
        'taskmanager',
        join(__dirname, '../taskmanager-mcp-server/server.js')
      );
      
      await this.clientManager.connectClient(
        'figma',
        join(__dirname, '../figma-mcp-server/server.js')
      );
      
      await this.clientManager.connectClient(
        'github',
        join(__dirname, '../github-mcp-server/server.js')
      );
      
      await this.clientManager.connectClient(
        'supabase',
        join(__dirname, '../supabase-mcp-server/server.js')
      );
      
      await this.clientManager.connectClient(
        'dashboard',
        join(__dirname, '../dashboard-mcp-server/server.js')
      );
      
      console.log('✅ All MCP servers connected successfully');
      return true;
    } catch (error) {
      console.error('❌ Failed to initialize:', error.message);
      return false;
    }
  }

  async executeCompleteWorkflow(figmaFileKey, options = {}) {
    console.log('\n🚀 Starting Complete Automation Workflow');
    console.log(`📋 Figma File: ${figmaFileKey}`);
    
    this.workflowState.startTime = new Date();
    const workflowId = `wf_${Date.now()}`;

    try {
      // Dashboard에 워크플로우 시작 알림
      await this.updateDashboard('workflow-started', { workflowId });

      // 1. Figma 변경사항 감지
      console.log('\n📊 Step 1: Detecting Figma Changes...');
      const figmaChanges = await this.detectFigmaChanges(figmaFileKey);
      this.workflowState.results.figma = figmaChanges;

      // 2. 컴포넌트 추출 및 JSON 생성
      console.log('\n🎨 Step 2: Extracting Components...');
      const components = await this.extractComponents(figmaFileKey);
      this.workflowState.results.components = components;

      // 3. React 컴포넌트 생성
      console.log('\n⚡ Step 3: Generating React Components...');
      const generatedFiles = await this.generateReactComponents(components);
      this.workflowState.results.generatedFiles = generatedFiles;

      // 4. GitHub 브랜치 생성 및 커밋
      console.log('\n🌿 Step 4: Creating GitHub Branch...');
      const githubBranch = await this.createGitHubBranch(workflowId);
      this.workflowState.results.branch = githubBranch;

      console.log('\n💾 Step 5: Committing Files...');
      const commitResult = await this.commitFiles(githubBranch, generatedFiles);
      this.workflowState.results.commit = commitResult;

      // 5. Pull Request 생성
      console.log('\n📝 Step 6: Creating Pull Request...');
      const prResult = await this.createPullRequest(githubBranch, figmaChanges);
      this.workflowState.results.pullRequest = prResult;

      // 6. Supabase에 메타데이터 저장
      console.log('\n💾 Step 7: Saving Metadata...');
      await this.saveMetadata(workflowId, components);

      // 7. Dashboard 업데이트 및 알림
      console.log('\n📱 Step 8: Sending Notifications...');
      await this.sendNotifications(workflowId, prResult);

      this.workflowState.endTime = new Date();
      const duration = (this.workflowState.endTime - this.workflowState.startTime) / 1000;

      console.log('\n✅ Workflow Completed Successfully!');
      console.log(`⏱️  Total Duration: ${duration}s`);
      console.log(`📊 Results:`, JSON.stringify(this.workflowState.results, null, 2));

      return {
        success: true,
        workflowId,
        duration,
        results: this.workflowState.results
      };

    } catch (error) {
      console.error('\n❌ Workflow Failed:', error.message);
      await this.handleError(workflowId, error);
      
      return {
        success: false,
        workflowId,
        error: error.message
      };
    }
  }

  async detectFigmaChanges(fileKey) {
    const figmaClient = this.clientManager.getClient('figma');
    
    const result = await figmaClient.callTool('detect-design-changes', {
      fileKey,
      lastChecked: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
    });

    // Parse result
    const changes = JSON.parse(result.content[0].text);
    return changes;
  }

  async extractComponents(fileKey) {
    const figmaClient = this.clientManager.getClient('figma');
    
    const result = await figmaClient.callTool('extract-components', {
      fileKey
    });

    return JSON.parse(result.content[0].text);
  }

  async generateReactComponents(components) {
    // 실제로는 TaskManager를 통해 워크플로우 실행
    // 여기서는 간단한 구현
    const files = [];
    
    for (const component of components) {
      const componentCode = this.generateComponentCode(component);
      const filePath = `src/components/generated/${component.name}.tsx`;
      
      // 실제 파일 생성
      const fullPath = join(__dirname, '..', filePath);
      await fs.mkdir(dirname(fullPath), { recursive: true });
      await fs.writeFile(fullPath, componentCode);
      
      files.push({
        path: filePath,
        content: componentCode
      });
    }

    // index.ts 생성
    const indexContent = components
      .map(c => `export { ${c.name} } from './${c.name}';`)
      .join('\n');
    
    const indexPath = 'src/components/generated/index.ts';
    await fs.writeFile(join(__dirname, '..', indexPath), indexContent);
    
    files.push({
      path: indexPath,
      content: indexContent
    });

    return files;
  }

  generateComponentCode(component) {
    // 간단한 컴포넌트 템플릿
    return `import React from 'react';

interface ${component.name}Props {
  children?: React.ReactNode;
  className?: string;
}

/**
 * ${component.name} component
 * Auto-generated from Figma
 * ${component.description || ''}
 */
export const ${component.name}: React.FC<${component.name}Props> = ({ 
  children,
  className = ''
}) => {
  return (
    <div className={\`\${className}\`}>
      {children}
    </div>
  );
};

export default ${component.name};`;
  }

  async createGitHubBranch(workflowId) {
    const githubClient = this.clientManager.getClient('github');
    
    const branchName = `feature/figma-sync-${workflowId}`;
    const result = await githubClient.callTool('create-branch', {
      repository: process.env.GITHUB_REPOSITORY || 'owner/repo',
      branchName,
      baseBranch: 'main'
    });

    return branchName;
  }

  async commitFiles(branch, files) {
    const githubClient = this.clientManager.getClient('github');
    
    const result = await githubClient.callTool('commit-files', {
      repository: process.env.GITHUB_REPOSITORY || 'owner/repo',
      branch,
      files,
      message: '🎨 Auto-sync: Update components from Figma'
    });

    return JSON.parse(result.content[0].text);
  }

  async createPullRequest(branch, figmaChanges) {
    const githubClient = this.clientManager.getClient('github');
    
    const description = `## 🎨 Figma Design Sync

This PR automatically syncs the latest design changes from Figma.

### Changes
${figmaChanges.summary ? figmaChanges.summary.map(s => `- ${s}`).join('\n') : '- Component updates'}

### Components Updated
${figmaChanges.components ? figmaChanges.components.map(c => `- ${c.name}`).join('\n') : '- Various components'}

---
*This PR was automatically generated by the Figma-to-Code automation system.*`;

    const result = await githubClient.callTool('create-pull-request', {
      repository: process.env.GITHUB_REPOSITORY || 'owner/repo',
      title: '🎨 Design System Update from Figma',
      description,
      head: branch,
      base: 'main',
      labels: ['figma-sync', 'automated']
    });

    return JSON.parse(result.content[0].text);
  }

  async saveMetadata(workflowId, components) {
    const supabaseClient = this.clientManager.getClient('supabase');
    
    // 워크플로우 상태 저장
    await supabaseClient.callTool('save-workflow-state', {
      workflowId,
      status: 'completed',
      metadata: {
        componentsCount: components.length,
        timestamp: new Date().toISOString()
      }
    });

    // 각 컴포넌트 메타데이터 저장
    for (const component of components) {
      await supabaseClient.callTool('save-component-metadata', {
        componentId: component.id,
        name: component.name,
        figmaData: component,
        generatedFiles: [`src/components/generated/${component.name}.tsx`]
      });
    }
  }

  async updateDashboard(event, data) {
    const dashboardClient = this.clientManager.getClient('dashboard');
    
    switch (event) {
      case 'workflow-started':
        await dashboardClient.callTool('update-workflow-metrics', {
          status: 'started',
          workflowId: data.workflowId
        });
        break;
        
      case 'workflow-completed':
        await dashboardClient.callTool('update-workflow-metrics', {
          status: 'completed',
          workflowId: data.workflowId,
          duration: data.duration
        });
        break;
    }
  }

  async sendNotifications(workflowId, prResult) {
    const dashboardClient = this.clientManager.getClient('dashboard');
    
    await dashboardClient.callTool('send-notification', {
      type: 'success',
      title: '🎨 Figma Sync Complete',
      message: `Design changes have been synced. PR #${prResult.prNumber} is ready for review.`,
      metadata: {
        workflowId,
        prUrl: prResult.prUrl
      }
    });
  }

  async handleError(workflowId, error) {
    const dashboardClient = this.clientManager.getClient('dashboard');
    
    // Dashboard에 에러 알림
    await dashboardClient.callTool('update-workflow-metrics', {
      status: 'failed',
      workflowId
    });

    await dashboardClient.callTool('send-notification', {
      type: 'error',
      title: '❌ Workflow Failed',
      message: error.message,
      metadata: { workflowId }
    });

    // Supabase에 실패 상태 저장
    const supabaseClient = this.clientManager.getClient('supabase');
    await supabaseClient.callTool('save-workflow-state', {
      workflowId,
      status: 'failed',
      metadata: {
        error: error.message,
        timestamp: new Date().toISOString()
      }
    });
  }

  async cleanup() {
    console.log('\n🧹 Cleaning up...');
    await this.clientManager.disconnectAll();
    console.log('✅ Cleanup complete');
  }
}

// CLI 실행
async function main() {
  const orchestrator = new EnhancedMasterOrchestrator();
  
  const initialized = await orchestrator.initialize();
  if (!initialized) {
    console.error('Failed to initialize orchestrator');
    process.exit(1);
  }

  const figmaFileKey = process.argv[2] || process.env.FIGMA_FILE_KEY;
  
  if (!figmaFileKey) {
    console.error('❌ Please provide a Figma file key');
    console.log('Usage: node enhanced-orchestrator.js <figma-file-key>');
    process.exit(1);
  }

  try {
    const result = await orchestrator.executeCompleteWorkflow(figmaFileKey);
    
    if (result.success) {
      console.log('\n🎉 SUCCESS! Automation completed.');
    } else {
      console.log('\n❌ FAILED! Check logs for details.');
    }
  } finally {
    await orchestrator.cleanup();
  }
}

// 직접 실행시
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { EnhancedMasterOrchestrator };