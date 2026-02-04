/**
 * Centralized error handling and user-friendly messages
 */

export enum ErrorCategory {
  WALLET = 'WALLET',
  CONTRACT = 'CONTRACT',
  NETWORK = 'NETWORK',
  VALIDATION = 'VALIDATION',
  TRANSACTION = 'TRANSACTION',
  RPC = 'RPC',
  UNKNOWN = 'UNKNOWN',
}

export interface ObsqraError {
  category: ErrorCategory;
  userMessage: string;
  technicalMessage: string;
  originalError?: Error;
  code?: string;
  retryable: boolean;
}

/**
 * Categorize and translate errors to user-friendly messages
 */
export function categorizeError(error: unknown): ObsqraError {
  const message = error instanceof Error ? error.message : String(error);

  // Wallet errors
  if (message.includes('wallet') || message.includes('signer')) {
    return {
      category: ErrorCategory.WALLET,
      userMessage: 'Wallet connection issue. Please reconnect your wallet.',
      technicalMessage: message,
      originalError: error instanceof Error ? error : undefined,
      retryable: true,
    };
  }

  // Network errors
  if (
    message.includes('network') ||
    message.includes('Connection refused') ||
    message.includes('ECONNREFUSED')
  ) {
    return {
      category: ErrorCategory.NETWORK,
      userMessage: 'Network connection error. Check your internet and try again.',
      technicalMessage: message,
      originalError: error instanceof Error ? error : undefined,
      retryable: true,
    };
  }

  // RPC errors
  if (message.includes('RPC') || message.includes('rpc')) {
    return {
      category: ErrorCategory.RPC,
      userMessage: 'RPC provider error. The network may be temporarily unavailable.',
      technicalMessage: message,
      originalError: error instanceof Error ? error : undefined,
      retryable: true,
    };
  }

  // Contract errors
  if (
    message.includes('contract') ||
    message.includes('Contract') ||
    message.includes('entrypoint')
  ) {
    if (message.includes('not found')) {
      return {
        category: ErrorCategory.CONTRACT,
        userMessage: 'Contract not found. Contract address may be incorrect.',
        technicalMessage: message,
        originalError: error instanceof Error ? error : undefined,
        retryable: false,
      };
    }
    return {
      category: ErrorCategory.CONTRACT,
      userMessage: 'Contract interaction failed. Please check contract configuration.',
      technicalMessage: message,
      originalError: error instanceof Error ? error : undefined,
      retryable: true,
      code: 'CONTRACT_CALL_FAILED',
    };
  }

  // Proof verification errors (Stone-only strict mode)
  if (
    message.includes('Proof not verified') ||
    message.includes('proof verification failed') ||
    message.includes('Strict Mode') ||
    message.includes('FactRegistry')
  ) {
    return {
      category: ErrorCategory.VALIDATION,
      userMessage: 'Proof verification failed. The proof could not be verified on-chain. This is a strict error - no fallbacks are available.',
      technicalMessage: message,
      originalError: error instanceof Error ? error : undefined,
      retryable: false,
      code: 'PROOF_VERIFICATION_FAILED',
    };
  }

  // Validation errors
  if (message.includes('invalid') || message.includes('Invalid')) {
    return {
      category: ErrorCategory.VALIDATION,
      userMessage: 'Invalid input. Please check your values and try again.',
      technicalMessage: message,
      originalError: error instanceof Error ? error : undefined,
      retryable: false,
    };
  }

  // Insufficient balance
  if (
    message.includes('balance') ||
    message.includes('insufficient') ||
    message.includes('Insufficient')
  ) {
    return {
      category: ErrorCategory.VALIDATION,
      userMessage: 'Insufficient balance. Please check your account balance.',
      technicalMessage: message,
      originalError: error instanceof Error ? error : undefined,
      retryable: false,
    };
  }

  // Transaction errors
  if (message.includes('transaction') || message.includes('tx')) {
    if (message.includes('rejected') || message.includes('Rejected')) {
      return {
        category: ErrorCategory.TRANSACTION,
        userMessage: 'Transaction rejected. Please try again.',
        technicalMessage: message,
        originalError: error instanceof Error ? error : undefined,
        retryable: true,
      };
    }
    if (message.includes('timeout')) {
      return {
        category: ErrorCategory.TRANSACTION,
        userMessage: 'Transaction timeout. The network may be congested.',
        technicalMessage: message,
        originalError: error instanceof Error ? error : undefined,
        retryable: true,
      };
    }
    return {
      category: ErrorCategory.TRANSACTION,
      userMessage: 'Transaction failed. Please check the details and try again.',
      technicalMessage: message,
      originalError: error instanceof Error ? error : undefined,
      retryable: true,
    };
  }

  // Default unknown error
  return {
    category: ErrorCategory.UNKNOWN,
    userMessage: 'An unexpected error occurred. Please try again later.',
    technicalMessage: message,
    originalError: error instanceof Error ? error : undefined,
    retryable: true,
  };
}

/**
 * Format error for display in UI
 */
export function formatErrorForDisplay(error: ObsqraError): {
  title: string;
  message: string;
  icon: string;
  actionable: boolean;
} {
  const categoryMessages: Record<ErrorCategory, string> = {
    [ErrorCategory.WALLET]: '🔌',
    [ErrorCategory.CONTRACT]: '⚙️',
    [ErrorCategory.NETWORK]: '📡',
    [ErrorCategory.VALIDATION]: '⚠️',
    [ErrorCategory.TRANSACTION]: '💸',
    [ErrorCategory.RPC]: '🌐',
    [ErrorCategory.UNKNOWN]: '❌',
  };

  return {
    icon: categoryMessages[error.category],
    title: `${error.category} Error`,
    message: error.userMessage,
    actionable: error.retryable,
  };
}

/**
 * Retry logic with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  initialDelayMs = 1000
): Promise<T> {
  let lastError: Error | unknown;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      const obsqraError = categorizeError(error);

      if (!obsqraError.retryable || attempt === maxRetries - 1) {
        throw error;
      }

      // Exponential backoff
      const delayMs = initialDelayMs * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }

  throw lastError;
}

/**
 * Log error with context for debugging
 */
export function logError(
  error: ObsqraError,
  context?: {
    component?: string;
    action?: string;
    userId?: string;
    [key: string]: any;
  }
): void {
  // In production, this would send to error tracking service (Sentry, LogRocket, etc.)
  const logEntry = {
    timestamp: new Date().toISOString(),
    category: error.category,
    message: error.technicalMessage,
    context,
    retryable: error.retryable,
  };

  // Console log for development
  console.error('[ObsqraError]', logEntry);

  // TODO: Send to error tracking service
  // if (process.env.NODE_ENV === 'production') {
  //   reportToErrorTracking(logEntry);
  // }
}
