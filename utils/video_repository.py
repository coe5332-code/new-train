"""
Video Repository Module
Stores and manages metadata for training videos to enable recommendations
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import hashlib


# Repository storage paths
REPO_DIR = "video_repository"
METADATA_FILE = os.path.join(REPO_DIR, "videos_metadata.json")
CATEGORIES_FILE = os.path.join(REPO_DIR, "categories.json")


# Service categories for BSK training
SERVICE_CATEGORIES = {
    "identity": {
        "name": "Identity Services",
        "keywords": ["aadhaar", "pan", "voter", "id", "identity", "card", "certificate"],
        "icon": "🆔"
    },
    "education": {
        "name": "Education Services",
        "keywords": ["education", "scholarship", "admission", "certificate", "degree", "school"],
        "icon": "📚"
    },
    "healthcare": {
        "name": "Healthcare Services",
        "keywords": ["health", "medical", "hospital", "treatment", "insurance", "healthcard"],
        "icon": "🏥"
    },
    "employment": {
        "name": "Employment Services",
        "keywords": ["job", "employment", "work", "salary", "pension", "retirement"],
        "icon": "💼"
    },
    "housing": {
        "name": "Housing Services",
        "keywords": ["house", "housing", "property", "land", "registration", "ownership"],
        "icon": "🏠"
    },
    "financial": {
        "name": "Financial Services",
        "keywords": ["bank", "loan", "financial", "pension", "benefit", "subsidy"],
        "icon": "💰"
    },
    "legal": {
        "name": "Legal Services",
        "keywords": ["legal", "court", "law", "certificate", "document", "affidavit"],
        "icon": "⚖️"
    },
    "transport": {
        "name": "Transport Services",
        "keywords": ["vehicle", "license", "driving", "registration", "transport", "permit"],
        "icon": "🚗"
    },
    "utility": {
        "name": "Utility Services",
        "keywords": ["electricity", "water", "gas", "connection", "bill", "utility"],
        "icon": "⚡"
    },
    "general": {
        "name": "General Services",
        "keywords": [],
        "icon": "📋"
    }
}


def initialize_repository():
    """Initialize the video repository directory and files"""
    os.makedirs(REPO_DIR, exist_ok=True)
    
    # Initialize metadata file if it doesn't exist
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"videos": [], "last_updated": datetime.now().isoformat()}, f, indent=2)
    
    # Initialize categories file
    if not os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(SERVICE_CATEGORIES, f, indent=2)


def load_metadata() -> Dict:
    """Load all video metadata from repository"""
    initialize_repository()
    try:
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("videos", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_metadata(videos: List[Dict]):
    """Save video metadata to repository"""
    initialize_repository()
    data = {
        "videos": videos,
        "last_updated": datetime.now().isoformat()
    }
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def categorize_service(service_name: str, description: str = "") -> str:
    """Automatically categorize a service based on name and description"""
    text = (service_name + " " + description).lower()
    
    best_match = "general"
    max_matches = 0
    
    for category_id, category_info in SERVICE_CATEGORIES.items():
        if category_id == "general":
            continue
        
        matches = sum(1 for keyword in category_info["keywords"] if keyword in text)
        if matches > max_matches:
            max_matches = matches
            best_match = category_id
    
    return best_match


def extract_tags(service_name: str, description: str, content: Dict) -> List[str]:
    """Extract relevant tags from service information"""
    tags = []
    text = (service_name + " " + description).lower()
    
    # Add category-based tags
    category = categorize_service(service_name, description)
    tags.append(category)
    
    # Add content-based tags
    if content.get("eligibility_criteria"):
        tags.append("eligibility")
    if content.get("required_docs"):
        tags.append("documents")
    if content.get("how_to_apply"):
        tags.append("application")
    if content.get("operator_tips"):
        tags.append("operator-tips")
    if content.get("troubleshooting"):
        tags.append("troubleshooting")
    if content.get("service_link"):
        tags.append("online")
    
    # Add difficulty level based on content complexity
    word_count = len(description.split()) + len(content.get("how_to_apply", "").split())
    if word_count > 500:
        tags.append("advanced")
    elif word_count > 200:
        tags.append("intermediate")
    else:
        tags.append("beginner")
    
    return list(set(tags))  # Remove duplicates


def generate_video_id(service_name: str, timestamp: str) -> str:
    """Generate a unique video ID"""
    unique_string = f"{service_name}_{timestamp}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:12]


def register_video(
    video_path: str,
    service_name: str,
    service_content: Dict,
    slides_count: int = 0,
    duration: float = 0.0,
    voice: str = "en-IN-NeerjaNeural"
) -> Dict:
    """Register a new video in the repository with metadata"""
    videos = load_metadata()
    
    # Check if video already exists
    video_filename = os.path.basename(video_path)
    existing = next((v for v in videos if v.get("filename") == video_filename), None)
    
    if existing:
        # Update existing entry
        video_metadata = existing
        video_metadata["updated_at"] = datetime.now().isoformat()
    else:
        # Create new entry
        timestamp = datetime.now().isoformat()
        video_metadata = {
            "video_id": generate_video_id(service_name, timestamp),
            "filename": video_filename,
            "file_path": video_path,
            "service_name": service_name,
            "description": service_content.get("service_description", ""),
            "category": categorize_service(service_name, service_content.get("service_description", "")),
            "tags": extract_tags(service_name, service_content.get("service_description", ""), service_content),
            "slides_count": slides_count,
            "duration": duration,
            "voice": voice,
            "created_at": timestamp,
            "updated_at": timestamp,
            "views": 0,
            "downloads": 0,
            "rating": 0.0,
            "ratings_count": 0,
            "service_link": service_content.get("service_link", ""),
            "fees_timeline": service_content.get("fees_and_timeline", ""),
            "has_operator_tips": bool(service_content.get("operator_tips")),
            "has_troubleshooting": bool(service_content.get("troubleshooting")),
        }
        videos.append(video_metadata)
    
    save_metadata(videos)
    return video_metadata


def get_video_by_id(video_id: str) -> Optional[Dict]:
    """Get video metadata by ID"""
    videos = load_metadata()
    return next((v for v in videos if v.get("video_id") == video_id), None)


def get_videos_by_category(category: str) -> List[Dict]:
    """Get all videos in a specific category"""
    videos = load_metadata()
    return [v for v in videos if v.get("category") == category]


def get_all_videos(sort_by: str = "created_at", reverse: bool = True) -> List[Dict]:
    """Get all videos, sorted"""
    videos = load_metadata()
    
    if sort_by == "views":
        videos.sort(key=lambda x: x.get("views", 0), reverse=reverse)
    elif sort_by == "rating":
        videos.sort(key=lambda x: x.get("rating", 0.0), reverse=reverse)
    elif sort_by == "service_name":
        videos.sort(key=lambda x: x.get("service_name", "").lower(), reverse=reverse)
    else:  # created_at
        videos.sort(key=lambda x: x.get("created_at", ""), reverse=reverse)
    
    return videos


def increment_views(video_id: str):
    """Increment view count for a video"""
    videos = load_metadata()
    for video in videos:
        if video.get("video_id") == video_id:
            video["views"] = video.get("views", 0) + 1
            video["updated_at"] = datetime.now().isoformat()
            break
    save_metadata(videos)


def increment_downloads(video_id: str):
    """Increment download count for a video"""
    videos = load_metadata()
    for video in videos:
        if video.get("video_id") == video_id:
            video["downloads"] = video.get("downloads", 0) + 1
            video["updated_at"] = datetime.now().isoformat()
            break
    save_metadata(videos)


def update_rating(video_id: str, rating: float):
    """Update video rating"""
    videos = load_metadata()
    for video in videos:
        if video.get("video_id") == video_id:
            current_rating = video.get("rating", 0.0)
            ratings_count = video.get("ratings_count", 0)
            
            # Calculate new average rating
            new_ratings_count = ratings_count + 1
            new_rating = ((current_rating * ratings_count) + rating) / new_ratings_count
            
            video["rating"] = round(new_rating, 1)
            video["ratings_count"] = new_ratings_count
            video["updated_at"] = datetime.now().isoformat()
            break
    save_metadata(videos)


def get_statistics() -> Dict:
    """Get repository statistics"""
    videos = load_metadata()
    
    if not videos:
        return {
            "total_videos": 0,
            "total_views": 0,
            "total_downloads": 0,
            "categories": {},
            "average_rating": 0.0
        }
    
    total_views = sum(v.get("views", 0) for v in videos)
    total_downloads = sum(v.get("downloads", 0) for v in videos)
    
    # Category distribution
    categories = {}
    for video in videos:
        cat = video.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
    
    # Average rating
    rated_videos = [v for v in videos if v.get("ratings_count", 0) > 0]
    avg_rating = sum(v.get("rating", 0.0) for v in rated_videos) / len(rated_videos) if rated_videos else 0.0
    
    return {
        "total_videos": len(videos),
        "total_views": total_views,
        "total_downloads": total_downloads,
        "categories": categories,
        "average_rating": round(avg_rating, 1)
    }
