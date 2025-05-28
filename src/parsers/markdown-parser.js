/**
 * Markdown Parser - MD 파일에서 컴포넌트 정의 추출
 * 
 * 지원하는 형식:
 * 1. 표준 컴포넌트 명세 형식
 * 2. Storybook MDX 형식  
 * 3. JSON-like 형식
 */

import fs from 'fs/promises';
import path from 'path';

export class MarkdownParser {
  constructor() {
    this.supportedFormats = ['standard', 'storybook', 'json-like'];
  }

  async parseFile(filePath, format = 'standard') {
    const content = await fs.readFile(filePath, 'utf8');
    
    switch (format) {
      case 'standard':
        return this.parseStandardFormat(content);
      case 'storybook':
        return this.parseStorybookFormat(content);
      case 'json-like':
        return this.parseJsonLikeFormat(content);
      default:
        throw new Error(`지원하지 않는 형식: ${format}`);
    }
  }

  /**
   * 표준 컴포넌트 명세 형식 파싱
   * 
   * 예시:
   * ## Button
   * 
   * 기본 버튼 컴포넌트입니다.
   * 
   * ### Props
   * - **variant**: `'primary' | 'secondary' | 'outline'` - 버튼 스타일 (기본값: 'primary')
   * - **size**: `'small' | 'medium' | 'large'` - 버튼 크기 (기본값: 'medium')
   * - **disabled**: `boolean` - 비활성화 여부 (기본값: false)
   * 
   * ### Examples
   * ```tsx
   * <Button variant="primary" size="medium">Click me</Button>
   * ```
   */
  parseStandardFormat(content) {
    const components = [];
    
    // ## ComponentName 패턴으로 컴포넌트 블록 분리
    const componentBlocks = content.split(/^## /m).filter(block => block.trim());
    
    componentBlocks.forEach(block => {
      const component = this.parseStandardComponent(block);
      if (component) {
        components.push(component);
      }
    });
    
    return { components, format: 'standard' };
  }

  parseStandardComponent(block) {
    const lines = block.split('\n');
    const name = lines[0].trim();
    
    // 컴포넌트 이름이 유효한지 확인
    if (!name || name === 'Components' || !this.isValidComponentName(name)) {
      return null;
    }

    const component = {
      name,
      description: this.extractDescription(block),
      props: this.extractStandardProps(block),
      examples: this.extractExamples(block),
      variants: this.extractVariants(block)
    };

    return component;
  }

  extractDescription(block) {
    const lines = block.split('\n');
    let description = '';
    
    // 첫 번째 줄(컴포넌트 명) 이후부터 ### Props 이전까지가 설명
    let isInDescription = false;
    
    for (const line of lines) {
      if (isInDescription && line.startsWith('###')) {
        break;
      }
      
      if (isInDescription && line.trim()) {
        description += line.trim() + ' ';
      }
      
      if (!isInDescription && line.trim() && !line.startsWith('#')) {
        isInDescription = true;
        description = line.trim() + ' ';
      }
    }
    
    return description.trim();
  }

  extractStandardProps(block) {
    const props = [];
    const propsSection = this.extractSection(block, '### Props');
    
    if (!propsSection) return props;
    
    // - **propName**: `type` - description (기본값: default) 형식 파싱
    const propPattern = /^- \*\*(\w+)\*\*:\s*`([^`]+)`\s*-\s*(.+?)(?:\s*\(기본값:\s*([^)]+)\))?$/gm;
    let match;
    
    while ((match = propPattern.exec(propsSection)) !== null) {
      const [, name, type, description, defaultValue] = match;
      
      props.push({
        name,
        type: this.parseTypeString(type),
        description: description.trim(),
        defaultValue: defaultValue?.trim(),
        optional: !!defaultValue
      });
    }
    
    return props;
  }

  parseTypeString(typeStr) {
    // 'primary' | 'secondary' | 'outline' -> enum
    if (typeStr.includes('|')) {
      const options = typeStr
        .split('|')
        .map(opt => opt.trim().replace(/'/g, '').replace(/"/g, ''));
      
      return {
        type: 'enum',
        options
      };
    }
    
    // 기본 타입들
    const typeMap = {
      'boolean': 'boolean',
      'number': 'number',
      'string': 'string',
      'object': 'object',
      'array': 'array',
      'function': 'function',
      '() => void': 'function',
      'React.ReactNode': 'reactNode'
    };
    
    return {
      type: typeMap[typeStr] || 'string'
    };
  }

  extractExamples(block) {
    const examplesSection = this.extractSection(block, '### Examples');
    if (!examplesSection) return [];
    
    const examples = [];
    const codeBlocks = examplesSection.match(/```[\s\S]*?```/g);
    
    if (codeBlocks) {
      codeBlocks.forEach(codeBlock => {
        const code = codeBlock.replace(/```\w*\n?/g, '').trim();
        examples.push({
          code,
          language: 'tsx'
        });
      });
    }
    
    return examples;
  }

  extractVariants(block) {
    const variantsSection = this.extractSection(block, '### Variants');
    if (!variantsSection) return [];
    
    const variants = [];
    const variantPattern = /^- \*\*(\w+)\*\*:\s*(.+)$/gm;
    let match;
    
    while ((match = variantPattern.exec(variantsSection)) !== null) {
      const [, name, description] = match;
      variants.push({
        name,
        description: description.trim(),
        classes: this.generateVariantClasses(name)
      });
    }
    
    return variants;
  }

  generateVariantClasses(variantName) {
    // 일반적인 variant 이름에 따른 클래스 매핑
    const classMap = {
      primary: 'bg-blue-600 text-white hover:bg-blue-700',
      secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
      outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white',
      success: 'bg-green-600 text-white hover:bg-green-700',
      warning: 'bg-yellow-500 text-white hover:bg-yellow-600',
      error: 'bg-red-600 text-white hover:bg-red-700',
      small: 'px-2 py-1 text-sm',
      medium: 'px-4 py-2 text-base',
      large: 'px-6 py-3 text-lg',
      elevated: 'shadow-lg hover:shadow-xl',
      flat: 'shadow-none border border-gray-200'
    };
    
    return classMap[variantName] || `variant-${variantName}`;
  }

  extractSection(content, sectionTitle) {
    const lines = content.split('\n');
    let inSection = false;
    let section = '';
    
    for (const line of lines) {
      if (line.startsWith('###') && line !== sectionTitle) {
        if (inSection) break; // 다른 섹션 시작
        continue;
      }
      
      if (line === sectionTitle) {
        inSection = true;
        continue;
      }
      
      if (inSection) {
        section += line + '\n';
      }
    }
    
    return section.trim() || null;
  }

  /**
   * Storybook MDX 형식 파싱
   */
  parseStorybookFormat(content) {
    const components = [];
    
    // Meta export에서 컴포넌트 정보 추출
    const metaMatch = content.match(/export\s+const\s+meta\s*=\s*{[\s\S]*?}/);
    if (metaMatch) {
      const component = this.parseStorybookMeta(metaMatch[0]);
      if (component) {
        components.push(component);
      }
    }
    
    return { components, format: 'storybook' };
  }

  parseStorybookMeta(metaString) {
    // 간단한 meta 파싱 (실제로는 더 정교한 파서 필요)
    const titleMatch = metaString.match(/title:\s*['"`]([^'"`]+)['"`]/);
    const componentMatch = metaString.match(/component:\s*(\w+)/);
    
    if (!titleMatch || !componentMatch) return null;
    
    return {
      name: componentMatch[1],
      description: `Storybook 컴포넌트: ${titleMatch[1]}`,
      props: this.extractStorybookProps(metaString),
      format: 'storybook'
    };
  }

  extractStorybookProps(metaString) {
    // argTypes에서 props 정보 추출
    const argTypesMatch = metaString.match(/argTypes:\s*{([\s\S]*?)}/);
    if (!argTypesMatch) return [];
    
    const props = [];
    const argTypesContent = argTypesMatch[1];
    
    // 간단한 argTypes 파싱
    const propMatches = argTypesContent.match(/(\w+):\s*{[^}]*}/g);
    if (propMatches) {
      propMatches.forEach(propMatch => {
        const nameMatch = propMatch.match(/^(\w+):/);
        if (nameMatch) {
          props.push({
            name: nameMatch[1],
            type: 'string', // 기본값
            optional: true
          });
        }
      });
    }
    
    return props;
  }

  /**
   * JSON-like 형식 파싱
   */
  parseJsonLikeFormat(content) {
    const components = [];
    
    try {
      // JSON 형식의 컴포넌트 정의 파싱
      const jsonBlocks = content.match(/```json\s*\n([\s\S]*?)\n```/g);
      
      if (jsonBlocks) {
        jsonBlocks.forEach(block => {
          const jsonContent = block.replace(/```json\s*\n/, '').replace(/\n```/, '');
          try {
            const componentDef = JSON.parse(jsonContent);
            if (componentDef.name) {
              components.push(this.normalizeJsonComponent(componentDef));
            }
          } catch (error) {
            console.warn('JSON 파싱 오류:', error.message);
          }
        });
      }
    } catch (error) {
      console.warn('JSON-like 형식 파싱 오류:', error.message);
    }
    
    return { components, format: 'json-like' };
  }

  normalizeJsonComponent(jsonComponent) {
    return {
      name: jsonComponent.name,
      description: jsonComponent.description || '',
      props: (jsonComponent.props || []).map(prop => ({
        name: prop.name,
        type: prop.type || 'string',
        description: prop.description || '',
        optional: prop.optional !== false,
        defaultValue: prop.defaultValue
      })),
      variants: jsonComponent.variants || [],
      examples: jsonComponent.examples || []
    };
  }

  isValidComponentName(name) {
    // React 컴포넌트 이름 규칙: PascalCase, 문자로 시작
    return /^[A-Z][a-zA-Z0-9]*$/.test(name);
  }

  /**
   * 샘플 Markdown 파일 생성
   */
  async generateSampleMarkdown(outputPath) {
    const sampleContent = `# 컴포넌트 명세서

이 문서는 프로젝트에서 사용하는 UI 컴포넌트들을 정의합니다.

## Button

기본 버튼 컴포넌트입니다. 다양한 스타일과 크기를 지원합니다.

### Props

- **variant**: \`'primary' | 'secondary' | 'outline'\` - 버튼 스타일 (기본값: 'primary')
- **size**: \`'small' | 'medium' | 'large'\` - 버튼 크기 (기본값: 'medium')
- **disabled**: \`boolean\` - 비활성화 여부 (기본값: false)
- **onClick**: \`() => void\` - 클릭 이벤트 핸들러

### Variants

- **primary**: 기본 파란색 버튼
- **secondary**: 회색 배경의 보조 버튼  
- **outline**: 테두리만 있는 버튼

### Examples

\`\`\`tsx
<Button variant="primary" size="medium">
  기본 버튼
</Button>

<Button variant="outline" size="large" onClick={() => alert('클릭!')}>
  아웃라인 버튼
</Button>
\`\`\`

## Card

콘텐츠를 담는 카드 컴포넌트입니다.

### Props

- **elevation**: \`'none' | 'low' | 'medium' | 'high'\` - 그림자 높이 (기본값: 'low')
- **padding**: \`'none' | 'small' | 'medium' | 'large'\` - 내부 여백 (기본값: 'medium')
- **variant**: \`'default' | 'elevated' | 'outlined'\` - 카드 스타일 (기본값: 'default')

### Examples

\`\`\`tsx
<Card elevation="medium" padding="large">
  <h2>카드 제목</h2>
  <p>카드 내용입니다.</p>
</Card>
\`\`\`

## Input

텍스트 입력 필드 컴포넌트입니다.

### Props

- **type**: \`'text' | 'email' | 'password' | 'number'\` - 입력 타입 (기본값: 'text')
- **placeholder**: \`string\` - 플레이스홀더 텍스트
- **disabled**: \`boolean\` - 비활성화 여부 (기본값: false)
- **value**: \`string\` - 입력값
- **onChange**: \`(value: string) => void\` - 값 변경 이벤트 핸들러

### Examples

\`\`\`tsx
<Input 
  type="email" 
  placeholder="이메일을 입력하세요"
  value={email}
  onChange={setEmail}
/>
\`\`\`
`;

    await fs.writeFile(outputPath, sampleContent, 'utf8');
    console.log(`샘플 Markdown 파일이 생성되었습니다: ${outputPath}`);
  }
}

export default MarkdownParser;