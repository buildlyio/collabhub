"""
Download Service with License Injection
Handles downloading releases and injecting license files
"""

import io
import zipfile
import logging
from django.core.files.base import ContentFile
from .github_release_service import GitHubReleaseService

logger = logging.getLogger(__name__)


class LicenseDownloadService:
    """Service for creating downloads with injected license files"""
    
    def __init__(self):
        self.github_service = GitHubReleaseService()
    
    def generate_license_instructions(self, forge_app, purchase):
        """
        Generate LICENSE.md file content with instructions
        
        Args:
            forge_app: ForgeApp instance
            purchase: Purchase instance
            
        Returns:
            str: License file content
        """
        return f"""# {forge_app.name} - Commercial License

## License Information
- **Product:** {forge_app.name}
- **License Type:** {forge_app.get_license_type_display()}
- **Purchased By:** {purchase.user.get_full_name() or purchase.user.username}
- **Purchase Date:** {purchase.created_at.strftime('%Y-%m-%d')}
- **Purchase ID:** {purchase.id}

## License Terms

This software is licensed under the {forge_app.get_license_type_display()} license.

{'### Business Source License (BSL 1.1)' if 'BSL' in forge_app.license_type else ''}
{'''
This software is provided under the Business Source License 1.1.

**Commercial Use Restriction:**
- Production use requires a commercial license purchase
- This purchase grants you a commercial license for production use

**License Change:**
''' if 'BSL' in forge_app.license_type else ''}
{f'- On {forge_app.change_date_utc.strftime("%Y-%m-%d") if forge_app.change_date_utc else "the specified change date"}, this software automatically converts to Apache License 2.0' if 'BSL' in forge_app.license_type and forge_app.change_date_utc else ''}

## Your License Grant

**You are granted the following rights:**
- ✅ Use in production environments
- ✅ Modify the source code for your needs
- ✅ Create derivative works
- ✅ Use for commercial purposes

**Restrictions:**
- ❌ Do not redistribute this software commercially
- ❌ Do not remove or modify license headers
- ❌ License is non-transferable

## Installation

1. **Extract this archive** to your desired location
2. **Keep this LICENSE.md file** in the root of your project
3. **Follow the README.md** for installation instructions

## Repository Information
- **Source:** {forge_app.repo_url}
- **Release:** {forge_app.latest_release_name or 'Latest'}
{f'- **Version:** {forge_app.latest_release_tag}' if forge_app.latest_release_tag else ''}

## Support

For support and questions:
- Check the repository issues: {forge_app.repo_url}/issues
- Contact: support@buildly.io

## Verification

This license can be verified at:
https://collab.buildly.io/marketplace/verify/{purchase.id}

---
**Important:** This license file must remain in the root directory of your project.
Removing or modifying this file may invalidate your license.
"""
    
    def inject_license_into_zip(self, zip_content, license_content, app_name):
        """
        Inject LICENSE.md into a zip file
        
        Args:
            zip_content: Original zip file bytes
            license_content: License text to inject
            app_name: Name for the new archive
            
        Returns:
            bytes: New zip file with license injected
        """
        try:
            # Read original zip
            original_zip = zipfile.ZipFile(io.BytesIO(zip_content))
            
            # Create new zip in memory
            new_zip_io = io.BytesIO()
            new_zip = zipfile.ZipFile(new_zip_io, 'w', zipfile.ZIP_DEFLATED)
            
            # Determine root folder name
            root_folder = None
            for name in original_zip.namelist():
                if '/' in name:
                    root_folder = name.split('/')[0]
                    break
            
            # Copy all files from original zip
            for item in original_zip.infolist():
                data = original_zip.read(item.filename)
                new_zip.writestr(item, data)
            
            # Add LICENSE.md to root
            license_path = f"{root_folder}/LICENSE.md" if root_folder else "LICENSE.md"
            new_zip.writestr(license_path, license_content)
            
            # Add LICENSE_INSTRUCTIONS.md
            instructions = f"""# License Installation Instructions

## Step 1: Verify License File
Ensure the `LICENSE.md` file is present in the root directory of your project.

## Step 2: Add to Your Repository
```bash
# If using git, add the license file
git add LICENSE.md
git commit -m "Add commercial license"
```

## Step 3: Deployment
The LICENSE.md file should be included in all deployments:
- Docker builds: Include in your Dockerfile
- GitHub Pages: Will be deployed automatically
- Kubernetes: Include in your deployment manifests

## Step 4: Team Distribution
Share this licensed version with your team members who will be working on the project.

## Important Notes
- Keep LICENSE.md in the root directory
- Do not modify the license file content
- Renew your license before expiration if applicable
- Contact support if you need to transfer the license

For questions: support@buildly.io
"""
            instructions_path = f"{root_folder}/LICENSE_INSTRUCTIONS.md" if root_folder else "LICENSE_INSTRUCTIONS.md"
            new_zip.writestr(instructions_path, instructions)
            
            new_zip.close()
            original_zip.close()
            
            return new_zip_io.getvalue()
            
        except Exception as e:
            logger.error(f"Error injecting license into zip: {str(e)}")
            return None
    
    def create_licensed_download(self, forge_app, purchase):
        """
        Create a downloadable zip with license for a purchase
        
        Args:
            forge_app: ForgeApp instance
            purchase: Purchase instance
            
        Returns:
            tuple: (file_content, filename) or (None, None)
        """
        # Update release info if needed
        self.github_service.update_app_release_info(forge_app)
        
        if not forge_app.latest_release_zip_url:
            logger.error(f"No release zip URL for {forge_app.slug}")
            return None, None
        
        # Download original zip
        logger.info(f"Downloading release zip for {forge_app.slug}")
        zip_content = self.github_service.download_release_zip(forge_app.latest_release_zip_url)
        
        if not zip_content:
            logger.error(f"Failed to download release for {forge_app.slug}")
            return None, None
        
        # Generate license
        license_content = self.generate_license_instructions(forge_app, purchase)
        
        # Inject license into zip
        logger.info(f"Injecting license into zip for {forge_app.slug}")
        licensed_zip = self.inject_license_into_zip(zip_content, license_content, forge_app.name)
        
        if not licensed_zip:
            logger.error(f"Failed to inject license for {forge_app.slug}")
            return None, None
        
        # Generate filename
        tag = forge_app.latest_release_tag or 'latest'
        filename = f"{forge_app.slug}-{tag}-licensed.zip"
        
        return licensed_zip, filename
