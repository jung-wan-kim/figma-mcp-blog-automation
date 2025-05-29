import { createComponentLogger } from './logger.js';

/**
 * MCP 서버용 통합 로깅 유틸리티
 */
export class MCPLogger {
  constructor(serverName) {
    this.logger = createComponentLogger(serverName);
    this.serverName = serverName;
  }

  // 서버 시작/종료 로깅
  logServerStart(port) {
    this.logger.info(`${this.serverName} started`, { port, pid: process.pid });
  }

  logServerStop(reason = 'normal') {
    this.logger.info(`${this.serverName} stopped`, { reason, pid: process.pid });
  }

  // 도구 호출 로깅
  logToolCall(toolName, params, userId = 'system') {
    this.logger.info(`Tool called: ${toolName}`, {
      tool: toolName,
      params: this.sanitizeParams(params),
      userId,
      timestamp: new Date().toISOString(),
    });
  }

  logToolSuccess(toolName, result, duration) {
    this.logger.info(`Tool completed: ${toolName}`, {
      tool: toolName,
      duration: `${duration}ms`,
      resultSize: JSON.stringify(result).length,
      success: true,
    });
  }

  logToolError(toolName, error, params) {
    this.logger.error(`Tool failed: ${toolName}`, {
      tool: toolName,
      error: error.message,
      stack: error.stack,
      params: this.sanitizeParams(params),
    });
  }

  // 연결 관리 로깅
  logConnection(clientId, action = 'connected') {
    this.logger.info(`Client ${action}`, {
      clientId,
      action,
      timestamp: new Date().toISOString(),
    });
  }

  // API 호출 로깅
  logAPICall(endpoint, method, statusCode, duration) {
    const level = statusCode >= 400 ? 'error' : 'info';
    this.logger[level](`API call: ${method} ${endpoint}`, {
      endpoint,
      method,
      statusCode,
      duration: `${duration}ms`,
    });
  }

  // 워크플로우 로깅
  logWorkflowStart(workflowId, type) {
    this.logger.info(`Workflow started`, {
      workflowId,
      type,
      timestamp: new Date().toISOString(),
    });
  }

  logWorkflowStep(workflowId, step, status) {
    this.logger.info(`Workflow step: ${step}`, {
      workflowId,
      step,
      status,
      timestamp: new Date().toISOString(),
    });
  }

  logWorkflowComplete(workflowId, duration, success = true) {
    const level = success ? 'info' : 'error';
    this.logger[level](`Workflow completed`, {
      workflowId,
      duration: `${duration}ms`,
      success,
      timestamp: new Date().toISOString(),
    });
  }

  // 성능 메트릭 로깅
  logMetric(name, value, unit = 'ms', metadata = {}) {
    this.logger.info(`Metric: ${name}`, {
      metric: name,
      value,
      unit,
      ...metadata,
    });
  }

  // 헬스체크 로깅
  logHealthCheck(status, details = {}) {
    const level = status === 'healthy' ? 'info' : 'warn';
    this.logger[level](`Health check: ${status}`, {
      status,
      ...details,
      timestamp: new Date().toISOString(),
    });
  }

  // 보안 관련 파라미터 정리
  sanitizeParams(params) {
    if (!params) return {};

    const sanitized = { ...params };
    const sensitiveKeys = ['token', 'password', 'secret', 'key', 'apiKey', 'auth'];

    Object.keys(sanitized).forEach((key) => {
      if (sensitiveKeys.some((sensitive) => key.toLowerCase().includes(sensitive))) {
        sanitized[key] = '[REDACTED]';
      }
    });

    return sanitized;
  }

  // 일반 로깅 메서드
  info(message, metadata = {}) {
    this.logger.info(message, metadata);
  }

  warn(message, metadata = {}) {
    this.logger.warn(message, metadata);
  }

  error(message, error = null, metadata = {}) {
    if (error instanceof Error) {
      this.logger.error(message, {
        error: error.message,
        stack: error.stack,
        ...metadata,
      });
    } else {
      this.logger.error(message, metadata);
    }
  }

  debug(message, metadata = {}) {
    this.logger.debug(message, metadata);
  }
}

// 싱글톤 인스턴스 생성 헬퍼
const loggerInstances = new Map();

export const getMCPLogger = (serverName) => {
  if (!loggerInstances.has(serverName)) {
    loggerInstances.set(serverName, new MCPLogger(serverName));
  }
  return loggerInstances.get(serverName);
};
