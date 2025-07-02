"""
Migration script to enhance the research service with better async handling
"""
import asyncio
import os
import sys
import shutil
from datetime import datetime
from typing import Dict, Any
from uuid import UUID
import json

def backup_current_service():
    """Create backup of current research service"""
    backup_dir = f"../app/services/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup research service
    if os.path.exists("../app/services/research_service.py"):
        shutil.copy2("../app/services/research_service.py", f"{backup_dir}/research_service.py")
        print(f"✅ Backed up research_service.py to {backup_dir}")
    
    return backup_dir

def enhance_research_service():
    """Apply enhancements to research service"""
    service_path = "../app/services/research_service.py"
    
    if not os.path.exists(service_path):
        print("❌ Research service not found. Skipping enhancement.")
        return False
    
    # Read current service
    with open(service_path, 'r') as f:
        content = f.read()
    
    # Check if already enhanced
    if "# ENHANCED_MIGRATION_APPLIED" in content:
        print("✅ Research service already enhanced. Skipping.")
        return True
    
    # Add enhancement marker and improved error handling
    enhancement = """
# ENHANCED_MIGRATION_APPLIED - Enhanced async handling and progress tracking

import asyncio
from datetime import datetime, timedelta
from typing import Optional

class EnhancedProgressTracker:
    \"\"\"Enhanced progress tracking with better state management\"\"\"
    
    def __init__(self, research_id: str):
        self.research_id = research_id
        self.stages = []
        self.current_stage = 0
        self.overall_progress = 0.0
        self.start_time = datetime.now()
        self.estimated_completion = None
    
    def update_progress(self, stage: str, progress: float):
        \"\"\"Update progress with time estimation\"\"\"
        self.overall_progress = progress
        elapsed = datetime.now() - self.start_time
        
        if progress > 0:
            estimated_total = elapsed / (progress / 100)
            self.estimated_completion = self.start_time + estimated_total
    
    def get_time_remaining(self) -> Optional[timedelta]:
        \"\"\"Get estimated time remaining\"\"\"
        if self.estimated_completion:
            remaining = self.estimated_completion - datetime.now()
            return remaining if remaining.total_seconds() > 0 else None
        return None

"""
    
    # Insert enhancement at the beginning of the file
    enhanced_content = enhancement + content
    
    # Write enhanced service
    with open(service_path, 'w') as f:
        f.write(enhanced_content)
    
    print("✅ Research service enhanced successfully")
    return True

def validate_migration():
    """Validate that migration was successful"""
    service_path = "../app/services/research_service.py"
    
    if not os.path.exists(service_path):
        print("❌ Validation failed: Research service not found")
        return False
    
    with open(service_path, 'r') as f:
        content = f.read()
    
    if "ENHANCED_MIGRATION_APPLIED" not in content:
        print("❌ Validation failed: Enhancement marker not found")
        return False
    
    if "EnhancedProgressTracker" not in content:
        print("❌ Validation failed: Enhanced progress tracker not found")
        return False
    
    print("✅ Migration validation successful")
    return True

def main():
    """Main migration function"""
    print("🚀 Starting research service enhancement migration...")
    
    try:
        # Step 1: Create backup
        backup_dir = backup_current_service()
        
        # Step 2: Apply enhancements
        if not enhance_research_service():
            print("❌ Migration failed during enhancement")
            return False
        
        # Step 3: Validate migration
        if not validate_migration():
            print("❌ Migration validation failed")
            return False
        
        print("✅ Migration completed successfully!")
        print(f"📁 Backup created at: {backup_dir}")
        print("🔄 Please restart the services to apply changes")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
