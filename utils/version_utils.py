"""
Version Control and Update Strategy Module
Handles document fingerprinting, version detection, and update management
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path


# Registry file path
REGISTRY_FILE = "version_registry.json"
ARCHIVE_DIR = "output_videos/archive"


def initialize_registry():
    """Initialize the version registry file if it doesn't exist"""
    if not os.path.exists(REGISTRY_FILE):
        registry = {
            "services": {},
            "last_updated": datetime.now().isoformat(),
            "schema_version": "1.0"
        }
        save_registry(registry)
        return registry
    return load_registry()


def load_registry() -> Dict:
    """Load the version registry from JSON file"""
    try:
        if os.path.exists(REGISTRY_FILE):
            with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load registry: {e}. Creating new one.")
    
    return initialize_registry()


def save_registry(registry: Dict):
    """Save the version registry to JSON file"""
    registry["last_updated"] = datetime.now().isoformat()
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def get_file_hash(file_bytes: bytes) -> str:
    """
    Generates a unique SHA-256 hash for the uploaded file content.
    This serves as the document fingerprint.
    """
    return hashlib.sha256(file_bytes).hexdigest()


def normalize_service_name(service_name: str) -> str:
    """Normalize service name for consistent registry lookup"""
    # Remove special characters and convert to consistent format
    normalized = service_name.strip().replace(" ", "_").replace("-", "_")
    # Remove multiple underscores
    normalized = "_".join(filter(None, normalized.split("_")))
    return normalized


def get_next_version(current_version: str) -> str:
    """
    Increment version number.
    Supports formats: "1.0", "1.1", "2.0", etc.
    """
    try:
        parts = current_version.split(".")
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        
        # Increment minor version
        minor += 1
        
        # If minor exceeds 9, increment major
        if minor > 9:
            major += 1
            minor = 0
        
        return f"{major}.{minor}"
    except (ValueError, IndexError):
        # If version format is invalid, start at 1.0
        return "1.0"


def check_for_updates(service_name: str, new_hash: str, registry: Optional[Dict] = None) -> Tuple[str, Optional[Dict]]:
    """
    Determines if the uploaded file is a new version or the same.
    
    Returns:
        Tuple[str, Optional[Dict]]: 
            - Status: "NEW_SERVICE", "UP_TO_DATE", or "UPDATE_NEEDED"
            - Existing service data (if found)
    """
    if registry is None:
        registry = load_registry()
    
    normalized_name = normalize_service_name(service_name)
    services = registry.get("services", {})
    
    # Check if service exists
    if normalized_name not in services:
        return "NEW_SERVICE", None
    
    service_data = services[normalized_name]
    existing_hash = service_data.get("source_hash")
    
    # Compare hashes
    if existing_hash == new_hash:
        return "UP_TO_DATE", service_data
    else:
        return "UPDATE_NEEDED", service_data


def register_service_version(
    service_name: str,
    file_hash: str,
    video_path: str,
    pdf_path: Optional[str] = None,
    source_type: str = "uploaded"
) -> Dict:
    """
    Register a new version of a service in the registry.
    
    Args:
        service_name: Name of the service
        file_hash: SHA-256 hash of the source document
        video_path: Path to the generated video
        pdf_path: Optional path to the source PDF
        source_type: Type of source ("uploaded" or "generated")
    
    Returns:
        Dict: Updated service data
    """
    registry = load_registry()
    normalized_name = normalize_service_name(service_name)
    services = registry.setdefault("services", {})
    
    # Check if this is an update or new service
    status, existing_data = check_for_updates(service_name, file_hash, registry)
    
    if status == "UPDATE_NEEDED" and existing_data:
        # Archive old video
        archive_old_version(normalized_name, existing_data.get("video_path"))
        
        # Increment version
        current_version = existing_data.get("current_version", "1.0")
        new_version = get_next_version(current_version)
        
        # Update history
        history = existing_data.get("history", [])
        history.append({
            "version": existing_data.get("current_version", "1.0"),
            "hash": existing_data.get("source_hash"),
            "video_path": existing_data.get("video_path"),
            "date": existing_data.get("last_updated", datetime.now().isoformat())
        })
        
        # Update service data
        service_data = {
            "service_name": service_name,
            "normalized_name": normalized_name,
            "current_version": new_version,
            "last_updated": datetime.now().isoformat(),
            "source_hash": file_hash,
            "video_path": video_path,
            "pdf_path": pdf_path,
            "source_type": source_type,
            "history": history,
            "created_at": existing_data.get("created_at", datetime.now().isoformat())
        }
    elif status == "UP_TO_DATE":
        # Same version, just update metadata
        service_data = existing_data.copy()
        service_data["last_updated"] = datetime.now().isoformat()
        service_data["video_path"] = video_path
        if pdf_path:
            service_data["pdf_path"] = pdf_path
    else:
        # New service
        service_data = {
            "service_name": service_name,
            "normalized_name": normalized_name,
            "current_version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "source_hash": file_hash,
            "video_path": video_path,
            "pdf_path": pdf_path,
            "source_type": source_type,
            "history": []
        }
    
    services[normalized_name] = service_data
    save_registry(registry)
    
    return service_data


def archive_old_version(service_name: str, old_video_path: Optional[str]):
    """Move old video to archive directory"""
    if not old_video_path or not os.path.exists(old_video_path):
        return
    
    try:
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        filename = os.path.basename(old_video_path)
        archive_path = os.path.join(ARCHIVE_DIR, f"{service_name}_{filename}")
        
        # If archive path exists, add timestamp
        if os.path.exists(archive_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(filename)
            archive_path = os.path.join(ARCHIVE_DIR, f"{service_name}_{name}_{timestamp}{ext}")
        
        os.rename(old_video_path, archive_path)
        return archive_path
    except Exception as e:
        print(f"Warning: Could not archive old version: {e}")
        return None


def get_service_info(service_name: str) -> Optional[Dict]:
    """Get version information for a specific service"""
    registry = load_registry()
    normalized_name = normalize_service_name(service_name)
    services = registry.get("services", {})
    return services.get(normalized_name)


def get_all_services() -> Dict[str, Dict]:
    """Get all registered services with their version info"""
    registry = load_registry()
    return registry.get("services", {})


def get_version_history(service_name: str) -> list:
    """Get version history for a service"""
    service_info = get_service_info(service_name)
    if not service_info:
        return []
    
    history = service_info.get("history", [])
    # Add current version to history display
    current = {
        "version": service_info.get("current_version", "1.0"),
        "hash": service_info.get("source_hash"),
        "video_path": service_info.get("video_path"),
        "date": service_info.get("last_updated"),
        "is_current": True
    }
    
    return [current] + [dict(h, is_current=False) for h in history]


def compare_documents(old_hash: str, new_hash: str) -> Dict:
    """
    Compare two document versions.
    Returns comparison metadata (for future AI-powered diff analysis).
    """
    return {
        "old_hash": old_hash,
        "new_hash": new_hash,
        "has_changes": old_hash != new_hash,
        "comparison_date": datetime.now().isoformat()
    }
