#!/usr/bin/env python3
"""
Database Initialization Script
Initializes the database schema and creates initial tables for the Multi-Agent Research System.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.database_service import DatabaseService
from app.database.models import Base

async def init_db():
    """Initialize the database with all required tables."""
    print("🗄️ Initializing database...")
    
    try:
        # Initialize database service
        db_service = DatabaseService()
        db_service._ensure_engine()
        
        # Create all tables
        async with db_service.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database initialized successfully!")
        print("✅ All tables created!")
        
        # Test database connection
        async with db_service.session_factory() as session:
            print("✅ Database connection verified!")
            await session.close()
        
        print("\n📋 Database initialization complete!")
        print("• All tables created")
        print("• Database connection verified")
        print("• Ready for application use")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(init_db())