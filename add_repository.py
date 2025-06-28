#!/usr/bin/env python3
"""
Script to manually add the astropy repository to the API's repository service
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.kenobi_agent import KenobiAgent

async def add_repository():
    """Add the astropy repository to the API's repository service"""

    print("Adding astropy repository to API...")

    # Initialize the same Kenobi agent instance used by the API
    kenobi = KenobiAgent()

    # Check if the repository directory exists
    repo_path = "/tmp/kenobi_repos/astropy"
    if not os.path.exists(repo_path):
        print(f"❌ Repository directory not found: {repo_path}")
        return

    try:
        # Scan the local repository and add it to the repository service
        repository = await kenobi.repository_service.scan_local_directory(
            path=repo_path,
            url="https://github.com/astropy/astropy"
        )

        print(f"✅ Repository added successfully:")
        print(f"   - ID: {repository.id}")
        print(f"   - Name: {repository.name}")
        print(f"   - Language: {repository.language.value}")
        print(f"   - Files: {repository.file_count}")
        print(f"   - Lines: {repository.line_count}")

        # List all repositories to verify
        repositories = await kenobi.repository_service.list_repositories()
        print(f"\n📋 Total repositories in service: {len(repositories)}")
        for repo in repositories:
            print(f"   - {repo.name} ({repo.id})")

    except Exception as e:
        print(f"❌ Error adding repository: {e}")

if __name__ == "__main__":
    asyncio.run(add_repository())