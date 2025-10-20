import requests
import yaml
import base64
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.utils import timezone
from .models import ForgeApp, RepoValidation, ValidationStatus


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    pass


class GitHubRepoValidationService:
    """Service for validating GitHub repositories for Forge apps"""
    
    def __init__(self):
        self.github_token = getattr(settings, 'GITHUB_API_TOKEN', None)
        self.marketplace_org = getattr(settings, 'FORGE_MARKETPLACE_ORG', 'buildly-marketplace')
        self.default_branch = getattr(settings, 'FORGE_DEFAULT_BRANCH', 'main')
        
        # Note: GitHub token is optional for app startup, but required for actual validation operations
    
    def get_headers(self) -> Dict[str, str]:
        """Get GitHub API headers with authentication"""
        if not self.github_token:
            raise ValueError("GITHUB_API_TOKEN setting is required for validation operations")
        
        return {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Buildly-Forge/1.0'
        }
    
    def check_file_exists(self, owner: str, repo: str, path: str, branch: str = None) -> bool:
        """Check if a file exists in the repository"""
        branch = branch or self.default_branch
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        params = {'ref': branch}
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_file_content(self, owner: str, repo: str, path: str, branch: str = None) -> Optional[str]:
        """Get the content of a file from the repository"""
        branch = branch or self.default_branch
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        params = {'ref': branch}
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('encoding') == 'base64':
                    return base64.b64decode(data['content']).decode('utf-8')
            return None
        except (requests.RequestException, UnicodeDecodeError):
            return None
    
    def check_directory_exists(self, owner: str, repo: str, path: str, branch: str = None) -> bool:
        """Check if a directory exists in the repository"""
        branch = branch or self.default_branch
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        params = {'ref': branch}
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            if response.status_code == 200:
                data = response.json()
                return isinstance(data, list)  # Directory returns array of contents
            return False
        except requests.RequestException:
            return False
    
    def get_commit_sha(self, owner: str, repo: str, branch: str = None) -> Optional[str]:
        """Get the latest commit SHA for a branch"""
        branch = branch or self.default_branch
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()['sha']
            return None
        except requests.RequestException:
            return None
    
    def parse_buildly_yaml(self, content: str) -> Tuple[bool, Dict, List[str]]:
        """Parse BUILDLY.yaml content and validate required fields"""
        required_fields = ['name', 'slug', 'version', 'summary', 'license', 'targets']
        missing_fields = []
        parsed_data = {}
        
        try:
            parsed_data = yaml.safe_load(content)
            if not isinstance(parsed_data, dict):
                return False, {}, ['Invalid YAML structure']
            
            for field in required_fields:
                if field not in parsed_data:
                    missing_fields.append(f'BUILDLY.yaml missing field: {field}')
            
            # Validate targets is a list
            if 'targets' in parsed_data and not isinstance(parsed_data['targets'], list):
                missing_fields.append('BUILDLY.yaml targets must be a list')
            
            return len(missing_fields) == 0, parsed_data, missing_fields
            
        except yaml.YAMLError as e:
            return False, {}, [f'BUILDLY.yaml parse error: {str(e)}']
    
    def validate_target_specific_files(self, owner: str, repo: str, targets: List[str], branch: str = None) -> List[str]:
        """Validate target-specific required files"""
        missing_items = []
        
        for target in targets:
            if target == 'github-pages':
                # Check for pages workflow
                if not self.check_file_exists(owner, repo, '.github/workflows/pages.yml', branch):
                    missing_items.append('github-pages: missing .github/workflows/pages.yml')
                
                # Check for build configuration
                has_tailwind = self.check_file_exists(owner, repo, 'tailwind.config.js', branch)
                has_package_json = self.check_file_exists(owner, repo, 'package.json', branch)
                
                if not (has_tailwind or has_package_json):
                    missing_items.append('github-pages: missing tailwind.config.js OR package.json with build scripts')
            
            elif target == 'docker':
                if not self.check_file_exists(owner, repo, 'Dockerfile', branch):
                    missing_items.append('docker: missing Dockerfile')
            
            elif target == 'k8s' or target == 'kubernetes':
                has_chart = self.check_directory_exists(owner, repo, 'chart', branch)
                has_helm = self.check_directory_exists(owner, repo, 'helm', branch)
                
                if not (has_chart or has_helm):
                    missing_items.append('k8s: missing chart/ or helm/ directory')
                else:
                    # Check for required files in the chart directory
                    chart_dir = 'chart' if has_chart else 'helm'
                    if not self.check_file_exists(owner, repo, f'{chart_dir}/Chart.yaml', branch):
                        missing_items.append(f'k8s: missing {chart_dir}/Chart.yaml')
                    if not self.check_file_exists(owner, repo, f'{chart_dir}/values.yaml', branch):
                        missing_items.append(f'k8s: missing {chart_dir}/values.yaml')
            
            elif target == 'desktop':
                if not self.check_directory_exists(owner, repo, 'installers', branch):
                    missing_items.append('desktop: missing installers/ directory')
                else:
                    # Check for at least one OS subdirectory
                    os_dirs = ['macos', 'windows', 'linux']
                    has_os_dir = any(
                        self.check_directory_exists(owner, repo, f'installers/{os_dir}', branch) 
                        for os_dir in os_dirs
                    )
                    if not has_os_dir:
                        missing_items.append('desktop: installers/ directory missing OS subdirectories (macos/, windows/, linux/)')
        
        return missing_items
    
    def validate_repository(self, forge_app: ForgeApp) -> RepoValidation:
        """Main validation method for a ForgeApp repository"""
        missing_items = []
        detected_targets = []
        status = ValidationStatus.FAILED
        commit_sha = None
        
        try:
            # Validate that repo is in the correct organization
            if forge_app.repo_owner != self.marketplace_org:
                missing_items.append(f'Repository must be in {self.marketplace_org} organization')
                return self._create_validation_record(forge_app, status, missing_items, detected_targets, commit_sha)
            
            # Get current commit SHA
            commit_sha = self.get_commit_sha(forge_app.repo_owner, forge_app.repo_name)
            if not commit_sha:
                missing_items.append('Unable to access repository or get commit SHA')
                return self._create_validation_record(forge_app, status, missing_items, detected_targets, commit_sha)
            
            # Check common required files
            common_files = ['BUILDLY.yaml', 'README.md', 'LICENSE']
            for file_path in common_files:
                if not self.check_file_exists(forge_app.repo_owner, forge_app.repo_name, file_path):
                    missing_items.append(f'missing {file_path}')
            
            # Parse BUILDLY.yaml
            buildly_content = self.get_file_content(forge_app.repo_owner, forge_app.repo_name, 'BUILDLY.yaml')
            if buildly_content:
                is_valid, parsed_data, yaml_errors = self.parse_buildly_yaml(buildly_content)
                if not is_valid:
                    missing_items.extend(yaml_errors)
                else:
                    detected_targets = parsed_data.get('targets', [])
            else:
                missing_items.append('Unable to read BUILDLY.yaml content')
            
            # Validate target-specific files
            if detected_targets:
                target_missing = self.validate_target_specific_files(
                    forge_app.repo_owner, 
                    forge_app.repo_name, 
                    detected_targets
                )
                missing_items.extend(target_missing)
            
            # Determine final status
            status = ValidationStatus.PASSED if len(missing_items) == 0 else ValidationStatus.FAILED
            
        except Exception as e:
            missing_items.append(f'Validation error: {str(e)}')
            status = ValidationStatus.FAILED
        
        return self._create_validation_record(forge_app, status, missing_items, detected_targets, commit_sha)
    
    def _create_validation_record(self, forge_app: ForgeApp, status: ValidationStatus, 
                                missing_items: List[str], detected_targets: List[str], 
                                commit_sha: Optional[str]) -> RepoValidation:
        """Create and save a validation record"""
        validation = RepoValidation.objects.create(
            forge_app=forge_app,
            status=status,
            missing_items=missing_items,
            detected_targets=detected_targets,
            validated_commit_sha=commit_sha,
            run_at=timezone.now()
        )
        return validation