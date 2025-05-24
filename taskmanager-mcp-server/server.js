import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import yaml from 'js-yaml';
import fs from 'fs/promises';
import { spawn } from 'child_process';

const server = new Server({
  name: "taskmanager-mcp-server",
  version: "1.0.0",
}, {
  capabilities: {
    tools: {}
  }
});

// 워크플로우 실행 도구
server.setRequestHandler("tools/execute-workflow", async (request) => {
  const { workflowPath, input = {} } = request.params;
  
  try {
    console.log(`🎯 Executing workflow: ${workflowPath}`);
    
    // 워크플로우 파일 읽기
    const workflowContent = await fs.readFile(workflowPath, 'utf8');
    const workflow = yaml.load(workflowContent);
    
    console.log(`📋 Workflow loaded: ${workflow.name}`);
    
    // 작업 실행 컨텍스트
    const context = {
      input,
      results: {},
      timestamp: new Date().toISOString()
    };
  import { Server } from '@modelcontextprotocol/??mport { StdioServerTransport } from '@modelcontextprotocol/sdk/sef import yaml from 'js-yaml';
import fs from 'fs/promises';
import { spawn } from   import fs from 'fs/promiseltimport { spawn } from 'childon
const server = new Server({
  name: d]   name: "taskmanager-mcp-slo  version: "1.0.0",
}, {
  capab`)}, {
  capabilitierr  c {    tools: {}
  .e  }
});

// sk}){t
/k.iserver.setRequestHandler("tools    const { workflowPath, input = {} } = request.params;
  
  try {
        
  try {
    console.log(`🎯 Executing workflow: je t.    coon    
    // 워크플로우 파일 읽기
    const workflotc   er    const workflowContent = await ffa    const workflow = yaml.load(workflowContent);
    
    console.l;
    
    console.log(`📋 Workflow loaded: ${wun   on    
    // 작업 실행 컨텍스트
    const context l-   ')    const context = {
      inpu?     input,
      r??      resul?     timestamp: ur    };
  import { Server } from '@modelcms  impanimport fs from 'fs/promises';
import { spawn } from   import fs from 'fs/promiseltimport { spawn } from 'childon
const server = new Server({
  netimport { spawn } from   impojeconst server = new Server({
  name: d]   name: "taskmanager-mcp-slo  version: "1.cw  name: d]   name: "taskma '}, {
  capab`)}, {
  capabilitierr  c {    tools: {}
  .est  cr   capabiliti    .e  }
});

// sk}){t
/k.iserve) });

/  
/ st/k.iservda  
  try {
        
  try {
    console.log(`🎯 Executing workflow: je t.    coon    
  .t St      ;
  try {
     co      // 워크플로우 파일 읽기
    const workflotc        const workflotc   er    const wue    
    console.l;
    
    console.log(`📋 Workflow loaded: ${wun   on    
    // 작업 실행 컨텍?o   Co    
    conswi   co    // 작업 실행 컨텍스트
    const context ro    const context l-   ')    con        inpu?     input,
      r??      resul??      r??      resul?()  import { Server } from '@modelcms  impanimpot(import { spawn } from   import fs from 'fs/promiseltimport { spawn } fMCconst server = new Server({
  netimport { spawn } from   imecho "# Figma MCP Test Project - Phase 1" > README.md && echo "" >> README.md && echo "Terminal MCP를 활용한 기본 Git 자동화 테스트" >> README.md
echo "Testing Phase 1 workflow steps manually..."
# Step 1: Mock Figma data extraction
echo "📥 Step 1: Extracting Figma data..."
echo '{"components": [{"name": "Button", "props": ["variant", "size"]}], "tokens": {"colors": {"primary": "#3b82f6"}}}' > /tmp/figma-data.json
echo "✅ Figma data created at /tmp/figma-data.json"
# Step 2: Generate React components
echo "⚡ Step 2: Generating React components..."
mkdir -p src/components/generated

cat > src/components/generated/Button.tsx << 'EOF'
import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
}

/**
 * Auto-generated Button component from Figma
 * Generated at: $(date)
 * TaskManager MCP Pipeline
 */
export const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  onClick 
}) => {
  const baseClasses = 'px-4 py-2 rounded font-medium transition-colors focus:outline-none focus:ring-2';
  const variantClasses = variant === 'primary' 
    ? 'bg-blue-500 hover:bg-blue-600 text-white focus:ring-blue-300'
    : 'bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-300';
  const sizeClasses = {
    small: 'text-sm px-3 py-1',
    medium: 'text-base px-4 py-2', 
    large: 'text-lg px-6 py-3'
  }[size];
  
  retecho "⚡ Step 2: Generating React={mkdir -p src/components/generated

cat > src/com`}
cat > src/components/generated/   import React from 'react';

interface ButtonPropsor
interface ButtonProps {
on'  children: React.Reacne  variant?: 'primary' | 'seac  size?: 'small' | 'medi# Step 3: Add changes to Git
echo "📝 Step 3: Adding changes to Git..."
git add .
git status
# Step 4: Commit changes
echo "💾 Step 4: Committing changes..."
git commit -m "🎨 Auto-generated components from Figma

Generated Components:
- Button.tsx (with variant and size props)  
- index.ts (component exports)

Design Tokens Applied:
- Primary color: #3b82f6
- Hover states and transitions
- Focus states for accessibility

Infrastructure:
- TaskManager MCP Server setup
- Basic workflow definition
- Terminal MCP integration

Generated by: TaskManager MCP Pipeline
Phase: 1 (Basic Git Integration)

[auto-commit]"
echo "🎉 Phase 1 Completed Successfully && echo "" && git log --oneline && echo "" && echo "📁 Project Structure:" && find . -type f -name "*.tsx" -o -name "*.ts" -o -name "*.yaml" -o -name "*.js" | head -10
mkdir -p github-mcp-server && cd github-mcp-server
cat > package.json << 'EOF'
{
  "name": "github-mcp-server",
  "version": "1.0.0",
  "description": "GitHub integration MCP Server",
  "main": "server.js",
  "type": "module",
  "scripts": {
    "start": "node server.js",
    "dev": "node --watch server.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "@octokit/rest": "^20.0.0",
    "dotenv": "^16.3.0"
  }
}
