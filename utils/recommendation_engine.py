"""
Recommendation Engine for BSK Training Videos
Provides intelligent recommendations based on various factors
"""

from typing import List, Dict, Optional
from utils.video_repository import load_metadata, get_videos_by_category, SERVICE_CATEGORIES
from datetime import datetime, timedelta
import re


class RecommendationEngine:
    """Engine for generating video recommendations"""
    
    def __init__(self):
        self.videos = load_metadata()
    
    def refresh(self):
        """Refresh video data"""
        self.videos = load_metadata()
    
    def recommend_by_category(self, category: str, limit: int = 5) -> List[Dict]:
        """Recommend videos from a specific category"""
        category_videos = get_videos_by_category(category)
        
        # Sort by views and rating
        category_videos.sort(
            key=lambda x: (x.get("views", 0) * 0.3 + x.get("rating", 0.0) * 5, x.get("created_at", "")),
            reverse=True
        )
        
        return category_videos[:limit]
    
    def recommend_by_tags(self, tags: List[str], limit: int = 5) -> List[Dict]:
        """Recommend videos matching specific tags"""
        matching_videos = []
        
        for video in self.videos:
            video_tags = video.get("tags", [])
            match_score = sum(1 for tag in tags if tag in video_tags)
            
            if match_score > 0:
                video_copy = video.copy()
                video_copy["match_score"] = match_score
                matching_videos.append(video_copy)
        
        # Sort by match score, then by views/rating
        matching_videos.sort(
            key=lambda x: (
                x.get("match_score", 0),
                x.get("views", 0) * 0.3 + x.get("rating", 0.0) * 5
            ),
            reverse=True
        )
        
        return matching_videos[:limit]
    
    def recommend_popular(self, limit: int = 10) -> List[Dict]:
        """Recommend most popular videos"""
        popular = sorted(
            self.videos,
            key=lambda x: (
                x.get("views", 0) * 0.4 + 
                x.get("downloads", 0) * 0.3 + 
                x.get("rating", 0.0) * 3
            ),
            reverse=True
        )
        return popular[:limit]
    
    def recommend_recent(self, limit: int = 10) -> List[Dict]:
        """Recommend recently created videos"""
        recent = sorted(
            self.videos,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        return recent[:limit]
    
    def recommend_highly_rated(self, min_rating: float = 4.0, limit: int = 10) -> List[Dict]:
        """Recommend highly rated videos"""
        highly_rated = [
            v for v in self.videos 
            if v.get("rating", 0.0) >= min_rating and v.get("ratings_count", 0) >= 3
        ]
        highly_rated.sort(
            key=lambda x: (x.get("rating", 0.0), x.get("ratings_count", 0)),
            reverse=True
        )
        return highly_rated[:limit]
    
    def recommend_for_operator(self, operator_level: str = "beginner", limit: int = 5) -> List[Dict]:
        """Recommend videos based on operator experience level"""
        level_tags = {
            "beginner": ["beginner"],
            "intermediate": ["beginner", "intermediate"],
            "advanced": ["beginner", "intermediate", "advanced"]
        }
        
        tags = level_tags.get(operator_level.lower(), ["beginner"])
        return self.recommend_by_tags(tags, limit)
    
    def recommend_related(self, video_id: str, limit: int = 5) -> List[Dict]:
        """Recommend videos related to a specific video"""
        current_video = next((v for v in self.videos if v.get("video_id") == video_id), None)
        
        if not current_video:
            return []
        
        category = current_video.get("category")
        tags = current_video.get("tags", [])
        
        # Find videos in same category or with similar tags
        related = []
        for video in self.videos:
            if video.get("video_id") == video_id:
                continue
            
            score = 0
            if video.get("category") == category:
                score += 2
            
            video_tags = video.get("tags", [])
            common_tags = set(tags) & set(video_tags)
            score += len(common_tags)
            
            if score > 0:
                video_copy = video.copy()
                video_copy["related_score"] = score
                related.append(video_copy)
        
        related.sort(key=lambda x: x.get("related_score", 0), reverse=True)
        return related[:limit]
    
    def search_videos(self, query: str, limit: int = 10) -> List[Dict]:
        """Search videos by service name or description"""
        query_lower = query.lower()
        results = []
        
        for video in self.videos:
            score = 0
            service_name = video.get("service_name", "").lower()
            description = video.get("description", "").lower()
            
            # Exact match in service name (highest priority)
            if query_lower in service_name:
                score += 10
            
            # Partial match in service name
            if any(word in service_name for word in query_lower.split()):
                score += 5
            
            # Match in description
            if query_lower in description:
                score += 3
            
            # Match in tags
            tags = [tag.lower() for tag in video.get("tags", [])]
            if any(word in " ".join(tags) for word in query_lower.split()):
                score += 2
            
            if score > 0:
                video_copy = video.copy()
                video_copy["search_score"] = score
                results.append(video_copy)
        
        results.sort(key=lambda x: x.get("search_score", 0), reverse=True)
        return results[:limit]
    
    def recommend_by_difficulty(self, difficulty: str, limit: int = 5) -> List[Dict]:
        """Recommend videos by difficulty level"""
        difficulty_map = {
            "beginner": "beginner",
            "easy": "beginner",
            "intermediate": "intermediate",
            "medium": "intermediate",
            "advanced": "advanced",
            "hard": "advanced"
        }
        
        target_tag = difficulty_map.get(difficulty.lower(), "beginner")
        return self.recommend_by_tags([target_tag], limit)
    
    def get_category_recommendations(self) -> Dict[str, List[Dict]]:
        """Get top recommendations for each category"""
        recommendations = {}
        
        for category_id in SERVICE_CATEGORIES.keys():
            category_videos = get_videos_by_category(category_id)
            if category_videos:
                # Sort by popularity
                category_videos.sort(
                    key=lambda x: (
                        x.get("views", 0) * 0.4 + 
                        x.get("rating", 0.0) * 5
                    ),
                    reverse=True
                )
                recommendations[category_id] = category_videos[:3]  # Top 3 per category
        
        return recommendations
    
    def get_personalized_recommendations(
        self,
        viewed_videos: List[str] = None,
        preferred_categories: List[str] = None,
        operator_level: str = "beginner",
        limit: int = 10
    ) -> List[Dict]:
        """Generate personalized recommendations based on user behavior"""
        if viewed_videos is None:
            viewed_videos = []
        if preferred_categories is None:
            preferred_categories = []
        
        scored_videos = []
        
        for video in self.videos:
            if video.get("video_id") in viewed_videos:
                continue  # Skip already viewed
            
            score = 0
            
            # Boost score for preferred categories
            if video.get("category") in preferred_categories:
                score += 5
            
            # Boost score for operator level match
            video_tags = video.get("tags", [])
            if operator_level.lower() in video_tags:
                score += 3
            
            # Boost score for popular videos
            score += video.get("views", 0) * 0.001
            score += video.get("rating", 0.0) * 0.5
            
            # Boost score for recent videos
            try:
                created_at = datetime.fromisoformat(video.get("created_at", ""))
                days_old = (datetime.now() - created_at).days
                if days_old < 30:
                    score += 2
            except:
                pass
            
            if score > 0:
                video_copy = video.copy()
                video_copy["personalized_score"] = score
                scored_videos.append(video_copy)
        
        scored_videos.sort(key=lambda x: x.get("personalized_score", 0), reverse=True)
        return scored_videos[:limit]
