#!/usr/bin/env python3
"""
Database Backup Script
Creates backups of the SQLite database with timestamp and compression options.
"""

import argparse
import asyncio
import sys
import os
import shutil
import gzip
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.config import settings

def backup_database(output_path: str, compress: bool = False):
    """Create a backup of the database."""
    print("💾 Creating database backup...")
    
    try:
        # Get the database path from settings
        database_url = getattr(settings, 'DATABASE_URL', None) or "sqlite+aiosqlite:///./kenobi.db"
        # Extract the file path from the SQLite URL
        if database_url.startswith("sqlite"):
            db_path = database_url.split("///")[-1]
        else:
            print("❌ This backup script only supports SQLite databases")
            sys.exit(1)
        
        if not os.path.exists(db_path):
            print(f"❌ Database file not found: {db_path}")
            sys.exit(1)
        
        # Create backup
        if compress:
            print(f"📦 Creating compressed backup: {output_path}")
            with open(db_path, 'rb') as f_in:
                with gzip.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            print(f"📄 Creating backup: {output_path}")
            shutil.copy2(db_path, output_path)
        
        # Get file sizes
        original_size = os.path.getsize(db_path)
        backup_size = os.path.getsize(output_path)
        
        print("✅ Backup created successfully!")
        print(f"• Original size: {original_size:,} bytes")
        print(f"• Backup size: {backup_size:,} bytes")
        
        if compress:
            compression_ratio = (1 - backup_size / original_size) * 100
            print(f"• Compression: {compression_ratio:.1f}%")
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Backup the Multi-Agent Research System database")
    parser.add_argument("--output", "-o", 
                       default=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                       help="Output backup file path")
    parser.add_argument("--compress", "-c", action="store_true",
                       help="Compress the backup using gzip")
    
    args = parser.parse_args()
    
    # Add .gz extension if compressing
    if args.compress and not args.output.endswith('.gz'):
        args.output += '.gz'
    
    backup_database(args.output, args.compress)

if __name__ == "__main__":
    main()