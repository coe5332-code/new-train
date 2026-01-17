# Version Control and Update Strategy Guide

## Overview

This document outlines the **Version Control and Update Strategy** implemented for the BSK Training Video Generator. The system ensures that training videos are automatically or systematically revised when source documents are updated.

## Core Components

### 1. Document Fingerprinting

Every source document (PDF) is assigned a unique **SHA-256 hash** based on its binary content. This hash serves as a "fingerprint" that uniquely identifies each version of a document.

- **Location**: `utils/version_utils.py` → `get_file_hash()`
- **Purpose**: Detect when a document has changed, even if the filename remains the same

### 2. Version Registry

A JSON-based registry (`version_registry.json`) tracks all service versions:

```json
{
  "services": {
    "Aadhaar_Card": {
      "service_name": "Aadhaar Card Update",
      "current_version": "2.0",
      "last_updated": "2024-05-20T10:30:00",
      "source_hash": "a1b2c3d4...",
      "video_path": "output_videos/BSK_Training_Aadhaar_Card_v2.0.mp4",
      "history": [
        {
          "version": "1.0",
          "hash": "z9y8x7...",
          "date": "2023-01-10T09:00:00"
        }
      ]
    }
  }
}
```

### 3. Version Detection Workflow

When a PDF is uploaded or form is submitted:

1. **Hash Calculation**: System calculates SHA-256 hash of the document
2. **Registry Lookup**: Checks if service exists in registry
3. **Version Comparison**: Compares new hash with existing hash
4. **Update Detection**: Flags if document has changed

**Status Codes**:
- `NEW_SERVICE`: First time creating video for this service
- `UP_TO_DATE`: Document matches existing version (same hash)
- `UPDATE_NEEDED`: Document has changed (different hash)

### 4. Update Strategy

#### Systematic Revision (Current Implementation)

When an update is detected:

1. **User Prompt**: Streamlit UI shows warning with current version info
2. **User Confirmation**: User clicks "Generate New Version" or "Cancel"
3. **Version Increment**: System automatically increments version (e.g., 1.0 → 1.1)
4. **Archive Old Version**: Previous video moved to `output_videos/archive/`
5. **Generate New Video**: New video created with version number in filename

#### Automatic Revision (Future Enhancement)

For automated updates:
- Background watcher service monitors source folders
- Automatically triggers regeneration when changes detected
- Can be implemented via scheduled jobs or file system watchers

## File Structure

```
train-video-main/
├── utils/
│   └── version_utils.py          # Version control utilities
├── version_registry.json         # Version tracking database
├── output_videos/
│   ├── BSK_Training_Service_v1.0.mp4
│   ├── BSK_Training_Service_v2.0.mp4
│   └── archive/                  # Old versions
│       └── Service_BSK_Training_Service_v1.0_20240520.mp4
└── app.py                        # Main Streamlit app (integrated)
```

## Usage

### Creating a New Video

1. Upload PDF or fill form
2. System checks for existing versions
3. If new service → Creates v1.0
4. If update detected → Prompts for confirmation → Creates new version

### Viewing Version History

1. Navigate to "📂 View Existing Videos"
2. Select a service from dropdown
3. View version history and metrics
4. Select specific version to preview/download

## API Reference

### `utils/version_utils.py`

#### `get_file_hash(file_bytes: bytes) -> str`
Calculate SHA-256 hash of document content.

#### `check_for_updates(service_name: str, new_hash: str) -> Tuple[str, Optional[Dict]]`
Check if document is new, updated, or unchanged.

#### `register_service_version(service_name, file_hash, video_path, ...) -> Dict`
Register a new version in the registry.

#### `get_version_history(service_name: str) -> list`
Get complete version history for a service.

#### `archive_old_version(service_name: str, old_video_path: str)`
Move old video to archive directory.

## Deployment Considerations

### Streamlit Cloud

1. **Persistent Storage**: `version_registry.json` is tracked in Git, so versions persist across deployments
2. **Video Storage**: Videos are stored in `output_videos/` (can be configured to use cloud storage)
3. **Archive Management**: Archive folder grows over time - consider periodic cleanup

### Docker Deployment

1. **Volume Mounting**: Mount `output_videos/` and `version_registry.json` to persistent volumes
2. **Backup Strategy**: Regularly backup `version_registry.json`

### Environment Variables

No additional environment variables required for version control system.

## Best Practices

1. **Always use PDF uploads** for consistent hashing (form-based generation creates hash from content string)
2. **Review version history** before generating updates to avoid duplicates
3. **Archive cleanup**: Periodically review and remove very old archived versions
4. **Registry backup**: Keep backups of `version_registry.json` for disaster recovery

## Troubleshooting

### Issue: Version not detected
- **Solution**: Check that service name matches exactly (normalization handles most cases)
- **Check**: Verify `version_registry.json` exists and is readable

### Issue: Old videos not archiving
- **Solution**: Check `output_videos/archive/` directory permissions
- **Check**: Verify old video path exists before archiving

### Issue: Registry file corrupted
- **Solution**: Restore from Git history or backup
- **Prevention**: Regular commits of `version_registry.json`

## Future Enhancements

1. **AI-Powered Diff Analysis**: Use Gemini to highlight what changed between versions
2. **Automatic Watchers**: Monitor Google Drive/GitHub for new policy PDFs
3. **Version Comparison UI**: Side-by-side comparison of video versions
4. **Rollback Feature**: Ability to revert to previous versions
5. **Version Notifications**: Email/Slack notifications when updates detected

## Support

For issues or questions about the version control system, refer to:
- `utils/version_utils.py` - Core implementation
- `app.py` - UI integration
- This guide - Documentation
