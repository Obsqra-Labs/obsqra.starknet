"""Transaction tracking endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Transaction
from app.api.routes.auth import get_current_user

router = APIRouter()


class TransactionCreate(BaseModel):
    """Create transaction entry."""
    tx_hash: str
    tx_type: str
    amount: float = None
    details: dict = None


@router.post("/")
async def create_transaction(
    tx: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create transaction entry."""
    transaction = Transaction(
        user_id=current_user.id,
        tx_hash=tx.tx_hash,
        tx_type=tx.tx_type,
        amount=tx.amount,
        details=tx.details or {},
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return {"id": transaction.id, "tx_hash": transaction.tx_hash}


@router.get("/")
async def list_transactions(
    tx_type: str = Query(None),
    status: str = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user transactions."""
    query = select(Transaction).where(
        Transaction.user_id == current_user.id
    ).order_by(desc(Transaction.created_at))
    
    if tx_type:
        query = query.where(Transaction.tx_type == tx_type)
    
    if status:
        query = query.where(Transaction.status == status)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return [
        {
            "id": t.id,
            "tx_hash": t.tx_hash,
            "tx_type": t.tx_type,
            "amount": t.amount,
            "status": t.status,
            "details": t.details,
            "created_at": t.created_at,
        }
        for t in transactions
    ]


@router.get("/{tx_hash}")
async def get_transaction(
    tx_hash: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get transaction details."""
    result = await db.execute(
        select(Transaction).where(
            (Transaction.user_id == current_user.id) &
            (Transaction.tx_hash == tx_hash)
        )
    )
    transaction = result.scalars().first()
    
    if not transaction:
        return {"error": "Transaction not found"}, 404
    
    return {
        "id": transaction.id,
        "tx_hash": transaction.tx_hash,
        "tx_type": transaction.tx_type,
        "amount": transaction.amount,
        "status": transaction.status,
        "details": transaction.details,
        "created_at": transaction.created_at,
        "updated_at": transaction.updated_at,
    }

