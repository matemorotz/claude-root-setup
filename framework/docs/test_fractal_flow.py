#!/usr/bin/env python3
"""
Test Full Fractal Memory Flow

Demonstrates intelligent context distillation through all 4 levels:
User → Opus → Sonnet → Haiku
"""

import json
from fractal_memory import FractalMemory
from context_distiller import (
    distill_user_to_opus,
    distill_opus_to_sonnet,
    distill_sonnet_to_haiku
)


def test_full_fractal_flow():
    """
    Test complete fractal flow with realistic project context
    """
    print("=" * 70)
    print("FRACTAL MEMORY FLOW TEST")
    print("=" * 70)

    memory = FractalMemory()

    # Step 1: User Level - Full Project Context
    print("\n" + "="*70)
    print("LAYER 1: USER LEVEL (Full Context - Unlimited)")
    print("="*70)

    full_context = {
        "project": "peti",
        "claude_md": """
## Coding Conventions
- Use type hints in Python
- Follow PEP 8 style guide
- Use Pydantic for API schemas

## Testing
- Write tests before implementation
- Use pytest framework
- Aim for 80%+ coverage

## API Design
- RESTful endpoints
- Use FastAPI decorators
- Return JSON responses with proper HTTP codes
        """,
        "project_md": """
## Tech Stack
- Python 3.11
- FastAPI
- SQLAlchemy ORM
- Alembic migrations
- PostgreSQL

## Architectural Decisions
- PDF processing via Celery background tasks
- JWT authentication with bcrypt
- Pydantic schemas for validation
        """,
        "files": [
            {
                "path": "app/auth.py",
                "content": """
from fastapi import Depends
import bcrypt
import jwt

@require_auth
def verify_token(token: str):
    # JWT verification logic
    pass

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                """
            },
            {
                "path": "app/models/user.py",
                "content": """
from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
                """
            },
            {
                "path": "app/routes/auth.py",
                "content": """
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    # Login logic
    pass
                """
            }
        ],
        "file_structure": [
            "app/__init__.py",
            "app/main.py",
            "app/auth.py",
            "app/models/user.py",
            "app/models/__init__.py",
            "app/routes/auth.py",
            "app/routes/__init__.py",
            "tests/test_auth.py"
        ],
        "tech_stack": ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL"]
    }

    memory.store_project("peti", full_context)

    print(f"Stored full context: {len(json.dumps(full_context))} characters")
    print(f"Estimated tokens: {len(json.dumps(full_context)) // 4}")

    # Step 2: Opus Level - Extract Seed Rules
    print("\n" + "="*70)
    print("LAYER 2: OPUS LEVEL (Seed Rules - 10-50K tokens)")
    print("="*70)
    print("OpusPlanner distills patterns from full context...")

    seed_rules = memory.distill_to_opus("peti", distill_user_to_opus)

    print(f"\nExtracted seed rules:")
    print(json.dumps(seed_rules, indent=2))
    print(f"\nSeed rules size: {len(json.dumps(seed_rules))} characters")
    print(f"Estimated tokens: {len(json.dumps(seed_rules)) // 4}")

    # Step 3: Sonnet Level - Engineer Task Context
    print("\n" + "="*70)
    print("LAYER 3: SONNET LEVEL (Task Context - 5-15K tokens)")
    print("="*70)
    print("OpusPlanner engineers context for SonnetCoder...")

    task = {
        "task_id": "1.2",
        "action": "Add password reset endpoint",
        "description": "Add POST /auth/reset-password endpoint. Send reset email with token. Follow existing auth patterns.",
        "validation": [
            "Endpoint accepts email",
            "Token generated and stored",
            "Email sent"
        ]
    }

    task_context = memory.distill_to_sonnet("peti", task, distill_opus_to_sonnet)

    print(f"\nEngineered task context:")
    print(json.dumps(task_context, indent=2))
    print(f"\nTask context size: {len(json.dumps(task_context))} characters")
    print(f"Estimated tokens: {len(json.dumps(task_context)) // 4}")

    # Step 4: Haiku Level - Extract Minimal Step Context
    print("\n" + "="*70)
    print("LAYER 4: HAIKU LEVEL (Step Context - <2K tokens)")
    print("="*70)
    print("SonnetCoder extracts minimal context for HaikuExecutor...")

    step = {
        "step_id": "1.2.1",
        "action": "Create password reset email template",
        "description": "Create HTML email template for password reset",
        "requirements": [
            "Include reset token link",
            "Match existing email style",
            "Add expiration notice (24h)"
        ],
        "location": "app/templates/emails/reset_password.html",
        "validation": ["File created", "Contains token placeholder", "Valid HTML"]
    }

    step_context = memory.distill_to_haiku("1.2", step, distill_sonnet_to_haiku)

    print(f"\nExtracted step context:")
    print(json.dumps(step_context, indent=2))
    print(f"\nStep context size: {len(json.dumps(step_context))} characters")
    print(f"Estimated tokens: {len(json.dumps(step_context)) // 4}")

    # Summary
    print("\n" + "="*70)
    print("FRACTAL DISTILLATION SUMMARY")
    print("="*70)

    full_tokens = len(json.dumps(full_context)) // 4
    opus_tokens = len(json.dumps(seed_rules)) // 4
    sonnet_tokens = len(json.dumps(task_context)) // 4
    haiku_tokens = len(json.dumps(step_context)) // 4

    print(f"\nUser Level:   {full_tokens:,} tokens (full context)")
    print(f"Opus Level:   {opus_tokens:,} tokens ({100 * opus_tokens / full_tokens:.1f}% of full)")
    print(f"Sonnet Level: {sonnet_tokens:,} tokens ({100 * sonnet_tokens / full_tokens:.1f}% of full)")
    print(f"Haiku Level:  {haiku_tokens:,} tokens ({100 * haiku_tokens / full_tokens:.1f}% of full)")

    print(f"\nToken reduction:")
    print(f"  Full → Opus:   {100 * (1 - opus_tokens / full_tokens):.1f}% reduction")
    print(f"  Full → Sonnet: {100 * (1 - sonnet_tokens / full_tokens):.1f}% reduction")
    print(f"  Full → Haiku:  {100 * (1 - haiku_tokens / full_tokens):.1f}% reduction")

    # Agent context examples
    print("\n" + "="*70)
    print("AGENT CONTEXT EXAMPLES")
    print("="*70)

    print("\n1. OpusPlanner reads:")
    print(f"   - Full context from User level ({full_tokens} tokens)")
    print(f"   - Distills to seed rules and stores at Opus level")

    print("\n2. SonnetCoder reads:")
    print(f"   - Task context from Sonnet level ({sonnet_tokens} tokens)")
    print(f"   - Only sees relevant patterns for this specific task")
    print(f"   - Does NOT see full project context")

    print("\n3. HaikuExecutor reads:")
    print(f"   - Step context from Haiku level ({haiku_tokens} tokens)")
    print(f"   - Absolute minimum to execute single step")
    print(f"   - Does NOT see task or project context")

    # Memory statistics
    print("\n" + "="*70)
    print("MEMORY STATISTICS")
    print("="*70)

    stats = memory.get_statistics()
    print(json.dumps(stats, indent=2))

    print("\n" + "="*70)
    print("✅ FRACTAL MEMORY FLOW TEST COMPLETE")
    print("="*70)

    return True


if __name__ == "__main__":
    test_full_fractal_flow()
