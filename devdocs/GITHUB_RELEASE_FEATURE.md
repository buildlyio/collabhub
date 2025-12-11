# GitHub Release Download Feature

## Overview

This feature enables automatic downloading of GitHub releases with automated license injection for purchased ForgeApps. Users who purchase an app can download a licensed copy of the latest GitHub release with their purchase details embedded in a LICENSE.md file.

## New Features

### 1. Video Demo Support
- **New Fields**: `demo_video_url`, `video_type` (youtube/vimeo/loom)
- **Automatic Embed URLs**: Property method `video_embed_url` generates embed URLs for video players
- **Admin Support**: Video fields added to admin interface

### 2. GitHub Release Integration
- **New Fields**: 
  - `latest_release_name`: Name of the latest release
  - `latest_release_tag`: Git tag of the release
  - `latest_release_url`: URL to the GitHub release page
  - `latest_release_zip_url`: Direct download URL for the release zip
  - `last_release_check`: Timestamp of last GitHub API check
- **Property**: `has_github_release` - Boolean indicating if app has release data
- **Service**: `GitHubReleaseService` handles all GitHub API interactions
- **1-hour Cache**: Release info is cached for 1 hour to avoid API rate limits

### 3. Download Tracking
- **New Purchase Fields**:
  - `download_count`: Number of times user downloaded the app
  - `last_downloaded`: Timestamp of last download
- **Service**: `LicenseDownloadService` creates licensed downloads
- **API Endpoint**: `GET /api/forge/purchases/{id}/download/`

### 4. Automated License Injection
- **License Document**: Auto-generated `LICENSE.md` with:
  - App name and version
  - Purchaser information (name, email)
  - Purchase date and ID
  - License type (MIT, Apache 2.0, GPL-3.0, etc.)
  - Usage terms and restrictions
- **Instructions File**: `README_LICENSE.txt` with installation and usage instructions
- **Zip Injection**: Files injected into GitHub release zip without re-downloading

## API Endpoints

### Purchase Download
```
GET /api/forge/purchases/{id}/download/
Authorization: Token <user-token>
```
Returns: Zip file with licensed app code

**Requirements**:
- User must own the purchase
- Purchase status must be `completed`
- ForgeApp must have a GitHub release configured

**Response**:
- Content-Type: application/zip
- Content-Disposition: attachment; filename="appname-v1.0.0-licensed.zip"
- Updates `download_count` and `last_downloaded` on Purchase

### Update Release Info (Admin Only)
```
POST /api/forge/apps/{slug}/update_release/
Authorization: Token <admin-token>
Body: {"force": true}  # Optional
```
Updates GitHub release information for an app

**Requirements**:
- User must be staff/admin
- ForgeApp must have `repo_url` configured

**Response**:
```json
{
  "success": true,
  "message": "Release info updated for App Name",
  "release": {
    "name": "v1.0.0",
    "tag": "v1.0.0",
    "url": "https://github.com/org/repo/releases/tag/v1.0.0",
    "last_checked": "2024-12-04T22:32:00Z"
  }
}
```

## Admin Actions

### Update GitHub Releases
Bulk action to update release information for multiple apps:
1. Select apps in admin
2. Choose "Update GitHub releases" from Actions dropdown
3. Service fetches latest release data from GitHub API for each app

### View Release Information
Each ForgeApp in admin now shows:
- Release name and tag
- Release URLs (page and zip download)
- Last check timestamp
- Visual indicator if release is available

### Download Tracking
Purchase admin now displays:
- `download_count`: Total downloads by user
- `last_downloaded`: When user last downloaded

## Services

### GitHubReleaseService
**File**: `forge/github_release_service.py`

**Methods**:
- `get_latest_release(owner, repo)`: Fetch latest release from GitHub API
- `update_app_release_info(forge_app, force=False)`: Update app's release fields
- `download_release_zip(zip_url)`: Download release zip file

**GitHub API Requirements**:
- Token in settings: `GITHUB_API_TOKEN`
- API endpoint: `https://api.github.com/repos/{owner}/{repo}/releases/latest`
- Rate limit: 5000/hour (authenticated)

### LicenseDownloadService
**File**: `forge/download_service.py`

**Methods**:
- `generate_license_instructions(forge_app, purchase)`: Create LICENSE.md content
- `inject_license_into_zip(zip_data, license_content)`: Inject files into zip
- `create_licensed_download(forge_app, purchase)`: Full download workflow

