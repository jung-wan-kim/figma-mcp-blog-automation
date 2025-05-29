import { getEnvManager } from './env-manager.js';
import { getMCPLogger } from './mcp-logger.js';
import chalk from 'chalk';

const logger = getMCPLogger('env-validator');

/**
 * 환경변수 검증 및 초기화 유틸리티
 */
export class EnvValidator {
  constructor() {
    this.errors = [];
    this.warnings = [];
  }

  /**
   * 전체 시스템 환경변수 검증
   */
  async validateSystem() {
    console.log(chalk.blue('\n🔍 환경변수 검증 시작...\n'));

    const envManager = await getEnvManager();
    const services = ['common', 'figma', 'github', 'supabase'];

    for (const service of services) {
      await this.validateService(service, envManager);
    }

    this.printReport();

    if (this.errors.length > 0) {
      throw new Error('환경변수 검증 실패');
    }

    return true;
  }

  /**
   * 서비스별 환경변수 검증
   */
  async validateService(service, envManager) {
    console.log(chalk.yellow(`\n[${service.toUpperCase()}] 서비스 검증`));

    try {
      envManager.validateServiceEnv(service);
      console.log(chalk.green(`✓ ${service} 서비스 환경변수 검증 완료`));
    } catch (error) {
      this.errors.push({
        service,
        message: error.message,
      });
      console.log(chalk.red(`✗ ${service} 서비스 환경변수 오류: ${error.message}`));
    }

    // 추가 검증 로직
    await this.performAdditionalValidations(service, envManager);
  }

  /**
   * 서비스별 추가 검증
   */
  async performAdditionalValidations(service, envManager) {
    switch (service) {
      case 'figma':
        await this.validateFigmaConfig(envManager);
        break;
      case 'github':
        await this.validateGitHubConfig(envManager);
        break;
      case 'supabase':
        await this.validateSupabaseConfig(envManager);
        break;
    }
  }

  /**
   * Figma 설정 검증
   */
  async validateFigmaConfig(envManager) {
    const token = envManager.get('FIGMA_TOKEN');
    if (token && !token.startsWith('figd_')) {
      this.warnings.push({
        service: 'figma',
        message: 'FIGMA_TOKEN이 올바른 형식이 아닐 수 있습니다 (figd_로 시작해야 함)',
      });
    }
  }

  /**
   * GitHub 설정 검증
   */
  async validateGitHubConfig(envManager) {
    const token = envManager.get('GITHUB_TOKEN');
    const _owner = envManager.get('GITHUB_OWNER');
    const repo = envManager.get('GITHUB_REPO');

    if (token && !token.startsWith('ghp_') && !token.startsWith('github_pat_')) {
      this.warnings.push({
        service: 'github',
        message: 'GITHUB_TOKEN이 올바른 형식이 아닐 수 있습니다',
      });
    }

    if (repo && repo.includes('/')) {
      this.errors.push({
        service: 'github',
        message: 'GITHUB_REPO는 저장소 이름만 포함해야 합니다 (소유자 제외)',
      });
    }
  }

  /**
   * Supabase 설정 검증
   */
  async validateSupabaseConfig(envManager) {
    const url = envManager.get('SUPABASE_URL');
    const anonKey = envManager.get('SUPABASE_ANON_KEY');

    if (url && !url.includes('.supabase.co')) {
      this.warnings.push({
        service: 'supabase',
        message: 'SUPABASE_URL이 올바른 Supabase URL이 아닐 수 있습니다',
      });
    }

    if (anonKey && anonKey.length < 100) {
      this.warnings.push({
        service: 'supabase',
        message: 'SUPABASE_ANON_KEY가 너무 짧습니다',
      });
    }
  }

  /**
   * 검증 결과 출력
   */
  printReport() {
    console.log(chalk.blue('\n📊 환경변수 검증 결과\n'));

    if (this.errors.length === 0 && this.warnings.length === 0) {
      console.log(chalk.green('✅ 모든 환경변수가 올바르게 설정되었습니다!\n'));
      return;
    }

    if (this.errors.length > 0) {
      console.log(chalk.red(`\n❌ 오류 (${this.errors.length}개):`));
      this.errors.forEach(({ service, message }) => {
        console.log(chalk.red(`  - [${service}] ${message}`));
      });
    }

    if (this.warnings.length > 0) {
      console.log(chalk.yellow(`\n⚠️  경고 (${this.warnings.length}개):`));
      this.warnings.forEach(({ service, message }) => {
        console.log(chalk.yellow(`  - [${service}] ${message}`));
      });
    }

    console.log('');
  }

  /**
   * 환경변수 초기화 가이드 출력
   */
  static async printSetupGuide() {
    console.log(chalk.blue('\n📋 환경변수 설정 가이드\n'));

    console.log(chalk.white('1. .env.example 파일을 복사하여 .env 파일을 생성하세요:'));
    console.log(chalk.gray('   cp .env.example .env\n'));

    console.log(chalk.white('2. 각 서비스의 토큰/키를 획득하세요:'));
    console.log(chalk.gray('   - Figma: https://www.figma.com/developers/api#access-tokens'));
    console.log(chalk.gray('   - GitHub: https://github.com/settings/tokens'));
    console.log(chalk.gray('   - Supabase: https://app.supabase.com/project/_/settings/api\n'));

    console.log(chalk.white('3. .env 파일에 필요한 값들을 입력하세요\n'));

    console.log(chalk.white('4. 환경변수 검증을 실행하세요:'));
    console.log(chalk.gray('   npm run validate:env\n'));
  }
}

// CLI 실행을 위한 메인 함수
export async function validateEnvironment() {
  const validator = new EnvValidator();

  try {
    await validator.validateSystem();
    logger.info('환경변수 검증 완료');
    process.exit(0);
  } catch (error) {
    logger.error('환경변수 검증 실패', error);
    console.log(chalk.red('\n❌ 환경변수 검증 실패\n'));

    await EnvValidator.printSetupGuide();
    process.exit(1);
  }
}

// CLI로 직접 실행 시
if (import.meta.url === `file://${process.argv[1]}`) {
  validateEnvironment();
}
