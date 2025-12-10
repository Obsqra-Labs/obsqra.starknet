# Strategy Router V2 - Protocol Flow Diagram

## Contract Architecture

```mermaid
graph TB
    subgraph "User Layer"
        User[User Wallet<br/>Argent/Braavos]
    end
    
    subgraph "Strategy Router V2"
        SR[StrategyRouterV2<br/>0x0456ae70...]
        
        subgraph "Core Functions"
            Deposit[deposit<br/>amount: u256]
            Withdraw[withdraw<br/>amount: u256]
            Deploy[deploy_to_protocols]
            Accrue[accrue_yields]
            Rebalance[rebalance]
        end
        
        subgraph "Storage"
            Balances[User Balances<br/>Map<address, u256>]
            Positions[Position Tracking<br/>JediSwap & Ekubo IDs]
            Metadata[Position Metadata<br/>Pool Keys, Bounds, Salts]
            Pending[Pending Deposits<br/>u256]
        end
    end
    
    subgraph "JediSwap Integration"
        JSRouter[JediSwap V2 Router<br/>0x03c8e56d...]
        JSNFT[JediSwap NFT Manager<br/>0x024fd972...]
    end
    
    subgraph "Ekubo Integration"
        EkuboCore[Ekubo Core<br/>0x0444a09d...]
        EkuboPos[Ekubo Positions<br/>NFT Registry]
    end
    
    subgraph "Tokens"
        STRK[STRK Token<br/>0x04718f5a...]
        ETH[ETH Token]
    end
    
    User -->|1. deposit| Deposit
    Deposit -->|Transfer STRK| STRK
    Deposit -->|Track| Balances
    Deposit -->|Add to| Pending
    
    User -->|2. deploy_to_protocols| Deploy
    Deploy -->|Swap STRK→ETH| JSRouter
    Deploy -->|Add Liquidity| JSNFT
    Deploy -->|Mint Position| JSNFT
    Deploy -->|Store NFT ID| Positions
    Deploy -->|Add Liquidity| EkuboPos
    Deploy -->|Mint Position| EkuboPos
    Deploy -->|Store Position ID| Positions
    Deploy -->|Store Metadata| Metadata
    
    User -->|3. accrue_yields| Accrue
    Accrue -->|Collect Fees| JSNFT
    Accrue -->|Lock Core| EkuboCore
    EkuboCore -->|Callback| SR
    SR -->|collect_fees| EkuboCore
    Accrue -->|Reinvest| Balances
    
    User -->|4. withdraw| Withdraw
    Withdraw -->|Transfer STRK| STRK
    Withdraw -->|Update| Balances
```

## User Deposit Flow

```mermaid
sequenceDiagram
    participant U as User
    participant W as Wallet
    participant SR as StrategyRouterV2
    participant STRK as STRK Token
    
    U->>W: Request deposit(amount)
    W->>STRK: approve(SR, amount)
    STRK-->>W: Success
    W->>SR: deposit(amount)
    SR->>STRK: transfer_from(user, amount)
    STRK-->>SR: Success
    SR->>SR: Update user_balances[user]
    SR->>SR: Update pending_deposits
    SR-->>W: Success
    W-->>U: Transaction confirmed
```

## Protocol Deployment Flow

```mermaid
sequenceDiagram
    participant U as User
    participant SR as StrategyRouterV2
    participant JSR as JediSwap Router
    participant JSN as JediSwap NFT Manager
    participant EP as Ekubo Positions
    participant EC as Ekubo Core
    
    U->>SR: deploy_to_protocols()
    
    Note over SR: Calculate allocations<br/>50% JediSwap, 50% Ekubo
    
    rect rgb(200, 220, 255)
        Note over SR,JSR: JediSwap Integration
        SR->>STRK: approve(JSR, half_amount)
        SR->>JSR: exact_input_single(STRK→ETH)
        JSR-->>SR: ETH received
        SR->>STRK: approve(JSN, STRK_amount)
        SR->>ETH: approve(JSN, ETH_amount)
        SR->>JSN: mint(MintParams)
        JSN-->>SR: (token_id, liquidity, amount0, amount1)
        SR->>SR: Store jediswap_position_ids[index] = token_id
    end
    
    rect rgb(255, 220, 200)
        Note over SR,EP: Ekubo Integration
        SR->>STRK: approve(EP, ekubo_amount)
        SR->>EP: mint_and_deposit(pool_key, bounds)
        Note over EP,EC: EP handles Core.lock() internally
        EP->>EC: lock()
        EC->>EP: locked() callback
        EP->>EC: pay(STRK)
        EP->>EC: update_position()
        EC-->>EP: Position created
        EP-->>SR: (token_id, liquidity)
        SR->>SR: Store ekubo_position_ids[index] = token_id
        SR->>SR: Store pool_key, bounds, salt metadata
    end
    
    SR-->>U: Deployment complete
```

## Fee Collection Flow

### JediSwap Fee Collection

```mermaid
sequenceDiagram
    participant SR as StrategyRouterV2
    participant JSN as JediSwap NFT Manager
    participant STRK as STRK Token
    participant ETH as ETH Token
    
    SR->>SR: accrue_yields()
    
    loop For each JediSwap position
        SR->>SR: Get token_id from jediswap_position_ids
        SR->>JSN: collect(CollectParams)
        Note over JSN: Collects fees from position
        JSN->>STRK: transfer(fees_0)
        JSN->>ETH: transfer(fees_1)
        STRK-->>SR: Fees received
        ETH-->>SR: Fees received
    end
    
    SR->>SR: Sum total_fees_0, total_fees_1
    SR->>SR: Update total_deposits += fees
    SR-->>SR: Yield accrued
```