**Process**:
1. Check if app has release data
2. Download release zip from GitHub
3. Generate LICENSE.md with purchase details
4. Create README_LICENSE.txt with instructions
5. Inject both files into zip using Python zipfile
6. Return modified zip bytes

## Serializer Updates

### ForgeAppDetailSerializer
Added fields:
- `demo_video_url`
- `video_type`
- `video_embed_url` (read-only property)
- `latest_release_name`
- `latest_release_tag`
- `latest_release_url`
- `has_release` (read-only property)

### ForgeAppListSerializer
Added fields:
- `has_release` (boolean indicator)

### PurchaseSerializer
Added fields:
- `download_count` (read-only)
- `last_downloaded` (read-only)
- `can_download` (computed boolean)

## Migration

**File**: `forge/migrations/0004_auto_20251204_2232.py`

**Operations**:
1. Add `demo_video_url` to ForgeApp (CharField, max_length=500, blank=True, null=True)
2. Add `last_release_check` to ForgeApp (DateTimeField, blank=True, null=True)
3. Add `latest_release_name` to ForgeApp (CharField, max_length=200, blank=True, null=True)
4. Add `latest_release_tag` to ForgeApp (CharField, max_length=100, blank=True, null=True)
5. Add `latest_release_url` to ForgeApp (CharField, max_length=500, blank=True, null=True)
6. Add `latest_release_zip_url` to ForgeApp (CharField, max_length=500, blank=True, null=True)
7. Add `video_type` to ForgeApp (CharField, max_length=20, choices=['youtube', 'vimeo', 'loom'], blank=True, null=True)
8. Add `download_count` to Purchase (IntegerField, default=0)
9. Add `last_downloaded` to Purchase (DateTimeField, blank=True, null=True)
10. Alter `screenshots` help_text on ForgeApp

**Status**: ✅ Applied to development database

## Configuration Required

### Settings
Add to `mysite/settings/base.py` or environment variables:
```python
# GitHub API token for release fetching
GITHUB_API_TOKEN = 'ghp_xxxxxxxxxxxxxxxxxxxxx'

# Optional: Override default organization
FORGE_MARKETPLACE_ORG = 'buildly-marketplace'
```

### GitHub Release Requirements
For an app to support downloads:
1. Repository must have at least one release
2. Release must include source code (GitHub auto-generates .zip)
3. `repo_url` must be configured on ForgeApp
4. Admin must trigger release update (bulk action or API endpoint)

## Security Considerations

### Download Authorization
- Only authenticated users can download
- User must own the purchase (verified in view)
- Purchase must have `status='completed'`
- Token authentication required

### GitHub API
- Uses authenticated requests (respects rate limits)
- Errors logged but don't expose API details to users
- 1-hour cache prevents excessive API calls

### License Injection
- No user input in license content (prevents injection attacks)
- All content generated from database models
- Zip manipulation done in-memory (no temp files)

## Error Handling

### No Release Available
Returns 400 Bad Request:
```json
{
  "error": "No repository configured for this app"
}
```

### Download Failure
Returns 500 Internal Server Error:
```json
{
  "error": "Failed to generate download. Please try again later."
}
```

Logged errors include:
- GitHub API failures
- Network issues downloading zip
- Zip manipulation errors

## Testing Checklist

- [ ] Create ForgeApp with `repo_url`
- [ ] Ensure repository has a release on GitHub
- [ ] Run admin action "Update GitHub releases"
- [ ] Verify release info displayed in admin
- [ ] Create test purchase with `status='completed'`
- [ ] Call download endpoint as purchase owner
- [ ] Verify zip contains LICENSE.md and README_LICENSE.txt
- [ ] Check download_count incremented
- [ ] Test with YouTube video URL
- [ ] Test with Vimeo video URL
- [ ] Verify video embed URL generation

## Future Enhancements

1. **Automated Release Checks**: Celery task to check for new releases daily
2. **Release Notifications**: Email users when new version available
3. **Multi-file License Injection**: Support multiple license files
4. **Custom License Templates**: Per-app license templates
5. **Download Analytics**: Track which versions are most popular
6. **Version Selection**: Let users download specific release versions
7. **Changelog Display**: Show release notes from GitHub
8. **Pre-release Support**: Beta/alpha releases for testers
