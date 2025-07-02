#!/usr/bin/env python3
"""
Legacy Migration Script - Version 1.x to Current
Migrates data from version 1.x of the Multi-Agent Research System to the current version.
"""

import argparse
import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.database_service import DatabaseService
from sqlalchemy import text

class V1Migrator:
    """Handles migration from version 1.x to current version."""
    
    def __init__(self, source_path: str, target_path: str):
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        self.migration_log = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log migration messages."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level}: {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
    async def migrate(self):
        """Perform the migration from v1.x to current version."""
        self.log("🔄 Starting migration from version 1.x to current version")
        
        try:
            # Validate source directory
            if not self.source_path.exists():
                raise FileNotFoundError(f"Source directory not found: {self.source_path}")
            
            # Create target directory if it doesn't exist
            self.target_path.mkdir(parents=True, exist_ok=True)
            
            # Migration steps
            await self.migrate_repositories()
            await self.migrate_documentation()
            await self.migrate_configurations()
            await self.update_database_schema()
            
            # Save migration log
            await self.save_migration_log()
            
            self.log("✅ Migration completed successfully!")
            
        except Exception as e:
            self.log(f"❌ Migration failed: {e}", "ERROR")
            raise
    
    async def migrate_repositories(self):
        """Migrate repository data from v1.x format."""
        self.log("📁 Migrating repository data...")
        
        # Look for v1.x repository files
        v1_repos_file = self.source_path / "repositories.json"
        
        if not v1_repos_file.exists():
            self.log("ℹ️ No v1.x repository data found", "WARN")
            return
        
        try:
            with open(v1_repos_file, 'r', encoding='utf-8') as f:
                v1_data = json.load(f)
            
            # Convert v1.x format to current format
            migrated_repos = []
            for repo in v1_data.get('repositories', []):
                migrated_repo = self.convert_repository_format(repo)
                migrated_repos.append(migrated_repo)
            
            # Save migrated data
            output_file = self.target_path / "migrated_repositories.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "migration_timestamp": datetime.now().isoformat(),
                    "source_version": "1.x",
                    "target_version": "current",
                    "repositories": migrated_repos
                }, f, indent=2)
            
            self.log(f"✅ Migrated {len(migrated_repos)} repositories")
            
        except Exception as e:
            self.log(f"❌ Repository migration failed: {e}", "ERROR")
            raise
    
    def convert_repository_format(self, v1_repo: dict) -> dict:
        """Convert v1.x repository format to current format."""
        # Map v1.x fields to current format
        current_repo = {
            "id": v1_repo.get("id"),
            "name": v1_repo.get("name"),
            "url": v1_repo.get("github_url", v1_repo.get("url")),
            "description": v1_repo.get("description", ""),
            "status": "active" if v1_repo.get("active", True) else "inactive",
            "created_at": v1_repo.get("created_at", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat(),
            # Add new fields with defaults
            "clone_path": v1_repo.get("local_path", ""),
            "analysis_status": "pending",
            "documentation_status": "pending"
        }
        
        return current_repo
    
    async def migrate_documentation(self):
        """Migrate documentation data from v1.x format."""
        self.log("📚 Migrating documentation data...")
        
        # Look for v1.x documentation files
        v1_docs_dir = self.source_path / "docs"
        
        if not v1_docs_dir.exists():
            self.log("ℹ️ No v1.x documentation data found", "WARN")
            return
        
        try:
            migrated_docs = []
            
            # Process each documentation file
            for doc_file in v1_docs_dir.glob("*.json"):
                with open(doc_file, 'r', encoding='utf-8') as f:
                    v1_doc = json.load(f)
                
                migrated_doc = self.convert_documentation_format(v1_doc)
                migrated_docs.append(migrated_doc)
            
            # Save migrated documentation
            output_file = self.target_path / "migrated_documentation.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "migration_timestamp": datetime.now().isoformat(),
                    "source_version": "1.x",
                    "target_version": "current",
                    "documentation": migrated_docs
                }, f, indent=2)
            
            self.log(f"✅ Migrated {len(migrated_docs)} documentation entries")
            
        except Exception as e:
            self.log(f"❌ Documentation migration failed: {e}", "ERROR")
            raise
    
    def convert_documentation_format(self, v1_doc: dict) -> dict:
        """Convert v1.x documentation format to current format."""
        current_doc = {
            "id": v1_doc.get("id"),
            "repository_id": v1_doc.get("repo_id"),
            "title": v1_doc.get("title", "Migrated Documentation"),
            "content": v1_doc.get("content", ""),
            "type": v1_doc.get("type", "general"),
            "created_at": v1_doc.get("created_at", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat(),
            # Add new fields
            "ai_generated": v1_doc.get("auto_generated", False),
            "model_used": v1_doc.get("model", "unknown"),
            "status": "migrated"
        }
        
        return current_doc
    
    async def migrate_configurations(self):
        """Migrate configuration files from v1.x format."""
        self.log("⚙️ Migrating configuration data...")
        
        # Look for v1.x config files
        v1_config_file = self.source_path / "config.json"
        
        if not v1_config_file.exists():
            self.log("ℹ️ No v1.x configuration data found", "WARN")
            return
        
        try:
            with open(v1_config_file, 'r', encoding='utf-8') as f:
                v1_config = json.load(f)
            
            # Convert to current .env format
            env_content = self.convert_config_to_env(v1_config)
            
            # Save as .env.migrated
            env_file = self.target_path / ".env.migrated"
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            self.log("✅ Configuration migrated to .env.migrated")
            self.log("ℹ️ Review and rename to .env to apply settings")
            
        except Exception as e:
            self.log(f"❌ Configuration migration failed: {e}", "ERROR")
            raise
    
    def convert_config_to_env(self, v1_config: dict) -> str:
        """Convert v1.x config format to .env format."""
        env_lines = [
            "# Migrated configuration from version 1.x",
            f"# Migration date: {datetime.now().isoformat()}",
            "",
        ]
        
        # Map v1.x config to current .env variables
        config_mapping = {
            "github_token": "GITHUB_TOKEN",
            "openai_api_key": "OPENAI_API_KEY",
            "anthropic_api_key": "ANTHROPIC_API_KEY",
            "ollama_url": "OLLAMA_BASE_URL",
            "database_url": "DATABASE_URL",
            "redis_url": "REDIS_URL",
        }
        
        for v1_key, env_key in config_mapping.items():
            if v1_key in v1_config:
                env_lines.append(f"{env_key}={v1_config[v1_key]}")
        
        # Add default values for new settings
        env_lines.extend([
            "",
            "# New settings (review and adjust as needed)",
            "LEAD_AGENT_MODEL=claude-3-5-sonnet-20241022",
            "SUBAGENT_MODEL=llama3.1:8b",
            "CITATION_MODEL=llama3.2:3b",
            "KENOBI_MODEL=claude-3-5-sonnet-20241022",
            "DOCUMENTATION_MODEL=claude-3-5-sonnet-20241022",
        ])
        
        return "\n".join(env_lines)
    
    async def update_database_schema(self):
        """Update database schema for current version."""
        self.log("🗄️ Updating database schema...")
        
        try:
            db_service = DatabaseService()
            
            # Add new columns that might not exist in v1.x
            schema_updates = [
                "ALTER TABLE repositories ADD COLUMN analysis_status TEXT DEFAULT 'pending'",
                "ALTER TABLE repositories ADD COLUMN documentation_status TEXT DEFAULT 'pending'",
                "ALTER TABLE documentation ADD COLUMN ai_generated BOOLEAN DEFAULT FALSE",
                "ALTER TABLE documentation ADD COLUMN model_used TEXT DEFAULT 'unknown'",
            ]
            
            async with db_service.session_factory() as session:
                for update in schema_updates:
                    try:
                        await session.execute(text(update))
                        await session.commit()
                        self.log(f"✅ Applied schema update: {update}")
                    except Exception as e:
                        # Column might already exist
                        await session.rollback()
                        self.log(f"ℹ️ Schema update skipped (already applied): {update}")
            
            self.log("✅ Database schema updated")
            
        except Exception as e:
            self.log(f"❌ Database schema update failed: {e}", "ERROR")
            raise
    
    async def save_migration_log(self):
        """Save the migration log to a file."""
        log_file = self.target_path / f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.migration_log))
        
        self.log(f"📝 Migration log saved to {log_file}")

async def main():
    parser = argparse.ArgumentParser(description="Migrate from Multi-Agent Research System v1.x to current version")
    parser.add_argument("--source", "-s", required=True,
                       help="Path to v1.x installation directory")
    parser.add_argument("--target", "-t", 
                       default="./migrated_data",
                       help="Path to store migrated data")
    
    args = parser.parse_args()
    
    migrator = V1Migrator(args.source, args.target)
    await migrator.migrate()

if __name__ == "__main__":
    asyncio.run(main())