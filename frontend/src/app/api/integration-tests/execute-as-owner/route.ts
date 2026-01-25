import { NextRequest, NextResponse } from 'next/server';
import { Account, RpcProvider, Call, uint256 } from 'starknet';
import { getConfig } from '@/lib/config';
import { readFile } from 'fs/promises';
import { join } from 'path';

/**
 * API route to execute owner-only functions using the owner's private key
 * This allows non-owner wallets to trigger owner-only functions via backend
 * Reads the private key from the sncast keystore file
 */
async function getOwnerPrivateKey(): Promise<string> {
  // Try environment variable first (for flexibility)
  if (process.env.OWNER_PRIVATE_KEY) {
    return process.env.OWNER_PRIVATE_KEY;
  }

  // Otherwise, read from sncast keystore file
  // The keystore is typically at ~/.starknet_accounts/starknet_open_zeppelin_accounts.json
  // In production, this would be an absolute path or environment variable
  const keystorePath = process.env.KEYSTORE_PATH || '/root/.starknet_accounts/starknet_open_zeppelin_accounts.json';
  
  try {
    const keystoreContent = await readFile(keystorePath, 'utf-8');
    const keystore = JSON.parse(keystoreContent);
    
    // Get the deployer account from alpha-sepolia network
    const deployerAccount = keystore['alpha-sepolia']?.['deployer'];
    if (!deployerAccount || !deployerAccount.private_key) {
      throw new Error('Deployer account not found in keystore');
    }
    
    return deployerAccount.private_key;
  } catch (error: any) {
    throw new Error(`Failed to read keystore: ${error.message}. Please set OWNER_PRIVATE_KEY in .env.local or ensure keystore exists at ${keystorePath}`);
  }
}

