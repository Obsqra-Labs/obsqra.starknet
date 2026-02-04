# Backend Development Guide

This guide covers backend architecture, adding new services, API endpoint creation, database models, and testing backend services.

## Backend Architecture

### Service Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/        # API endpoints
│   ├── services/          # Business logic
│   ├── models.py         # Database models
│   ├── config.py         # Configuration
│   └── database.py       # Database connection
├── requirements.txt
└── main.py              # Application entry
```

### Service Layer Pattern

**Services:**
- `stone_prover_service.py`: Proof generation
- `integrity_service.py`: Proof verification
- `model_service.py`: Model management
- `risk_engine.py`: API endpoints

## Adding New Services

### Service Template

```python
"""Service description"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class NewService:
    """Service class description"""
    
    def __init__(self, config: dict):
        self.config = config
    
    async def service_method(self, param: str) -> dict:
        """Method description"""
        try:
            # Service logic
            result = {}
            logger.info(f"Service method completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Service error: {e}")
            raise
```

### Service Registration

**In main.py:**
```python
from app.services.new_service import NewService

@app.on_event("startup")
async def startup():
    app.state.new_service = NewService(config)
```

## API Endpoint Creation

### Endpoint Template

**Create route file:**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class RequestModel(BaseModel):
    field: str

class ResponseModel(BaseModel):
    result: str

@router.post("/endpoint", response_model=ResponseModel)
async def endpoint(request: RequestModel):
    """Endpoint description"""
    try:
        # Logic
        return ResponseModel(result="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Register Route

**In app/api/__init__.py:**
```python
from app.api.routes import new_route

app.include_router(new_route.router, prefix="/api/v1/new", tags=["new"])
```

## Database Models

### Model Definition

```python
from sqlalchemy import Column, String, Integer, DateTime
from app.database import Base

class NewModel(Base):
    __tablename__ = "new_table"
    
    id = Column(String, primary_key=True)
    field1 = Column(String)
    field2 = Column(Integer)
    created_at = Column(DateTime)
```

### Database Operations

```python
from app.database import get_db
from app.models import NewModel

def create_item(db: Session, data: dict):
    item = NewModel(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
```

## Testing Backend Services

### Unit Tests

```python
import pytest
from app.services.new_service import NewService

def test_service_method():
    service = NewService({})
    result = service.service_method("test")
    assert result == expected
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_api_endpoint(client):
    response = await client.post("/api/v1/endpoint", json={"field": "value"})
    assert response.status_code == 200
    assert response.json()["result"] == "success"
```

### Run Tests

```bash
pytest tests/
pytest --cov=app tests/
```

## Next Steps

- **[Frontend Development](04-frontend-development.md)** - Next.js development
- **[Contract Development](02-contract-development.md)** - Cairo contracts
- **[Setup](01-setup.md)** - Development environment

---

**Backend Development Summary:** Complete guide for Python/FastAPI backend development with services, APIs, and testing.