### Ekubo Fee Collection

```mermaid
sequenceDiagram
    participant SR as StrategyRouterV2
    participant EC as Ekubo Core
    participant STRK as STRK Token
    participant ETH as ETH Token
    
    SR->>SR: accrue_yields()
    
    loop For each Ekubo position
        SR->>SR: Get pool_key, bounds, salt from metadata
        SR->>SR: Set ekubo_collecting_fees = true
        SR->>SR: Store collection state
        SR->>EC: lock(empty_data)
        
        Note over EC: Core locks state<br/>Calls back to SR
        
        EC->>SR: locked(id, data)
        
        alt Fee Collection Mode
            SR->>SR: Read pool_key, bounds, salt from storage
            SR->>EC: collect_fees(pool_key, salt, bounds)
            Note over EC: Computes fees owed<br/>Updates position state
            EC->>STRK: Transfer fees_0 to SR
            EC->>ETH: Transfer fees_1 to SR
            EC-->>SR: Delta(amount0, amount1)
        end
        
        SR->>SR: Set ekubo_collecting_fees = false
    end
    
    SR->>SR: Sum total fees
    SR->>SR: Update total_deposits += fees
    SR-->>SR: Yield accrued
```

## Withdrawal Flow

```mermaid
sequenceDiagram
    participant U as User
    participant SR as StrategyRouterV2
    participant STRK as STRK Token
    
    U->>SR: withdraw(amount)
    
    SR->>SR: Check user_balances[user] >= amount
    SR->>SR: Update user_balances[user] -= amount
    SR->>SR: Update total_deposits -= amount
    SR->>STRK: transfer(user, amount)
    STRK-->>SR: Success
    SR-->>U: Withdrawal complete
```

## Contract Function Reference

### StrategyRouterV2 Core Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `deposit` | User deposits STRK | `amount: u256` | - |
| `withdraw` | User withdraws STRK | `amount: u256` | `u256` (actual withdrawn) |
| `deploy_to_protocols` | Deploy pending deposits to protocols | - | - |
| `accrue_yields` | Collect fees from all positions | - | `u256` (total yield) |
| `rebalance` | Rebalance positions based on allocation | - | - |
| `update_allocation` | Update protocol allocation percentages | `jediswap_pct: felt252`, `ekubo_pct: felt252` | - |

### Position Tracking Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `get_jediswap_position` | Get JediSwap NFT token ID | `index: u256` | `u256` (token_id) |
| `get_ekubo_position` | Get Ekubo position ID | `index: u256` | `u64` (token_id) |
| `get_jediswap_position_count` | Get total JediSwap positions | - | `u256` |
| `get_ekubo_position_count` | Get total Ekubo positions | - | `u256` |

### Testing Functions

| Function | Purpose | Parameters |
|----------|---------|------------|
| `test_jediswap_only` | Test JediSwap integration only | `amount: u256` |
| `test_ekubo_only` | Test Ekubo integration only | `amount: u256` |
| `approve_token_for_testing` | Approve tokens for testing | `token: ContractAddress`, `spender: ContractAddress`, `amount: u256` |

## Storage Structure

### User Balances
```cairo
user_balances: Map<ContractAddress, u256>
```

### Position Tracking
```cairo
// JediSwap
jediswap_position_count: u256
jediswap_position_ids: Map<u256, u256>  // index -> NFT token_id

// Ekubo
ekubo_position_count: u256
ekubo_position_ids: Map<u256, u64>  // index -> position token_id
ekubo_position_token0: Map<u256, ContractAddress>
ekubo_position_token1: Map<u256, ContractAddress>
ekubo_position_fee: Map<u256, u128>
ekubo_position_tick_spacing: Map<u256, u128>
ekubo_position_extension: Map<u256, ContractAddress>
ekubo_position_salt: Map<u256, felt252>  // For collect_fees()
ekubo_position_tick_lower_mag: Map<u256, u128>
ekubo_position_tick_lower_sign: Map<u256, bool>
ekubo_position_tick_upper_mag: Map<u256, u128>
ekubo_position_tick_upper_sign: Map<u256, bool>
```

### Protocol Configuration
```cairo
jediswap_allocation: u256  // Basis points (10000 = 100%)
ekubo_allocation: u256     // Basis points (10000 = 100%)
jediswap_router: ContractAddress
jediswap_nft_manager: ContractAddress
ekubo_core: ContractAddress
ekubo_positions: ContractAddress
```

## Integration Details

### JediSwap Integration
- **Router**: V2 Swap Router (`exact_input_single`)
- **Liquidity**: NFT Position Manager (`mint`)
- **Fee Collection**: NFT Position Manager (`collect`)
- **Position Type**: ERC-721 NFT (token_id)

### Ekubo Integration
- **Liquidity**: Positions Contract (`mint_and_deposit`)
- **Fee Collection**: Core Contract (`collect_fees` via lock/callback)
- **Position Type**: Position ID (u64) + metadata (pool_key, bounds, salt)
- **Lock Pattern**: Core.lock() → locked() callback → collect_fees()

## Current Deployment

**Contract Address**: `0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e`  
**Network**: Starknet Sepolia  
**Class Hash**: `0x01afb6e5a5811eca06eddb043710aff0b2527055703d80d41f18325e40b332d8`

**Explorer**: https://sepolia.starkscan.co/contract/0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e

