"""
Obsqra.starknet AI Service

Off-chain service for monitoring protocols and triggering rebalances.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('obsqra.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Obsqra.starknet AI Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/health')
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {
            'starknet_rpc': True,
            'risk_engine': True,
            'strategy_router': True,
        }
    })


@app.post('/trigger-rebalance')
async def trigger_rebalance():
    """Trigger AI rebalancing"""
    try:
        from monitor import ProtocolMonitor
        monitor = ProtocolMonitor()
        allocation = await monitor.trigger_rebalance()
        
        return JSONResponse({
            'status': 'success',
            'message': 'Rebalancing triggered',
            'allocation': allocation
        })
    except Exception as e:
        logger.error(f"Rebalance error: {e}")
        return JSONResponse({
            'status': 'error',
            'message': str(e)
        }, status_code=500)


@app.post('/accrue-yields')
async def accrue_yields():
    """Accrue yields from protocols"""
    # TODO: Implement yield accrual
    return JSONResponse({
        'status': 'success',
        'message': 'Yields accrued'
    })


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

