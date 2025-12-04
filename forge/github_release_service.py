"""
GitHub Release Management Service
Handles fetching and caching GitHub release information
"""

import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class GitHubReleaseService:
    """Service for managing GitHub releases"""
    
    def __init__(self, github_token=None):
        self.github_token = github_token or getattr(settings, 'GITHUB_API_TOKEN', None)
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'
    
    def get_latest_release(self, owner, repo):
        """
        Fetch the latest release from GitHub
        
        Returns:
            dict: Release information or None if error/no releases
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                logger.info(f"No releases found for {owner}/{repo}")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            return {
                'name': data.get('name') or data.get('tag_name'),
                'tag': data.get('tag_name'),
                'url': data.get('html_url'),
                'zipball_url': data.get('zipball_url'),
                'tarball_url': data.get('tarball_url'),
                'published_at': data.get('published_at'),
                'body': data.get('body', ''),
                'assets': [
                    {
                        'name': asset['name'],
                        'url': asset['browser_download_url'],
                        'size': asset['size']
                    }
                    for asset in data.get('assets', [])
                ]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching release for {owner}/{repo}: {str(e)}")
            return None
    
    def update_app_release_info(self, forge_app, force=False):
        """
        Update ForgeApp with latest release information
        
        Args:
            forge_app: ForgeApp instance
            force: Force update even if recently checked
            
        Returns:
            bool: True if updated, False otherwise
        """
        # Check if we need to update (only check once per hour unless forced)
        if not force and forge_app.last_release_check:
            time_since_check = timezone.now() - forge_app.last_release_check
            if time_since_check < timedelta(hours=1):
                logger.info(f"Release info for {forge_app.slug} checked recently, skipping")
                return False
        
        # Fetch latest release
        release = self.get_latest_release(forge_app.repo_owner, forge_app.repo_name)
        
        if not release:
            logger.warning(f"No release found for {forge_app.slug}")
            forge_app.last_release_check = timezone.now()
            forge_app.save(update_fields=['last_release_check'])
            return False
        
        # Update forge app
        forge_app.latest_release_name = release['name']
        forge_app.latest_release_tag = release['tag']
        forge_app.latest_release_url = release['url']
        forge_app.latest_release_zip_url = release['zipball_url']
        forge_app.last_release_check = timezone.now()
        
        forge_app.save(update_fields=[
            'latest_release_name',
            'latest_release_tag',
            'latest_release_url',
            'latest_release_zip_url',
            'last_release_check'
        ])
        
        logger.info(f"Updated release info for {forge_app.slug}: {release['name']}")
        return True
    
    def download_release_zip(self, zipball_url):
        """
        Download release zip file from GitHub
        
        Args:
            zipball_url: URL to the zipball
            
        Returns:
            bytes: Zip file content or None
        """
        try:
            response = requests.get(zipball_url, headers=self.headers, timeout=30, stream=True)
            response.raise_for_status()
            return response.content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading release zip: {str(e)}")
            return None
