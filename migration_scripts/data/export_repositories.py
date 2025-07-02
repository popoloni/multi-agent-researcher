#!/usr/bin/env python3
"""
Repository Data Export Script
Exports repository data to JSON or CSV format for backup or migration purposes.
"""

import argparse
import asyncio
import json
import csv
import sys
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.database_service import DatabaseService

async def export_repositories_json(output_path: str):
    """Export repositories to JSON format."""
    print("📄 Exporting repositories to JSON...")
    
    try:
        db_service = DatabaseService()
        
        # Get all repositories using the database service
        repositories = await db_service.get_all_repositories()
        
        # Convert to list of dictionaries
        repo_data = []
        for repo in repositories:
            repo_dict = repo.dict() if hasattr(repo, 'dict') else repo.__dict__
            # Convert datetime to string for JSON serialization
            if repo_dict.get('created_at'):
                repo_dict['created_at'] = repo_dict['created_at'].isoformat() if hasattr(repo_dict['created_at'], 'isoformat') else str(repo_dict['created_at'])
            if repo_dict.get('updated_at'):
                repo_dict['updated_at'] = repo_dict['updated_at'].isoformat() if hasattr(repo_dict['updated_at'], 'isoformat') else str(repo_dict['updated_at'])
            repo_data.append(repo_dict)
        
        # Export to JSON
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_repositories": len(repo_data),
            "repositories": repo_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(repo_data)} repositories to {output_path}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        sys.exit(1)

async def export_repositories_csv(output_path: str):
    """Export repositories to CSV format."""
    print("📊 Exporting repositories to CSV...")
    
    try:
        db_service = DatabaseService()
        
        # Get all repositories using the database service
        repositories = await db_service.get_all_repositories()
        
        if not repositories:
            print("ℹ️ No repositories found to export")
            return
        
        # Get column names from the first repository
        first_repo = repositories[0]
        repo_dict = first_repo.dict() if hasattr(first_repo, 'dict') else first_repo.__dict__
        columns = list(repo_dict.keys())
        
        # Export to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for repo in repositories:
                row = repo.dict() if hasattr(repo, 'dict') else repo.__dict__
                # Convert datetime to string for CSV
                if row.get('created_at'):
                    row['created_at'] = row['created_at'].isoformat() if hasattr(row['created_at'], 'isoformat') else str(row['created_at'])
                if row.get('updated_at'):
                    row['updated_at'] = row['updated_at'].isoformat() if hasattr(row['updated_at'], 'isoformat') else str(row['updated_at'])
                writer.writerow(row)
        
        print(f"✅ Exported {len(repositories)} repositories to {output_path}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        sys.exit(1)

async def main():
    parser = argparse.ArgumentParser(description="Export repository data from the Multi-Agent Research System")
    parser.add_argument("--format", "-f", choices=["json", "csv"], default="json",
                       help="Export format (json or csv)")
    parser.add_argument("--output", "-o", 
                       help="Output file path (auto-generated if not specified)")
    
    args = parser.parse_args()
    
    # Generate output filename if not specified
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f"repositories_export_{timestamp}.{args.format}"
    
    # Export based on format
    if args.format == "json":
        await export_repositories_json(args.output)
    elif args.format == "csv":
        await export_repositories_csv(args.output)

if __name__ == "__main__":
    asyncio.run(main())