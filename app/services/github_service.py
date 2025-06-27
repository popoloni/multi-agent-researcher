"""
GitHub API Service - Handles GitHub repository operations and API interactions
"""

import asyncio
import aiohttp
import os
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Multi-Agent-Researcher/1.0"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Dict = None, 
        data: Dict = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to GitHub API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        error_message = response_data.get('message', f'GitHub API error: {response.status}')
                        raise GitHubAPIError(
                            message=error_message,
                            status_code=response.status,
                            response_data=response_data
                        )
                    
                    return response_data
                    
        except aiohttp.ClientError as e:
            logger.error(f"GitHub API request failed: {str(e)}")
            raise GitHubAPIError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in GitHub API request: {str(e)}")
            raise GitHubAPIError(f"Unexpected error: {str(e)}")
    
    async def search_repositories(
        self, 
        query: str, 
        language: Optional[str] = None,
        sort: str = 'stars',
        order: str = 'desc',
        per_page: int = 30,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search GitHub repositories
        
        Args:
            query: Search query
            language: Programming language filter
            sort: Sort by 'stars', 'forks', 'help-wanted-issues', 'updated'
            order: 'asc' or 'desc'
            per_page: Results per page (max 100)
            page: Page number
            
        Returns:
            Dictionary with search results and metadata
        """
        # Build search query
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        params = {
            'q': search_query,
            'sort': sort,
            'order': order,
            'per_page': min(per_page, 100),
            'page': page
        }
        
        try:
            response = await self._make_request('GET', '/search/repositories', params=params)
            
            # Transform response to include useful metadata
            repositories = []
            for repo in response.get('items', []):
                repositories.append({
                    'id': repo['id'],
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'owner': repo['owner']['login'],
                    'description': repo.get('description', ''),
                    'language': repo.get('language'),
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'issues': repo['open_issues_count'],
                    'size': repo['size'],
                    'default_branch': repo['default_branch'],
                    'clone_url': repo['clone_url'],
                    'html_url': repo['html_url'],
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at'],
                    'pushed_at': repo.get('pushed_at'),
                    'topics': repo.get('topics', []),
                    'license': repo.get('license', {}).get('name') if repo.get('license') else None,
                    'archived': repo.get('archived', False),
                    'disabled': repo.get('disabled', False)
                })
            
            return {
                'repositories': repositories,
                'total_count': response.get('total_count', 0),
                'incomplete_results': response.get('incomplete_results', False),
                'page': page,
                'per_page': per_page,
                'has_next': len(repositories) == per_page
            }
            
        except GitHubAPIError:
            raise
        except Exception as e:
            logger.error(f"Error searching repositories: {str(e)}")
            raise GitHubAPIError(f"Search failed: {str(e)}")
    
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository information dictionary
        """
        try:
            response = await self._make_request('GET', f'/repos/{owner}/{repo}')
            
            return {
                'id': response['id'],
                'name': response['name'],
                'full_name': response['full_name'],
                'owner': response['owner']['login'],
                'description': response.get('description', ''),
                'language': response.get('language'),
                'stars': response['stargazers_count'],
                'forks': response['forks_count'],
                'issues': response['open_issues_count'],
                'size': response['size'],
                'default_branch': response['default_branch'],
                'clone_url': response['clone_url'],
                'ssh_url': response['ssh_url'],
                'html_url': response['html_url'],
                'created_at': response['created_at'],
                'updated_at': response['updated_at'],
                'pushed_at': response.get('pushed_at'),
                'topics': response.get('topics', []),
                'license': response.get('license', {}).get('name') if response.get('license') else None,
                'archived': response.get('archived', False),
                'disabled': response.get('disabled', False),
                'private': response.get('private', False),
                'fork': response.get('fork', False),
                'has_issues': response.get('has_issues', True),
                'has_projects': response.get('has_projects', True),
                'has_wiki': response.get('has_wiki', True),
                'has_pages': response.get('has_pages', False),
                'subscribers_count': response.get('subscribers_count', 0),
                'network_count': response.get('network_count', 0)
            }
            
        except GitHubAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting repository info: {str(e)}")
            raise GitHubAPIError(f"Failed to get repository info: {str(e)}")
    
    async def list_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """
        List all branches for a repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of branch information dictionaries
        """
        try:
            response = await self._make_request('GET', f'/repos/{owner}/{repo}/branches')
            
            branches = []
            for branch in response:
                branches.append({
                    'name': branch['name'],
                    'sha': branch['commit']['sha'],
                    'protected': branch.get('protected', False),
                    'commit_url': branch['commit']['url']
                })
            
            return branches
            
        except GitHubAPIError:
            raise
        except Exception as e:
            logger.error(f"Error listing branches: {str(e)}")
            raise GitHubAPIError(f"Failed to list branches: {str(e)}")
    
    async def get_repository_contents(
        self, 
        owner: str, 
        repo: str, 
        path: str = '', 
        branch: str = 'main'
    ) -> List[Dict[str, Any]]:
        """
        Get repository contents at a specific path
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within repository (empty for root)
            branch: Branch name
            
        Returns:
            List of file/directory information
        """
        try:
            params = {'ref': branch} if branch != 'main' else {}
            endpoint = f'/repos/{owner}/{repo}/contents/{path}' if path else f'/repos/{owner}/{repo}/contents'
            
            response = await self._make_request('GET', endpoint, params=params)
            
            # Handle single file vs directory listing
            if isinstance(response, dict):
                response = [response]
            
            contents = []
            for item in response:
                contents.append({
                    'name': item['name'],
                    'path': item['path'],
                    'type': item['type'],  # 'file' or 'dir'
                    'size': item.get('size', 0),
                    'sha': item['sha'],
                    'download_url': item.get('download_url'),
                    'html_url': item.get('html_url')
                })
            
            return contents
            
        except GitHubAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting repository contents: {str(e)}")
            raise GitHubAPIError(f"Failed to get repository contents: {str(e)}")
    
    async def get_user_repositories(
        self, 
        username: Optional[str] = None,
        type_filter: str = 'all',
        sort: str = 'updated',
        per_page: int = 30,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get repositories for a user (or authenticated user if no username provided)
        
        Args:
            username: GitHub username (None for authenticated user)
            type_filter: 'all', 'owner', 'public', 'private', 'member'
            sort: 'created', 'updated', 'pushed', 'full_name'
            per_page: Results per page
            page: Page number
            
        Returns:
            List of repository information dictionaries
        """
        try:
            if username:
                endpoint = f'/users/{username}/repos'
            else:
                endpoint = '/user/repos'
                if not self.token:
                    raise GitHubAPIError("Authentication required for user repositories")
            
            params = {
                'type': type_filter,
                'sort': sort,
                'per_page': min(per_page, 100),
                'page': page
            }
            
            response = await self._make_request('GET', endpoint, params=params)
            
            repositories = []
            for repo in response:
                repositories.append({
                    'id': repo['id'],
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'owner': repo['owner']['login'],
                    'description': repo.get('description', ''),
                    'language': repo.get('language'),
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'issues': repo['open_issues_count'],
                    'size': repo['size'],
                    'default_branch': repo['default_branch'],
                    'clone_url': repo['clone_url'],
                    'html_url': repo['html_url'],
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at'],
                    'pushed_at': repo.get('pushed_at'),
                    'private': repo.get('private', False),
                    'fork': repo.get('fork', False)
                })
            
            return repositories
            
        except GitHubAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting user repositories: {str(e)}")
            raise GitHubAPIError(f"Failed to get user repositories: {str(e)}")
    
    def parse_github_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse GitHub URL to extract owner and repository name
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo) or (None, None) if invalid
        """
        try:
            parsed = urlparse(url)
            
            # Handle different GitHub URL formats
            if parsed.netloc in ['github.com', 'www.github.com']:
                path_parts = parsed.path.strip('/').split('/')
                if len(path_parts) >= 2:
                    owner = path_parts[0]
                    repo = path_parts[1]
                    # Remove .git suffix if present
                    if repo.endswith('.git'):
                        repo = repo[:-4]
                    return owner, repo
            
            return None, None
            
        except Exception as e:
            logger.error(f"Error parsing GitHub URL: {str(e)}")
            return None, None
    
    async def validate_repository_access(self, owner: str, repo: str) -> bool:
        """
        Validate that a repository exists and is accessible
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            True if repository is accessible, False otherwise
        """
        try:
            await self.get_repository_info(owner, repo)
            return True
        except GitHubAPIError as e:
            if e.status_code == 404:
                return False
            raise
        except Exception:
            return False
    
    async def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current GitHub API rate limit status
        
        Returns:
            Rate limit information
        """
        try:
            response = await self._make_request('GET', '/rate_limit')
            
            return {
                'limit': response['rate']['limit'],
                'remaining': response['rate']['remaining'],
                'reset': response['rate']['reset'],
                'used': response['rate']['used'],
                'reset_datetime': datetime.fromtimestamp(response['rate']['reset'])
            }
            
        except Exception as e:
            logger.error(f"Error getting rate limit status: {str(e)}")
            return {
                'limit': 0,
                'remaining': 0,
                'reset': 0,
                'used': 0,
                'reset_datetime': None
            }


# Global instance
github_service = GitHubService()