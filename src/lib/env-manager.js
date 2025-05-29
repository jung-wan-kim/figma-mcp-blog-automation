import dotenv from 'dotenv';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { getMCPLogger } from './mcp-logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const logger = getMCPLogger('env-manager');

/**
 * 환경변수 중앙 관리 시스템
 */
export class EnvManager {
  constructor() {
    this.env = process.env.NODE_ENV || 'development';
    this.rootPath = path.join(__dirname, '../..');
    this.envCache = new Map();
    this.requiredVars = new Map();

    this.initializeRequiredVars();
  }

  initializeRequiredVars() {
    // 각 서비스별 필수 환경변수 정의
    this.requiredVars.set('figma', [
      { key: 'FIGMA_TOKEN', description: 'Figma API 접근 토큰' },
      { key: 'FIGMA_FILE_KEY', description: 'Figma 파일 키', optional: true },
    ]);

    this.requiredVars.set('github', [
      { key: 'GITHUB_TOKEN', description: 'GitHub Personal Access Token' },
      { key: 'GITHUB_OWNER', description: 'GitHub 저장소 소유자' },
      { key: 'GITHUB_REPO', description: 'GitHub 저장소 이름' },
    ]);

    this.requiredVars.set('supabase', [
      { key: 'SUPABASE_URL', description: 'Supabase 프로젝트 URL' },
      { key: 'SUPABASE_ANON_KEY', description: 'Supabase 익명 키' },
      { key: 'SUPABASE_SERVICE_KEY', description: 'Supabase 서비스 키', optional: true },
    ]);

    this.requiredVars.set('common', [
      { key: 'NODE_ENV', description: '실행 환경', optional: true },
      { key: 'LOG_LEVEL', description: '로깅 레벨', optional: true },
      { key: 'PORT', description: '서버 포트', optional: true },
    ]);
  }

  /**
   * 환경변수 파일 로드
   */
  async loadEnvFile(envPath = null) {
    try {
      const filePath = envPath || path.join(this.rootPath, `.env.${this.env}`);
      const fallbackPath = path.join(this.rootPath, '.env');

      // 환경별 파일 먼저 시도
      try {
        const envContent = await fs.readFile(filePath, 'utf-8');
        const parsed = dotenv.parse(envContent);
        Object.entries(parsed).forEach(([key, value]) => {
          this.envCache.set(key, value);
        });
        logger.info(`환경변수 파일 로드 완료: ${filePath}`);
      } catch {
        // 기본 .env 파일 시도
        if (await this.fileExists(fallbackPath)) {
          const envContent = await fs.readFile(fallbackPath, 'utf-8');
          const parsed = dotenv.parse(envContent);
          Object.entries(parsed).forEach(([key, value]) => {
            this.envCache.set(key, value);
          });
          logger.info(`환경변수 파일 로드 완료: ${fallbackPath}`);
        }
      }
    } catch (error) {
      logger.warn('환경변수 파일 로드 실패', { error: error.message });
    }
  }

  /**
   * 서비스별 환경변수 검증
   */
  validateServiceEnv(service) {
    const required = this.requiredVars.get(service) || [];
    const missing = [];
    const warnings = [];

    for (const { key, description, optional } of required) {
      const value = this.get(key);
      if (!value && !optional) {
        missing.push(`${key}: ${description}`);
      } else if (!value && optional) {
        warnings.push(`${key}: ${description} (선택사항)`);
      }
    }

    if (missing.length > 0) {
      logger.error(`${service} 서비스 필수 환경변수 누락`, { missing });
      throw new Error(`필수 환경변수 누락: ${missing.join(', ')}`);
    }

    if (warnings.length > 0) {
      logger.warn(`${service} 서비스 선택 환경변수 미설정`, { warnings });
    }

    return true;
  }

  /**
   * 환경변수 가져오기 (캐시 우선)
   */
  get(key, defaultValue = null) {
    // 1. 프로세스 환경변수 확인
    if (process.env[key]) {
      return process.env[key];
    }

    // 2. 캐시 확인
    if (this.envCache.has(key)) {
      return this.envCache.get(key);
    }

    // 3. 기본값 반환
    return defaultValue;
  }

  /**
   * 환경변수 설정 (런타임)
   */
  set(key, value) {
    process.env[key] = value;
    this.envCache.set(key, value);
    logger.debug(`환경변수 설정: ${key}`);
  }

  /**
   * 환경변수 템플릿 생성
   */
  async generateEnvTemplate(services = ['figma', 'github', 'supabase']) {
    const lines = ['# 자동 생성된 환경변수 템플릿', `# 생성일: ${new Date().toISOString()}`, ''];

    // 공통 환경변수
    lines.push('# 공통 설정');
    const commonVars = this.requiredVars.get('common') || [];
    for (const { key, description, optional } of commonVars) {
      const optionalMark = optional ? ' (선택사항)' : '';
      lines.push(`# ${description}${optionalMark}`);
      lines.push(`${key}=`);
      lines.push('');
    }

    // 서비스별 환경변수
    for (const service of services) {
      const vars = this.requiredVars.get(service) || [];
      if (vars.length > 0) {
        lines.push(`# ${service.toUpperCase()} 서비스`);
        for (const { key, description, optional } of vars) {
          const optionalMark = optional ? ' (선택사항)' : '';
          lines.push(`# ${description}${optionalMark}`);
          lines.push(`${key}=`);
          lines.push('');
        }
      }
    }

    const templatePath = path.join(this.rootPath, '.env.example');
    await fs.writeFile(templatePath, lines.join('\n'));
    logger.info('환경변수 템플릿 생성 완료', { path: templatePath });

    return templatePath;
  }

  /**
   * 환경변수 상태 리포트
   */
  getStatusReport() {
    const report = {
      environment: this.env,
      loaded: this.envCache.size,
      services: {},
    };

    for (const [service, vars] of this.requiredVars) {
      const status = {
        total: vars.length,
        configured: 0,
        missing: [],
      };

      for (const { key, optional } of vars) {
        if (this.get(key)) {
          status.configured++;
        } else if (!optional) {
          status.missing.push(key);
        }
      }

      report.services[service] = status;
    }

    return report;
  }

  /**
   * 환경별 설정 병합
   */
  async mergeEnvironmentConfigs() {
    const configs = {};

    // 기본 설정 로드
    const defaultConfig = await this.loadConfig('.env');
    Object.assign(configs, defaultConfig);

    // 환경별 설정 오버라이드
    if (this.env !== 'development') {
      const envConfig = await this.loadConfig(`.env.${this.env}`);
      Object.assign(configs, envConfig);
    }

    // 로컬 설정 오버라이드 (버전 관리 제외)
    const localConfig = await this.loadConfig('.env.local');
    Object.assign(configs, localConfig);

    return configs;
  }

  async loadConfig(filename) {
    try {
      const filePath = path.join(this.rootPath, filename);
      const content = await fs.readFile(filePath, 'utf-8');
      return dotenv.parse(content);
    } catch {
      return {};
    }
  }

  async fileExists(filePath) {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }
}

// 싱글톤 인스턴스
let instance;

export const getEnvManager = async () => {
  if (!instance) {
    instance = new EnvManager();
    await instance.loadEnvFile();
  }
  return instance;
};

// 헬퍼 함수들
export const validateEnv = async (service) => {
  const envManager = await getEnvManager();
  return envManager.validateServiceEnv(service);
};

export const getEnv = async (key, defaultValue) => {
  const envManager = await getEnvManager();
  return envManager.get(key, defaultValue);
};

export const setEnv = async (key, value) => {
  const envManager = await getEnvManager();
  return envManager.set(key, value);
};
