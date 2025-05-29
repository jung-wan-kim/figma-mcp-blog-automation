#!/usr/bin/env node

/**
 * Project Initializer - 프로젝트 초기화 방식 선택
 * 
 * 사용자가 다음 중 하나를 선택할 수 있습니다:
 * 1. Figma 파일 연동으로 시작
 * 2. Markdown 파일 기반으로 시작
 * 3. 템플릿에서 시작
 */

import readline from 'readline';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class ProjectInitializer {
  constructor() {
    this.projectRoot = path.resolve(__dirname, '../..');
    this.initMethods = {
      figma: new FigmaInitializer(),
      markdown: new MarkdownInitializer(),
      template: new TemplateInitializer()
    };
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async question(query) {
    return new Promise((resolve) => {
      this.rl.question(query, resolve);
    });
  }

  async select(message, choices) {
    console.log(message);
    choices.forEach((choice, index) => {
      console.log(`${index + 1}. ${choice.name || choice}`);
    });
    
    while (true) {
      const answer = await this.question('\n선택하세요 (번호 입력): ');
      const index = parseInt(answer) - 1;
      
      if (index >= 0 && index < choices.length) {
        return choices[index].value || choices[index];
      }
      console.log('올바른 번호를 입력해주세요.');
    }
  }

  async confirm(message, defaultValue = true) {
    const answer = await this.question(`${message} (${defaultValue ? 'Y/n' : 'y/N'}): `);
    if (answer.toLowerCase() === '') return defaultValue;
    return answer.toLowerCase().startsWith('y');
  }

  closeInterface() {
    this.rl.close();
  }

  async start() {
    console.log('🎯 Vibe 프로젝트 초기화');
    console.log('===================\n');

    const initMethod = await this.select('프로젝트를 어떻게 시작하시겠습니까?', [
      {
        name: '🎨 Figma 파일에서 시작 (디자인 시스템 자동 추출)',
        value: 'figma'
      },
      {
        name: '📝 Markdown 파일에서 시작 (문서 기반 컴포넌트 정의)',
        value: 'markdown'
      },
      {
        name: '📋 템플릿에서 시작 (미리 정의된 컴포넌트 세트)',
        value: 'template'
      }
    ]);

    console.log(`\n선택하신 방법: ${this.getMethodName(initMethod)}\n`);

    try {
      const result = await this.initMethods[initMethod].initialize();
      await this.generateProjectStructure(result);
      
      console.log('\n🎉 프로젝트 초기화 완료!');
      console.log('\n📁 생성된 파일들:');
      await this.showGeneratedFiles();
      
      console.log('\n🚀 다음 단계:');
      console.log('1. npm run dev - 개발 서버 시작');
      console.log('2. npm run dashboard:server - 대시보드 시작');
      console.log('3. npm run test:integration - 통합 테스트');
      
    } catch (error) {
      console.error('\n❌ 초기화 실패:', error.message);
      process.exit(1);
    } finally {
      this.closeInterface();
    }
  }

  getMethodName(method) {
    const names = {
      figma: '🎨 Figma 연동',
      markdown: '📝 Markdown 기반',
      template: '📋 템플릿 기반'
    };
    return names[method];
  }

  async generateProjectStructure(config) {
    console.log('📦 프로젝트 구조 생성 중...');
    
    // 컴포넌트 생성
    await this.generateComponents(config.components);
    
    // 스타일 생성
    if (config.styles) {
      await this.generateStyles(config.styles);
    }
    
    // 워크플로우 설정
    if (config.workflows) {
      await this.generateWorkflows(config.workflows);
    }
    
    // 환경 설정
    await this.updateEnvConfig(config.env);
  }

  async generateComponents(components) {
    const componentsDir = path.join(this.projectRoot, 'src/components/generated');
    await fs.mkdir(componentsDir, { recursive: true });

    for (const component of components) {
      await this.createComponentFile(component, componentsDir);
    }

    // index.ts 생성
    const indexContent = components
      .map(c => `export { ${c.name} } from './${c.name}';`)
      .join('\n');
    
    await fs.writeFile(
      path.join(componentsDir, 'index.ts'),
      indexContent
    );
  }

  async createComponentFile(component, dir) {
    const filePath = path.join(dir, `${component.name}.tsx`);
    const content = this.generateComponentCode(component);
    await fs.writeFile(filePath, content);
  }

  generateComponentCode(component) {
    const { name, props, description, variants } = component;
    
    // Props interface 생성
    const propsInterface = this.generatePropsInterface(name, props);
    
    // Variant classes 생성
    const variantClasses = variants ? this.generateVariantClasses(variants) : '';
    
    return `import React from 'react';

${propsInterface}

/**
 * ${name} component
 * ${description || `${name} 컴포넌트`}
 * 
 * @generated 자동 생성된 컴포넌트
 */
export const ${name}: React.FC<${name}Props> = ({ 
  children,
  className = '',
  ${props.map(p => p.name + (p.optional ? '' : '')).join(',\n  ')}
}) => {
  ${variantClasses}
  
  return (
    <div className={\`\${className}\`}>
      {children}
    </div>
  );
};

export default ${name};`;
  }

  generatePropsInterface(name, props) {
    const propsStr = props.map(prop => {
      const optional = prop.optional ? '?' : '';
      const type = this.getTypeScriptType(prop.type, prop.options);
      const description = prop.description ? `\n  /** ${prop.description} */` : '';
      
      return `${description}\n  ${prop.name}${optional}: ${type};`;
    }).join('');

    return `interface ${name}Props {
  children?: React.ReactNode;
  className?: string;${propsStr}
}`;
  }

  getTypeScriptType(type, options) {
    switch (type) {
      case 'enum':
        return options ? `'${options.join("' | '")}'` : 'string';
      case 'boolean':
        return 'boolean';
      case 'number':
        return 'number';
      case 'function':
        return '() => void';
      default:
        return 'string';
    }
  }

  generateVariantClasses(variants) {
    if (!variants || variants.length === 0) return '';
    
    return `const variantClasses = {
    ${variants.map(v => `${v.name}: '${v.classes}'`).join(',\n    ')}
  };`;
  }

  async generateStyles(styles) {
    const stylesPath = path.join(this.projectRoot, 'src/styles/generated.css');
    await fs.writeFile(stylesPath, styles);
  }

  async generateWorkflows(workflows) {
    const workflowsDir = path.join(this.projectRoot, 'workflows');
    await fs.mkdir(workflowsDir, { recursive: true });

    for (const workflow of workflows) {
      const filePath = path.join(workflowsDir, `${workflow.name}.yaml`);
      await fs.writeFile(filePath, workflow.content);
    }
  }

  async updateEnvConfig(envConfig) {
    if (!envConfig) return;

    const envPath = path.join(this.projectRoot, '.env');
    const envContent = Object.entries(envConfig)
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');
    
    await fs.writeFile(envPath, envContent);
  }

  async showGeneratedFiles() {
    const generatedDir = path.join(this.projectRoot, 'src/components/generated');
    try {
      const files = await fs.readdir(generatedDir);
      files.forEach(file => {
        console.log(`  ✅ src/components/generated/${file}`);
      });
    } catch (error) {
      console.log('  📁 생성된 파일이 없습니다.');
    }
  }
}

// Figma 초기화 클래스
class FigmaInitializer {
  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async question(query) {
    return new Promise((resolve) => {
      this.rl.question(query, resolve);
    });
  }

  async confirm(message, defaultValue = true) {
    const answer = await this.question(`${message} (${defaultValue ? 'Y/n' : 'y/N'}): `);
    if (answer.toLowerCase() === '') return defaultValue;
    return answer.toLowerCase().startsWith('y');
  }

  async initialize() {
    console.log('🎨 Figma 연동 초기화 시작\n');

    let figmaFileKey;
    while (!figmaFileKey) {
      figmaFileKey = await this.question('Figma 파일 키를 입력하세요: ');
      if (!figmaFileKey) {
        console.log('Figma 파일 키는 필수입니다.');
      }
    }

    let figmaToken;
    while (!figmaToken) {
      figmaToken = await this.question('Figma Personal Access Token을 입력하세요: ');
      if (!figmaToken) {
        console.log('Figma 토큰은 필수입니다.');
      }
    }

    const autoSync = await this.confirm('자동 동기화를 활성화하시겠습니까?', true);

    const answers = { figmaFileKey, figmaToken, autoSync };
    this.rl.close();

    console.log('\n🔍 Figma 파일 분석 중...');
    
    // Figma API 호출 시뮬레이션
    await this.delay(2000);
    
    const figmaData = await this.analyzeFigmaFile(answers.figmaFileKey, answers.figmaToken);
    
    console.log(`✅ ${figmaData.components.length}개 컴포넌트 발견`);
    console.log(`✅ ${Object.keys(figmaData.tokens.colors).length}개 색상 토큰 발견`);
    
    return {
      source: 'figma',
      components: figmaData.components,
      styles: figmaData.styles,
      workflows: this.generateFigmaWorkflows(),
      env: {
        FIGMA_FILE_KEY: answers.figmaFileKey,
        FIGMA_TOKEN: answers.figmaToken,
        AUTO_SYNC: answers.autoSync
      }
    };
  }

  async analyzeFigmaFile(fileKey, token) {
    // 실제 구현에서는 Figma API 호출
    // 현재는 모의 데이터 반환
    return {
      components: [
        {
          name: 'Button',
          description: 'Figma에서 추출된 버튼 컴포넌트',
          props: [
            { name: 'variant', type: 'enum', options: ['primary', 'secondary', 'outline'], optional: true },
            { name: 'size', type: 'enum', options: ['small', 'medium', 'large'], optional: true },
            { name: 'onClick', type: 'function', optional: true },
            { name: 'disabled', type: 'boolean', optional: true }
          ],
          variants: [
            { name: 'primary', classes: 'bg-blue-600 text-white hover:bg-blue-700' },
            { name: 'secondary', classes: 'bg-gray-200 text-gray-800 hover:bg-gray-300' }
          ]
        },
        {
          name: 'Card',
          description: 'Figma에서 추출된 카드 컴포넌트',
          props: [
            { name: 'elevation', type: 'enum', options: ['none', 'low', 'medium', 'high'], optional: true },
            { name: 'padding', type: 'enum', options: ['none', 'small', 'medium', 'large'], optional: true }
          ],
          variants: [
            { name: 'elevated', classes: 'shadow-lg' },
            { name: 'flat', classes: 'border border-gray-200' }
          ]
        }
      ],
      tokens: {
        colors: {
          primary: '#3b82f6',
          secondary: '#6b7280',
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444'
        }
      },
      styles: `/* Figma에서 추출된 스타일 */
.figma-primary { color: #3b82f6; }
.figma-secondary { color: #6b7280; }
/* 더 많은 스타일... */`
    };
  }

  generateFigmaWorkflows() {
    return [
      {
        name: 'figma-sync',
        content: `name: "Figma 동기화"
description: "Figma 파일 변경사항을 자동으로 동기화"

trigger:
  schedule: "0 */6 * * *"  # 6시간마다
  webhook: true

steps:
  - id: detect_changes
    name: "변경사항 감지"
    mcp: figma-mcp
    action: detect-design-changes
    
  - id: extract_components
    name: "컴포넌트 추출"
    mcp: figma-mcp
    action: extract-components
    
  - id: generate_code
    name: "코드 생성"
    mcp: nextjs-mcp
    action: generate-components
    
  - id: create_pr
    name: "PR 생성"
    mcp: github-mcp
    action: create-pull-request`
      }
    ];
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Markdown 초기화 클래스
class MarkdownInitializer {
  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async question(query) {
    return new Promise((resolve) => {
      this.rl.question(query, resolve);
    });
  }

  async select(message, choices) {
    console.log(message);
    choices.forEach((choice, index) => {
      console.log(`${index + 1}. ${choice.name || choice}`);
    });
    
    while (true) {
      const answer = await this.question('\n선택하세요 (번호 입력): ');
      const index = parseInt(answer) - 1;
      
      if (index >= 0 && index < choices.length) {
        return choices[index].value || choices[index];
      }
      console.log('올바른 번호를 입력해주세요.');
    }
  }

  async initialize() {
    console.log('📝 Markdown 기반 초기화 시작\n');

    let markdownPath;
    while (!markdownPath) {
      const input = await this.question('Markdown 파일 경로를 입력하세요 (기본값: ./docs/components.md): ');
      markdownPath = input || './docs/components.md';
      
      try {
        await fs.access(markdownPath);
      } catch {
        console.log('Markdown 파일을 찾을 수 없습니다. 다시 입력해주세요.');
        markdownPath = null;
      }
    }

    const format = await this.select('Markdown 파일 형식을 선택하세요:', [
      { name: '표준 컴포넌트 명세 (권장)', value: 'standard' },
      { name: 'Storybook 스타일', value: 'storybook' },
      { name: 'JSON-like 형식', value: 'json' }
    ]);

    const answers = { markdownPath, format };
    this.rl.close();

    console.log('\n📖 Markdown 파일 분석 중...');
    
    const markdownData = await this.parseMarkdownFile(answers.markdownPath, answers.format);
    
    console.log(`✅ ${markdownData.components.length}개 컴포넌트 정의 발견`);
    
    return {
      source: 'markdown',
      components: markdownData.components,
      workflows: this.generateMarkdownWorkflows(),
      env: {
        COMPONENT_SPEC_PATH: answers.markdownPath,
        SPEC_FORMAT: answers.format
      }
    };
  }

  async parseMarkdownFile(filePath, format) {
    const content = await fs.readFile(filePath, 'utf8');
    
    // 간단한 파싱 로직 (실제로는 더 정교한 파서 필요)
    const components = this.extractComponentsFromMarkdown(content, format);
    
    return { components };
  }

  extractComponentsFromMarkdown(content, format) {
    // 예시 파싱 로직
    const components = [];
    
    if (format === 'standard') {
      // ## ComponentName 형식으로 파싱
      const componentBlocks = content.split(/^## /m).filter(block => block.trim());
      
      componentBlocks.forEach(block => {
        const lines = block.split('\n');
        const name = lines[0].trim();
        
        if (name && name !== 'Components') {
          components.push({
            name,
            description: this.extractDescription(block),
            props: this.extractProps(block),
            variants: this.extractVariants(block)
          });
        }
      });
    }
    
    // 기본 컴포넌트 (파싱 실패시)
    if (components.length === 0) {
      components.push(
        {
          name: 'Button',
          description: 'Markdown에서 정의된 버튼 컴포넌트',
          props: [
            { name: 'variant', type: 'enum', options: ['primary', 'secondary'], optional: true },
            { name: 'size', type: 'enum', options: ['small', 'medium', 'large'], optional: true }
          ]
        },
        {
          name: 'Card',
          description: 'Markdown에서 정의된 카드 컴포넌트',
          props: [
            { name: 'padding', type: 'enum', options: ['small', 'medium', 'large'], optional: true }
          ]
        }
      );
    }
    
    return components;
  }

  extractDescription(block) {
    const descMatch = block.match(/^(.+?)$/m);
    return descMatch ? descMatch[1] : '';
  }

  extractProps(block) {
    const props = [];
    const propMatches = block.match(/\*\*(.+?)\*\*.*?:.*?`(.+?)`/g);
    
    if (propMatches) {
      propMatches.forEach(match => {
        const [, name, type] = match.match(/\*\*(.+?)\*\*.*?:.*?`(.+?)`/);
        props.push({
          name: name.toLowerCase(),
          type: type.includes('|') ? 'enum' : 'string',
          options: type.includes('|') ? type.split('|').map(s => s.trim().replace(/'/g, '')) : undefined,
          optional: true
        });
      });
    }
    
    return props;
  }

  extractVariants(block) {
    // 간단한 variant 추출 로직
    return [];
  }

  generateMarkdownWorkflows() {
    return [
      {
        name: 'markdown-sync',
        content: `name: "Markdown 동기화"
description: "Markdown 파일 변경사항을 코드에 반영"

trigger:
  file_change: "docs/**/*.md"

steps:
  - id: parse_markdown
    name: "Markdown 파싱"
    mcp: markdown-parser
    action: parse-components
    
  - id: generate_components
    name: "컴포넌트 생성"
    mcp: nextjs-mcp
    action: generate-from-spec
    
  - id: update_docs
    name: "문서 업데이트"
    mcp: docs-generator
    action: generate-storybook`
      }
    ];
  }
}

// 템플릿 초기화 클래스
class TemplateInitializer {
  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async question(query) {
    return new Promise((resolve) => {
      this.rl.question(query, resolve);
    });
  }

  async select(message, choices) {
    console.log(message);
    choices.forEach((choice, index) => {
      console.log(`${index + 1}. ${choice.name || choice}`);
    });
    
    while (true) {
      const answer = await this.question('\n선택하세요 (번호 입력): ');
      const index = parseInt(answer) - 1;
      
      if (index >= 0 && index < choices.length) {
        return choices[index].value || choices[index];
      }
      console.log('올바른 번호를 입력해주세요.');
    }
  }

  async multiSelect(message, choices) {
    console.log(message);
    console.log('(쉼표로 구분하여 여러 개 선택 가능, 예: 1,3,4)');
    choices.forEach((choice, index) => {
      console.log(`${index + 1}. ${choice.name || choice}`);
    });
    
    const answer = await this.question('\n선택하세요: ');
    const indices = answer.split(',').map(s => parseInt(s.trim()) - 1).filter(i => i >= 0 && i < choices.length);
    return indices.map(i => choices[i].value || choices[i]);
  }

  async initialize() {
    console.log('📋 템플릿 기반 초기화 시작\n');

    const templates = await this.getAvailableTemplates();
    
    const template = await this.select('사용할 템플릿을 선택하세요:', 
      templates.map(t => ({
        name: `${t.name} - ${t.description}`,
        value: t.id
      }))
    );

    const features = await this.multiSelect('추가할 기능을 선택하세요:', [
      { name: '다크 모드 지원', value: 'darkMode' },
      { name: '애니메이션 효과', value: 'animations' },
      { name: '접근성 기능', value: 'accessibility' },
      { name: '테스트 코드', value: 'tests' }
    ]);

    const answers = { template, features };
    this.rl.close();

    console.log('\n🏗️ 템플릿 적용 중...');
    
    const templateData = await this.loadTemplate(answers.template, answers.features);
    
    console.log(`✅ ${templateData.components.length}개 템플릿 컴포넌트 로드`);
    
    return templateData;
  }

  async getAvailableTemplates() {
    return [
      {
        id: 'basic',
        name: '기본 UI 템플릿',
        description: 'Button, Card, Input 등 기본 컴포넌트'
      },
      {
        id: 'dashboard',
        name: '대시보드 템플릿',
        description: 'Chart, Table, Sidebar 등 대시보드 컴포넌트'
      },
      {
        id: 'ecommerce',
        name: '이커머스 템플릿',
        description: 'ProductCard, Cart, Checkout 등 쇼핑 컴포넌트'
      }
    ];
  }

  async loadTemplate(templateId, features) {
    const templates = {
      basic: {
        source: 'template',
        components: [
          {
            name: 'Button',
            description: '기본 템플릿 버튼',
            props: [
              { name: 'variant', type: 'enum', options: ['primary', 'secondary', 'outline'], optional: true },
              { name: 'size', type: 'enum', options: ['xs', 'sm', 'md', 'lg', 'xl'], optional: true }
            ]
          },
          {
            name: 'Card',
            description: '기본 템플릿 카드',
            props: [
              { name: 'variant', type: 'enum', options: ['default', 'elevated', 'outlined'], optional: true }
            ]
          },
          {
            name: 'Input',
            description: '기본 템플릿 입력 필드',
            props: [
              { name: 'type', type: 'enum', options: ['text', 'email', 'password', 'number'], optional: true },
              { name: 'placeholder', type: 'string', optional: true }
            ]
          }
        ],
        workflows: this.generateTemplateWorkflows('basic')
      },
      dashboard: {
        source: 'template',
        components: [
          {
            name: 'Chart',
            description: '대시보드 차트 컴포넌트',
            props: [
              { name: 'type', type: 'enum', options: ['line', 'bar', 'pie', 'area'], optional: false },
              { name: 'data', type: 'object', optional: false }
            ]
          },
          {
            name: 'Table',
            description: '대시보드 테이블 컴포넌트',
            props: [
              { name: 'columns', type: 'array', optional: false },
              { name: 'data', type: 'array', optional: false }
            ]
          }
        ],
        workflows: this.generateTemplateWorkflows('dashboard')
      },
      ecommerce: {
        source: 'template',
        components: [
          {
            name: 'ProductCard',
            description: '상품 카드 컴포넌트',
            props: [
              { name: 'product', type: 'object', optional: false },
              { name: 'onAddToCart', type: 'function', optional: true }
            ]
          }
        ],
        workflows: this.generateTemplateWorkflows('ecommerce')
      }
    };

    return templates[templateId] || templates.basic;
  }

  generateTemplateWorkflows(templateType) {
    return [
      {
        name: `${templateType}-development`,
        content: `name: "${templateType} 개발 워크플로우"
description: "${templateType} 템플릿 개발 및 배포"

steps:
  - id: build
    name: "빌드"
    action: build-components
    
  - id: test
    name: "테스트"
    action: run-tests
    
  - id: deploy
    name: "배포"
    action: deploy-storybook`
      }
    ];
  }
}

// CLI 실행
export async function main() {
  const initializer = new ProjectInitializer();
  await initializer.start();
}

// Export classes for external use
export { ProjectInitializer, FigmaInitializer, MarkdownInitializer, TemplateInitializer };

// 직접 실행시
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}