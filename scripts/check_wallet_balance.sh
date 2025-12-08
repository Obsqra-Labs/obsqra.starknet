#!/bin/bash
# Monitor wallet balance and notify when STRK arrives

WALLET_ADDRESS="0x0199F1c59ffb4403E543B384f8BC77cF390A8671FBBC0F6f7eae0D462b39B777"
RPC_URL="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
CHECK_INTERVAL=10 # seconds

echo "════════════════════════════════════════════════════════════════"
echo "  💰 Wallet Balance Monitor"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Wallet: ${WALLET_ADDRESS:0:10}...${WALLET_ADDRESS: -8}"
echo "Checking every ${CHECK_INTERVAL} seconds..."
echo "Press Ctrl+C to stop"
echo ""

LAST_BALANCE="0"

while true; do
    BALANCE=$(starkli balance "$WALLET_ADDRESS" --rpc "$RPC_URL" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+')
    
    if [ -z "$BALANCE" ]; then
        BALANCE="0.000000000000000000"
    fi
    
    TIMESTAMP=$(date '+%H:%M:%S')
    
    if [ "$BALANCE" != "$LAST_BALANCE" ] && [ "$BALANCE" != "0.000000000000000000" ]; then
        echo ""
        echo "════════════════════════════════════════════════════════════════"
        echo "🎉 STRK RECEIVED!"
        echo "════════════════════════════════════════════════════════════════"
        echo "  Balance: $BALANCE STRK"
        echo "  Time: $TIMESTAMP"
        echo ""
        echo "✅ Your wallet is now funded!"
        echo "✅ Ready to deploy account and interact with contracts"
        echo ""
        echo "Next steps:"
        echo "  1. Refresh your wallet in ArgentX"
        echo "  2. Go to http://localhost:3003"
        echo "  3. Make your first transaction to deploy account"
        echo "════════════════════════════════════════════════════════════════"
        
        # Play a sound if available
        which paplay >/dev/null 2>&1 && paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || true
        
        break
    else
        echo -ne "\r[$TIMESTAMP] Balance: $BALANCE STRK (waiting...)"
    fi
    
    LAST_BALANCE="$BALANCE"
    sleep $CHECK_INTERVAL
done