export async function POST(request: NextRequest) {
  // SECURITY: Disable this route on production
  // Only allow on development/staging environments
  // Default to enabled on dev, only disable if explicitly set to false or in production
  const isProduction = process.env.NODE_ENV === 'production' || 
                       process.env.VERCEL_ENV === 'production';
  
  // Allow explicit override: ENABLE_OWNER_API=false to disable, ENABLE_OWNER_API=true to enable
  const ownerApiDisabled = process.env.ENABLE_OWNER_API === 'false';
  
  if (isProduction || ownerApiDisabled) {
    return NextResponse.json(
      {
        success: false,
        error: 'Owner wallet API is disabled on production for security',
        details: 'This endpoint is only available in development/staging environments. On production, only the contract owner can execute owner-only functions directly via their wallet.',
      },
      { status: 403 }
    );
  }

  try {
    const body = await request.json();
    const { functionName, calldata } = body;

    console.log('[Owner API] Received request:', { 
      functionName, 
      calldata,
      calldataType: typeof calldata,
      calldataIsArray: Array.isArray(calldata),
      calldataLength: calldata?.length
    });
    
    // Ensure calldata is always an array
    const safeCalldata = Array.isArray(calldata) ? calldata : (calldata ? [calldata] : []);

    // Get owner private key from keystore or environment
    let ownerPrivateKey: string;
    try {
      ownerPrivateKey = await getOwnerPrivateKey();
      console.log('[Owner API] Private key retrieved successfully');
    } catch (error: any) {
      console.error('[Owner API] Failed to get private key:', error);
      return NextResponse.json(
        {
          success: false,
          error: error.message,
        },
        { status: 500 }
      );
    }

    let config;
    let contractAddress: string;
    let rpcUrl: string;
    try {
      config = getConfig();
      contractAddress = config.strategyRouterAddress;
      rpcUrl = config.rpcUrl;
      console.log('[Owner API] Config loaded:', { contractAddress, rpcUrl });
    } catch (error: any) {
      console.error('[Owner API] Failed to load config:', error);
      return NextResponse.json(
        {
          success: false,
          error: `Failed to load config: ${error.message}`,
        },
        { status: 500 }
      );
    }

    // Create provider
    let provider: RpcProvider;
    let account: Account;
    try {
      provider = new RpcProvider({ nodeUrl: rpcUrl });
      console.log('[Owner API] Provider created');

      // Get owner address from deployment config
      const ownerAddress = '0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d';

      // Create account from private key
      // Note: This assumes the private key is for a standard account (not Argent/Braavos)
      // If using Argent/Braavos, you'd need their account abstraction SDK
      account = new Account(provider, ownerAddress, ownerPrivateKey);
      console.log('[Owner API] Account created for:', ownerAddress);
    } catch (error: any) {
      console.error('[Owner API] Failed to create provider/account:', error);
      return NextResponse.json(
        {
          success: false,
          error: `Failed to create account: ${error.message}`,
          details: error.toString(),
        },
        { status: 500 }
      );
    }

    // Construct the Call directly (like the Starknet.js docs example)
    // Don't use contract.populate() - it's causing undefined values
    let call: Call;
    try {
      if (functionName === 'deploy_to_protocols') {
        // No parameters - empty calldata array (per Starknet.js docs)
        call = {
          contractAddress: contractAddress,
          entrypoint: 'deploy_to_protocols',
          calldata: [], // Empty array - no parameters
        };
      } else if (functionName === 'accrue_yields' || functionName === 'accrue_jediswap_yields' || functionName === 'accrue_ekubo_yields') {
        // No parameters - empty calldata array
        call = {
          contractAddress: contractAddress,
          entrypoint: functionName,
          calldata: [], // No parameters
        };
      } else if (functionName === 'rebalance') {
        // No parameters - empty calldata array
        call = {
          contractAddress: contractAddress,
          entrypoint: 'rebalance',
          calldata: [], // No parameters
        };
      } else if (functionName === 'test_jediswap_only' || functionName === 'test_ekubo_only') {
        // Convert amount string to u256 [low, high]
        if (!safeCalldata || safeCalldata.length === 0 || !safeCalldata[0]) {
          throw new Error(`Missing amount parameter for ${functionName}`);
        }
        
        const amountString = String(safeCalldata[0]);
        if (amountString === 'undefined' || amountString === 'null' || amountString.trim() === '') {
          throw new Error(`Invalid amount for ${functionName}: ${amountString}`);
        }
        
        const amountBigInt = BigInt(amountString);
        const amountU256 = uint256.bnToUint256(amountBigInt);
        
        call = {
          contractAddress: contractAddress,
          entrypoint: functionName,
          calldata: [amountU256.low.toString(), amountU256.high.toString()], // Explicit u256 [low, high] as strings
        };
      } else if (functionName === 'commit_mist_deposit') {
        // MIST: commit_mist_deposit(commitment_hash: felt252, expected_amount: u256)
        if (!safeCalldata || safeCalldata.length < 2) {
          throw new Error('Missing parameters for commit_mist_deposit: need commitment_hash and expected_amount');
        }
        
        const commitmentHash = String(safeCalldata[0]);
        const amountString = String(safeCalldata[1]);
        const amountBigInt = BigInt(amountString);
        const amountU256 = uint256.bnToUint256(amountBigInt);
        
        call = {
          contractAddress: contractAddress,
          entrypoint: 'commit_mist_deposit',
          calldata: [commitmentHash, amountU256.low.toString(), amountU256.high.toString()],
        };
      } else if (functionName === 'reveal_and_claim_mist_deposit') {
        // MIST: reveal_and_claim_mist_deposit(secret: felt252)
        if (!safeCalldata || safeCalldata.length === 0 || !safeCalldata[0]) {
          throw new Error('Missing secret parameter for reveal_and_claim_mist_deposit');
        }
        
        const secret = String(safeCalldata[0]);
        
        call = {
          contractAddress: contractAddress,
          entrypoint: 'reveal_and_claim_mist_deposit',
          calldata: [secret],
        };
      } else {
        throw new Error(`Unknown function: ${functionName}`);
      }
      
      // Validate call object before proceeding
      if (!call.contractAddress || typeof call.contractAddress !== 'string') {
        throw new Error(`Invalid contractAddress: ${call.contractAddress}`);
      }
      if (!call.entrypoint || typeof call.entrypoint !== 'string') {
        throw new Error(`Invalid entrypoint: ${call.entrypoint}`);
      }
      if (!Array.isArray(call.calldata)) {
        throw new Error(`Calldata must be array, got: ${typeof call.calldata}`);
      }
      
      // Ensure calldata contains only strings (no undefined, null, BigInt, etc.)
      const validatedCalldata = call.calldata.map((val: any, idx: number) => {
        if (val === undefined || val === null) {
          throw new Error(`Calldata[${idx}] is undefined/null`);
        }
        return String(val); // Convert everything to string
      });
      
      const validatedCall: Call = {
        contractAddress: String(call.contractAddress),
        entrypoint: String(call.entrypoint),
        calldata: validatedCalldata,
      };
      const safeCalldataForLog: string[] = Array.isArray(validatedCall.calldata)
        ? validatedCall.calldata.map((v: any) => String(v))
        : [];
      
      console.log('[Owner API] Constructed call:', JSON.stringify({
        contractAddress: validatedCall.contractAddress,
        entrypoint: validatedCall.entrypoint,
        calldata: safeCalldataForLog,
        calldataLength: safeCalldataForLog.length,
        calldataTypes: safeCalldataForLog.map(v => typeof v),
      }, null, 2));
      
      // Use validated call
      call = validatedCall;
    } catch (error: any) {
      console.error('[Owner API] Failed to construct call:', error);
      console.error('[Owner API] Error stack:', error.stack);
      console.error('[Owner API] Function:', functionName);
      console.error('[Owner API] Calldata received:', calldata);
      console.error('[Owner API] Safe calldata:', safeCalldata);
      return NextResponse.json(
        {
          success: false,
          error: `Failed to construct call: ${error.message}`,
          details: error.toString(),
          stack: error.stack,
          functionName,
          receivedCalldata: calldata,
        },
        { status: 500 }
      );
    }

    // Execute the transaction
    let result;
    try {
      // Final validation: ensure calldata has no undefined/null values and is properly formatted
      // Filter out any undefined/null values and convert everything to strings
      const validatedCalldata = (Array.isArray(call.calldata) ? call.calldata : [])
        .filter((val: any) => val !== undefined && val !== null && val !== 'undefined' && val !== 'null')
        .map((val: any, idx: number) => {
          // Convert BigInt to string (Starknet expects calldata as strings)
          if (typeof val === 'bigint') {
            return val.toString();
          }
          // Convert number to string
          if (typeof val === 'number') {
            return val.toString();
          }
          // Ensure all values are strings (but not empty strings from undefined)
          const strVal = String(val);
          if (strVal === 'undefined' || strVal === 'null' || strVal === '') {
            throw new Error(`Calldata[${idx}] resulted in invalid string: "${strVal}". Original value: ${JSON.stringify(val)}`);
          }
          return strVal;
        });
      
      const validatedCall = {
        contractAddress: call.contractAddress,
        entrypoint: call.entrypoint,
        calldata: validatedCalldata,
      };
      
      // Ensure contractAddress and entrypoint are valid strings
      if (!validatedCall.contractAddress || typeof validatedCall.contractAddress !== 'string') {
        throw new Error(`Invalid contractAddress: ${validatedCall.contractAddress}`);
      }
      if (!validatedCall.entrypoint || typeof validatedCall.entrypoint !== 'string') {
        throw new Error(`Invalid entrypoint: ${validatedCall.entrypoint}`);
      }
      
      // Ensure calldata is an array (even if empty)
      if (!Array.isArray(validatedCall.calldata)) {
        throw new Error(`Calldata must be an array, got: ${typeof validatedCall.calldata}`);
      }
      
      console.log(`[Owner API] Executing ${functionName} as owner`);
      console.log('[Owner API] Validated call:', JSON.stringify({
        contractAddress: validatedCall.contractAddress,
        entrypoint: validatedCall.entrypoint,
        calldataLength: validatedCall.calldata.length,
        calldata: validatedCall.calldata,
        calldataTypes: validatedCall.calldata.map((v: any) => typeof v),
      }, null, 2));
      
      // Final check: ensure no undefined/null values
      for (let i = 0; i < validatedCall.calldata.length; i++) {
        const val = validatedCall.calldata[i];
        if (val === undefined || val === null) {
          throw new Error(`Calldata[${i}] is undefined/null. Full calldata: ${JSON.stringify(validatedCall.calldata)}`);
        }
        if (typeof val !== 'string') {
          throw new Error(`Calldata[${i}] must be string, got ${typeof val}: ${JSON.stringify(val)}`);
        }
      }
      
      // Create a fresh Call object to ensure no prototype pollution
      const finalCall: Call = {
        contractAddress: String(validatedCall.contractAddress),
        entrypoint: String(validatedCall.entrypoint),
        calldata: validatedCall.calldata.map(v => String(v)), // Double-ensure all strings
      };
      
      console.log('[Owner API] Final call object:', JSON.stringify({
        contractAddress: finalCall.contractAddress,
        entrypoint: finalCall.entrypoint,
        calldata: finalCall.calldata,
      }, null, 2));
      
      // Execute - wrap in try-catch to capture exact error location
      // The error "Cannot convert undefined to BigInt" happens inside account.execute()
      // This suggests account.execute() is trying to process something with undefined
      try {
        console.log('[Owner API] About to call account.execute()...');
        console.log('[Owner API] Account address:', account.address);
        console.log('[Owner API] Account class:', account.constructor.name);
        
        // Get nonce explicitly to ensure it's available
        // This prevents "undefined" nonce from causing BigInt conversion errors
        try {
          const nonce = await account.getNonce();
          console.log('[Owner API] Got nonce:', nonce.toString());
        } catch (nonceError: any) {
          console.warn('[Owner API] Failed to get nonce, will let account.execute() handle it:', nonceError.message);
          // If nonce fetch fails, account.execute() will get it automatically - that's fine
        }
        
        // Try single Call object first (per Starknet.js docs)
        // Omit abis parameter (don't pass undefined) - let Starknet.js handle it
        // Don't pass maxFee - let the account estimate fees automatically
        try {
          // Use execute with just the call, omit abis and details to use defaults
          // This lets Starknet.js handle fee estimation and nonce automatically
          result = await account.execute(finalCall);
          console.log('[Owner API] ✅ Execute succeeded with single Call object');
        } catch (singleCallError: any) {
          console.log('[Owner API] Single Call format failed, trying array format...', singleCallError.message);
          // Fallback to array format
          result = await account.execute([finalCall]);
          console.log('[Owner API] ✅ Execute succeeded with array format');
        }
      } catch (error: any) {
        console.error('[Owner API] ❌ Execute failed:', error.message);
        console.error('[Owner API] Error type:', error.constructor.name);
        console.error('[Owner API] Error stack:', error.stack);
        
        // Log the exact call object that failed
        const safeFinalCalldata: string[] = Array.isArray(finalCall.calldata)
          ? finalCall.calldata.map((v: any) => String(v))
          : [];
        console.error('[Owner API] Failed call object:', JSON.stringify({
          contractAddress: finalCall.contractAddress,
          entrypoint: finalCall.entrypoint,
          calldata: safeFinalCalldata,
          calldataLength: safeFinalCalldata.length,
          calldataTypes: safeFinalCalldata.map((v: any) => typeof v),
          calldataValues: safeFinalCalldata.map((v: any) => String(v)),
        }, null, 2));
        
        throw error; // Re-throw to be caught by outer handler
      }
      console.log('[Owner API] Transaction submitted:', result.transaction_hash);
    } catch (error: any) {
      console.error('[Owner API] Transaction execution failed:', error);
      
      // Check for "No pending deposits" error
      const errorStr = error.toString() + error.message;
      if (errorStr.includes('No pending deposits') || errorStr.includes('0x4e6f2070656e64696e67206465706f73697473')) {
        return NextResponse.json(
          {
            success: false,
            error: 'No pending deposits',
            details: 'The deploy_to_protocols function requires deposits to have been made first. Please deposit funds using the deposit() function before calling deploy_to_protocols.',
            userMessage: 'ℹ️ No Pending Deposits\n\nYou need to deposit funds first before deploying to protocols. Use the Deposit function in the main dashboard, then try deploy_to_protocols again.',
          },
          { status: 400 }
        );
      }
      
      return NextResponse.json(
        {
          success: false,
          error: `Transaction execution failed: ${error.message}`,
          details: error.toString(),
        },
        { status: 500 }
      );
    }

    // Return success immediately with transaction hash
    // Don't wait for receipt here - let the frontend handle it
    // This prevents API timeouts from causing false failures
    return NextResponse.json({
      success: true,
      transactionHash: result.transaction_hash,
      message: `Successfully executed ${functionName} as owner. Transaction submitted.`,
      note: 'Receipt will be fetched by frontend',
    });
  } catch (error: any) {
    console.error('[Owner API] Error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Failed to execute transaction',
        details: error.toString(),
      },
      { status: 500 }
    );
  }
}
