#!/usr/bin/env node

/**
 * 템플릿 초기화 테스트 스크립트
 * 논인터랙티브 모드로 템플릿 기반 초기화를 테스트합니다.
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 기본 UI 템플릿 데이터
const basicTemplateData = {
  source: 'template',
  components: [
    {
      name: 'Button',
      description: '기본 템플릿 버튼',
      props: [
        { name: 'variant', type: 'enum', options: ['primary', 'secondary', 'outline'], optional: true },
        { name: 'size', type: 'enum', options: ['xs', 'sm', 'md', 'lg', 'xl'], optional: true },
        { name: 'children', type: 'ReactNode', optional: false },
        { name: 'onClick', type: 'function', optional: true }
      ]
    },
    {
      name: 'Card',
      description: '기본 템플릿 카드',
      props: [
        { name: 'variant', type: 'enum', options: ['default', 'elevated', 'outlined'], optional: true },
        { name: 'children', type: 'ReactNode', optional: false },
        { name: 'className', type: 'string', optional: true }
      ]
    },
    {
      name: 'Input',
      description: '기본 템플릿 입력 필드',
      props: [
        { name: 'type', type: 'enum', options: ['text', 'email', 'password', 'number'], optional: true },
        { name: 'placeholder', type: 'string', optional: true },
        { name: 'value', type: 'string', optional: true },
        { name: 'onChange', type: 'function', optional: true }
      ]
    }
  ]
};

// 컴포넌트 생성 함수들
function generateButtonComponent(component) {
  return `import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  onClick,
  className
}) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
    outline: 'border border-gray-300 bg-transparent hover:bg-gray-50'
  };
  
  const sizeClasses = {
    xs: 'h-7 px-2 text-xs',
    sm: 'h-8 px-3 text-sm',
    md: 'h-9 px-4 text-sm',
    lg: 'h-10 px-6 text-base',
    xl: 'h-11 px-8 text-base'
  };

  return (
    <button
      onClick={onClick}
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {children}
    </button>
  );
};

export default Button;
`;
}

function generateCardComponent(component) {
  return `import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  variant?: 'default' | 'elevated' | 'outlined';
  children: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({
  variant = 'default',
  children,
  className
}) => {
  const baseClasses = 'rounded-lg bg-white p-6';
  
  const variantClasses = {
    default: 'border border-gray-200',
    elevated: 'shadow-lg',
    outlined: 'border-2 border-gray-300'
  };

  return (
    <div className={cn(baseClasses, variantClasses[variant], className)}>
      {children}
    </div>
  );
};

export default Card;
`;
}

function generateInputComponent(component) {
  return `import React from 'react';
import { cn } from '@/lib/utils';

interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
}

const Input: React.FC<InputProps> = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  className
}) => {
  const baseClasses = 'flex h-10 w-full rounded-md border border-gray-300 bg-transparent px-3 py-2 text-sm placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50';

  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className={cn(baseClasses, className)}
    />
  );
};

export default Input;
`;
}

function generateUtilsFile() {
  return `import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwindcss-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
`;
}

function generateIndexFile(components) {
  const exports = components.map(comp => `export { default as ${comp.name} } from './${comp.name}';`).join('\n');
  return exports;
}

async function createComponentFiles() {
  console.log('🏗️ 템플릿 기반 컴포넌트 생성 중...\n');
  
  const componentsDir = path.join(__dirname, 'src/components/generated');
  const libDir = path.join(__dirname, 'src/lib');
  
  // 디렉토리 생성
  await fs.mkdir(componentsDir, { recursive: true });
  await fs.mkdir(libDir, { recursive: true });
  
  // 컴포넌트 생성 함수 매핑
  const generators = {
    Button: generateButtonComponent,
    Card: generateCardComponent,
    Input: generateInputComponent
  };
  
  // 각 컴포넌트 파일 생성
  for (const component of basicTemplateData.components) {
    if (generators[component.name]) {
      const componentCode = generators[component.name](component);
      const filePath = path.join(componentsDir, `${component.name}.tsx`);
      await fs.writeFile(filePath, componentCode);
      console.log(`✅ ${component.name}.tsx 생성 완료`);
    }
  }
  
  // index.ts 파일 생성
  const indexContent = generateIndexFile(basicTemplateData.components);
  await fs.writeFile(path.join(componentsDir, 'index.ts'), indexContent);
  console.log('✅ index.ts 생성 완료');
  
  // utils 파일 생성
  const utilsContent = generateUtilsFile();
  await fs.writeFile(path.join(libDir, 'utils.ts'), utilsContent);
  console.log('✅ utils.ts 생성 완료');
  
  console.log('\n🎉 템플릿 기반 초기화 완료!');
  console.log(`📁 생성된 컴포넌트: ${basicTemplateData.components.map(c => c.name).join(', ')}`);
  console.log('📂 파일 위치: src/components/generated/');
}

async function main() {
  try {
    console.log('🚀 Vibe 템플릿 초기화 테스트\n');
    await createComponentFiles();
  } catch (error) {
    console.error('❌ 오류 발생:', error.message);
    process.exit(1);
  }
}

main();