"""
Advanced Personalization & Recommendation Engines

ML-powered recommendations with user profiling, multiple recommendation types,
real-time personalization, and adaptive content delivery.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import defaultdict, Counter
import math
from pathlib import Path
import pickle

from config.logging_config import setup_logger


class RecommendationType(Enum):
    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"
    CONTEXTUAL = "contextual"
    TREND_BASED = "trend_based"


class ContentType(Enum):
    TASK = "task"
    DOCUMENT = "document"
    PROJECT = "project"
    WORKFLOW = "workflow"
    TOOL = "tool"
    LEARNING_RESOURCE = "learning_resource"
    TEAM_MEMBER = "team_member"


@dataclass
class UserProfile:
    """User profile for personalization"""
    user_id: str
    preferences: Dict[str, Any]
    behavior_history: List[Dict[str, Any]]
    skill_levels: Dict[str, float]
    interests: Set[str]
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.last_updated:
            self.last_updated = datetime.now()


@dataclass
class ContentItem:
    """Content item for recommendations"""
    item_id: str
    content_type: ContentType
    title: str
    description: str
    tags: Set[str]
    features: Dict[str, Any]
    popularity_score: float = 0.0
    created_at: Optional[datetime] = None
    embeddings: Optional[np.ndarray] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()


@dataclass
class UserInteraction:
    """User interaction with content"""
    user_id: str
    item_id: str
    interaction_type: str  # view, like, complete, share, etc.
    rating: Optional[float] = None
    duration: Optional[int] = None  # seconds
    context: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()


@dataclass
class Recommendation:
    """Recommendation result"""
    recommendation_id: str
    user_id: str
    item_id: str
    score: float
    reason: str
    recommendation_type: RecommendationType
    context_factors: Dict[str, Any]
    generated_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now()


class PersonalizationRecommendationEngine:
    """Advanced Personalization & Recommendation Engine"""

    def __init__(self):
        self.logger = setup_logger("PersonalizationEngine")
        self.user_profiles: Dict[str, UserProfile] = {}
        self.content_items: Dict[str, ContentItem] = {}
        self.interactions: List[UserInteraction] = []
        self.user_item_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.content_embeddings: Dict[str, np.ndarray] = {}
        self.similarity_cache: Dict[Tuple[str, str], float] = {}

    async def initialize(self):
        """Initialize the personalization engine"""
        self.logger.info("Initializing Personalization & Recommendation Engine...")

        # Load or create initial data structures
        await self._load_data()

        # Pre-compute content embeddings if needed
        await self._build_content_embeddings()

        self.logger.info("Personalization engine initialized")

    async def _load_data(self):
        """Load existing data or create empty structures"""
        # In a real implementation, this would load from database
        # For now, we'll work with in-memory data
        pass

    async def _build_content_embeddings(self):
        """Build embeddings for content items"""
        try:
            # Simple TF-IDF style embeddings for demonstration
            all_tags = set()
            for item in self.content_items.values():
                all_tags.update(item.tags)

            tag_to_index = {tag: i for i, tag in enumerate(all_tags)}

            for item_id, item in self.content_items.items():
                # Create simple bag-of-tags embedding
                embedding = np.zeros(len(all_tags))
                for tag in item.tags:
                    embedding[tag_to_index[tag]] = 1.0

                # Normalize
                if np.linalg.norm(embedding) > 0:
                    embedding = embedding / np.linalg.norm(embedding)

                self.content_embeddings[item_id] = embedding
                item.embeddings = embedding

        except Exception as e:
            self.logger.error(f"Error building content embeddings: {e}")

    async def generate_recommendations(self, user_id: str, recommendation_type: str,
                                     user_data: Dict[str, Any],
                                     options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate personalized recommendations"""
        try:
            rec_type = RecommendationType(recommendation_type)

            # Ensure user profile exists
            if user_id not in self.user_profiles:
                await self._create_user_profile(user_id, user_data)

            # Update user profile with new data
            await self._update_user_profile(user_id, user_data)

            recommendations = []

            if rec_type == RecommendationType.CONTENT_BASED:
                recommendations = await self._content_based_recommendations(user_id, options)
            elif rec_type == RecommendationType.COLLABORATIVE:
                recommendations = await self._collaborative_filtering_recommendations(user_id, options)
            elif rec_type == RecommendationType.HYBRID:
                recommendations = await self._hybrid_recommendations(user_id, options)
            elif rec_type == RecommendationType.CONTEXTUAL:
                recommendations = await self._contextual_recommendations(user_id, user_data, options)
            elif rec_type == RecommendationType.TREND_BASED:
                recommendations = await self._trend_based_recommendations(user_id, options)

            # Apply diversity and business rules
            recommendations = await self._apply_recommendation_filters(recommendations, options)

            return {
                "user_id": user_id,
                "recommendation_type": rec_type.value,
                "recommendations": [asdict(rec) for rec in recommendations],
                "total_recommendations": len(recommendations),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return {"error": str(e)}

    async def _create_user_profile(self, user_id: str, user_data: Dict[str, Any]):
        """Create a new user profile"""
        profile = UserProfile(
            user_id=user_id,
            preferences=user_data.get("preferences", {}),
            behavior_history=[],
            skill_levels=user_data.get("skill_levels", {}),
            interests=set(user_data.get("interests", []))
        )

        self.user_profiles[user_id] = profile
        self.logger.info(f"Created user profile for {user_id}")

    async def _update_user_profile(self, user_id: str, user_data: Dict[str, Any]):
        """Update existing user profile with new data"""
        if user_id not in self.user_profiles:
            await self._create_user_profile(user_id, user_data)
            return

        profile = self.user_profiles[user_id]

        # Update preferences
        if "preferences" in user_data:
            profile.preferences.update(user_data["preferences"])

        # Update skill levels
        if "skill_levels" in user_data:
            profile.skill_levels.update(user_data["skill_levels"])

        # Update interests
        if "interests" in user_data:
            profile.interests.update(user_data["interests"])

        # Add to behavior history
        interaction = UserInteraction(
            user_id=user_id,
            item_id=user_data.get("current_item", ""),
            interaction_type=user_data.get("interaction_type", "view"),
            context=user_data.get("context", {})
        )
        profile.behavior_history.append(asdict(interaction))
        self.interactions.append(interaction)

        profile.last_updated = datetime.now()

    async def _content_based_recommendations(self, user_id: str,
                                           options: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """Generate content-based recommendations"""
        profile = self.user_profiles[user_id]
        max_recommendations = options.get("max_recommendations", 10) if options else 10

        recommendations = []
        user_interests = profile.interests

        for item_id, item in self.content_items.items():
            # Skip items the user has already interacted with heavily
            user_interactions = [i for i in self.interactions
                               if i.user_id == user_id and i.item_id == item_id]
            if user_interactions:
                continue

            # Calculate similarity based on tag overlap
            tag_similarity = len(user_interests.intersection(item.tags)) / len(user_interests.union(item.tags)) if user_interests.union(item.tags) else 0

            # Calculate preference similarity
            preference_score = 0
            if profile.preferences:
                for pref_key, pref_value in profile.preferences.items():
                    if pref_key in item.features:
                        if item.features[pref_key] == pref_value:
                            preference_score += 1
                preference_score /= len(profile.preferences) if profile.preferences else 1

            # Combined score
            score = (tag_similarity * 0.7) + (preference_score * 0.3)

            if score > 0.1:  # Minimum threshold
                recommendation = Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    user_id=user_id,
                    item_id=item_id,
                    score=score,
                    reason=f"Content matches your interests in {', '.join(user_interests.intersection(item.tags))}",
                    recommendation_type=RecommendationType.CONTENT_BASED,
                    context_factors={
                        "tag_similarity": tag_similarity,
                        "preference_match": preference_score
                    }
                )
                recommendations.append(recommendation)

        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:max_recommendations]

    async def _collaborative_filtering_recommendations(self, user_id: str,
                                                     options: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """Generate collaborative filtering recommendations"""
        max_recommendations = options.get("max_recommendations", 10) if options else 10

        # Find similar users
        similar_users = await self._find_similar_users(user_id, top_k=5)

        recommendations = []

        # Get items liked by similar users
        candidate_items = set()
        for similar_user_id, similarity in similar_users:
            user_interactions = [i for i in self.interactions
                               if i.user_id == similar_user_id and i.rating and i.rating > 3.0]
            candidate_items.update([i.item_id for i in user_interactions])

        # Remove items the user has already interacted with
        user_items = set([i.item_id for i in self.interactions if i.user_id == user_id])
        candidate_items = candidate_items - user_items

        # Score items based on similar user preferences
        for item_id in candidate_items:
            if item_id not in self.content_items:
                continue

            item_score = 0
            contributing_users = []

            for similar_user_id, similarity in similar_users:
                user_rating = None
                for interaction in self.interactions:
                    if (interaction.user_id == similar_user_id and
                        interaction.item_id == item_id and
                        interaction.rating):
                        user_rating = interaction.rating
                        break

                if user_rating:
                    item_score += similarity * user_rating
                    contributing_users.append(similar_user_id)

            if item_score > 0:
                item_score /= len(contributing_users) if contributing_users else 1

                recommendation = Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    user_id=user_id,
                    item_id=item_id,
                    score=min(item_score / 5.0, 1.0),  # Normalize to 0-1
                    reason=f"Recommended by {len(contributing_users)} similar users",
                    recommendation_type=RecommendationType.COLLABORATIVE,
                    context_factors={
                        "similar_users_count": len(contributing_users),
                        "average_similarity": np.mean([s for _, s in similar_users])
                    }
                )
                recommendations.append(recommendation)

        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:max_recommendations]

    async def _find_similar_users(self, user_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find users similar to the given user"""
        if user_id not in self.user_profiles:
            return []

        target_profile = self.user_profiles[user_id]
        similarities = []

        for other_id, other_profile in self.user_profiles.items():
            if other_id == user_id:
                continue

            # Calculate similarity based on interests overlap
            interest_similarity = (len(target_profile.interests.intersection(other_profile.interests)) /
                                 len(target_profile.interests.union(other_profile.interests))
                                 if target_profile.interests.union(other_profile.interests) else 0)

            # Calculate similarity based on skill levels
            skill_similarity = 0
            common_skills = set(target_profile.skill_levels.keys()).intersection(
                          set(other_profile.skill_levels.keys()))

            if common_skills:
                skill_diffs = []
                for skill in common_skills:
                    diff = abs(target_profile.skill_levels[skill] - other_profile.skill_levels[skill])
                    skill_diffs.append(1.0 - (diff / 10.0))  # Normalize difference
                skill_similarity = np.mean(skill_diffs)

            # Combined similarity
            total_similarity = (interest_similarity * 0.6) + (skill_similarity * 0.4)

            similarities.append((other_id, total_similarity))

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    async def _hybrid_recommendations(self, user_id: str,
                                    options: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """Generate hybrid recommendations combining multiple approaches"""
        max_recommendations = options.get("max_recommendations", 10) if options else 10

        # Get content-based recommendations
        content_based = await self._content_based_recommendations(user_id, {"max_recommendations": max_recommendations * 2})

        # Get collaborative recommendations
        collaborative = await self._collaborative_filtering_recommendations(user_id, {"max_recommendations": max_recommendations * 2})

        # Combine and re-rank
        all_candidates = {rec.item_id: rec for rec in content_based}
        for rec in collaborative:
            if rec.item_id in all_candidates:
                # Average the scores if item appears in both
                existing = all_candidates[rec.item_id]
                existing.score = (existing.score + rec.score) / 2
                existing.reason += f" and {rec.reason}"
            else:
                all_candidates[rec.item_id] = rec

        recommendations = list(all_candidates.values())
        recommendations.sort(key=lambda x: x.score, reverse=True)

        return recommendations[:max_recommendations]

    async def _contextual_recommendations(self, user_id: str, user_data: Dict[str, Any],
                                        options: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """Generate context-aware recommendations"""
        context = user_data.get("context", {})
        current_time = datetime.now()

        recommendations = []

        # Time-based recommendations
        hour = current_time.hour
        if 9 <= hour <= 12:
            time_context = "morning_productivity"
        elif 12 <= hour <= 17:
            time_context = "afternoon_work"
        else:
            time_context = "evening_planning"

        # Context-based filtering
        for item_id, item in self.content_items.items():
            context_score = 0
            reasons = []

            # Time context matching
            if time_context == "morning_productivity" and "productivity" in item.tags:
                context_score += 0.3
                reasons.append("Good for morning productivity")
            elif time_context == "afternoon_work" and "collaboration" in item.tags:
                context_score += 0.3
                reasons.append("Suitable for afternoon collaboration")
            elif time_context == "evening_planning" and "planning" in item.tags:
                context_score += 0.3
                reasons.append("Perfect for evening planning")

            # Location context
            location = context.get("location")
            if location and location in item.tags:
                context_score += 0.2
                reasons.append(f"Relevant to your location: {location}")

            # Device context
            device = context.get("device")
            if device == "mobile" and "mobile_friendly" in item.features:
                context_score += 0.2
                reasons.append("Optimized for mobile use")

            if context_score > 0:
                recommendation = Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    user_id=user_id,
                    item_id=item_id,
                    score=context_score,
                    reason="; ".join(reasons),
                    recommendation_type=RecommendationType.CONTEXTUAL,
                    context_factors={
                        "time_context": time_context,
                        "location": location,
                        "device": device
                    }
                )
                recommendations.append(recommendation)

        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:options.get("max_recommendations", 10) if options else 10]

    async def _trend_based_recommendations(self, user_id: str,
                                         options: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """Generate trend-based recommendations"""
        # Analyze recent interactions to find trending items
        recent_interactions = [i for i in self.interactions
                             if (datetime.now() - i.timestamp).days <= 7]

        # Count interactions per item
        item_counts = Counter([i.item_id for i in recent_interactions])

        recommendations = []
        for item_id, interaction_count in item_counts.most_common(10):
            if item_id in self.content_items:
                trend_score = min(interaction_count / 10.0, 1.0)  # Normalize

                recommendation = Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    user_id=user_id,
                    item_id=item_id,
                    score=trend_score,
                    reason=f"Trending item with {interaction_count} recent interactions",
                    recommendation_type=RecommendationType.TREND_BASED,
                    context_factors={
                        "recent_interactions": interaction_count,
                        "trend_period_days": 7
                    }
                )
                recommendations.append(recommendation)

        return recommendations

    async def _apply_recommendation_filters(self, recommendations: List[Recommendation],
                                          options: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """Apply business rules and diversity filters"""
        if not recommendations:
            return recommendations

        # Remove duplicates
        seen_items = set()
        filtered = []
        for rec in recommendations:
            if rec.item_id not in seen_items:
                filtered.append(rec)
                seen_items.add(rec.item_id)

        # Apply diversity (ensure different content types)
        content_types = set()
        diverse = []
        for rec in filtered:
            item = self.content_items.get(rec.item_id)
            if item and item.content_type not in content_types:
                diverse.append(rec)
                content_types.add(item.content_type)
                if len(diverse) >= (options.get("max_recommendations", 10) if options else 10):
                    break

        # If we don't have enough diverse recommendations, fill with remaining
        if len(diverse) < len(filtered):
            remaining = [rec for rec in filtered if rec not in diverse]
            diverse.extend(remaining[: (options.get("max_recommendations", 10) - len(diverse)) if options else (10 - len(diverse))])

        return diverse

    async def add_content_item(self, item_data: Dict[str, Any]) -> str:
        """Add a new content item to the system"""
        item_id = str(uuid.uuid4())

        item = ContentItem(
            item_id=item_id,
            content_type=ContentType(item_data.get("content_type", "task")),
            title=item_data["title"],
            description=item_data.get("description", ""),
            tags=set(item_data.get("tags", [])),
            features=item_data.get("features", {}),
            popularity_score=item_data.get("popularity_score", 0.0)
        )

        self.content_items[item_id] = item

        # Rebuild embeddings
        await self._build_content_embeddings()

        return item_id

    async def record_interaction(self, interaction_data: Dict[str, Any]):
        """Record a user interaction"""
        interaction = UserInteraction(
            user_id=interaction_data["user_id"],
            item_id=interaction_data["item_id"],
            interaction_type=interaction_data["interaction_type"],
            rating=interaction_data.get("rating"),
            duration=interaction_data.get("duration"),
            context=interaction_data.get("context", {})
        )

        self.interactions.append(interaction)

        # Update user-item matrix
        rating = interaction.rating or (1.0 if interaction.interaction_type in ["like", "complete"] else 0.5)
        self.user_item_matrix[interaction.user_id][interaction.item_id] = rating

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile data"""
        if user_id not in self.user_profiles:
            return None

        profile = self.user_profiles[user_id]
        return {
            "user_id": profile.user_id,
            "preferences": profile.preferences,
            "skill_levels": profile.skill_levels,
            "interests": list(profile.interests),
            "total_interactions": len([i for i in self.interactions if i.user_id == user_id]),
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "last_updated": profile.last_updated.isoformat() if profile.last_updated else None
        }

    async def get_recommendation_stats(self) -> Dict[str, Any]:
        """Get recommendation system statistics"""
        return {
            "total_users": len(self.user_profiles),
            "total_content_items": len(self.content_items),
            "total_interactions": len(self.interactions),
            "content_types": {ct.value: len([i for i in self.content_items.values() if i.content_type == ct])
                            for ct in ContentType},
            "recommendation_types": {rt.value: 0 for rt in RecommendationType}  # Would be tracked in real implementation
        }
