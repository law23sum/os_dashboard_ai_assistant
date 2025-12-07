#!/usr/bin/env python3
"""
Advanced Conversation Manager - Integrates sophisticated NLP with existing AI agents.
Combines the advanced conversation AI system with the current OpenAI-based multi-agent architecture.
"""

import asyncio
import json
import re
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from .ai import generate_ai_reply, get_agent_model
from .db import ChatMessage, PERSONAS
from .core.routing import route_user_intent, parse_intent_from_routing, route_intent
from config.logging_config import setup_logger

# Import key components from advanced conversation AI
# These will be integrated selectively to avoid full replacement

class ConversationMode(Enum):
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    SUPPORTIVE = "supportive"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    EDUCATIONAL = "educational"

class IntentType(Enum):
    QUESTION = "question"
    REQUEST = "request"
    COMMAND = "command"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    SMALL_TALK = "small_talk"
    TASK_RELATED = "task_related"
    EMOTIONAL_SUPPORT = "emotional_support"

class EmotionType(Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    EXCITEMENT = "excitement"
    FRUSTRATION = "frustration"
    CONFIDENCE = "confidence"

@dataclass
class ConversationContext:
    """Conversation context tracking"""
    user_id: str
    session_id: str
    conversation_history: List[Dict[str, Any]]
    current_topic: str
    user_mood: EmotionType
    conversation_mode: ConversationMode
    user_preferences: Dict[str, Any]
    active_tasks: List[str]
    mentioned_entities: Dict[str, List[str]]
    conversation_goals: List[str]
    last_interaction: datetime
    context_window: int = 10

@dataclass
class MessageAnalysis:
    """Analysis of user message"""
    message_id: str
    user_id: str
    text: str
    intent: IntentType
    emotion: EmotionType
    sentiment_score: float
    entities: Dict[str, List[str]]
    topics: List[str]
    urgency_level: int  # 1-10
    complexity_level: int  # 1-10
    requires_action: bool
    confidence_score: float
    timestamp: datetime

@dataclass
class ResponseGeneration:
    """Generated response structure"""
    response_id: str
    text: str
    personality_traits: List[str]
    emotion_tone: EmotionType
    confidence_level: float
    suggested_actions: List[str]
    follow_up_questions: List[str]
    context_updates: Dict[str, Any]
    response_type: str
    metadata: Dict[str, Any]

class ConversationManager:
    """
    Hybrid conversation manager that combines advanced NLP analysis
    with existing OpenAI-based multi-agent system.
    """

    def __init__(self):
        self.logger = setup_logger("ConversationManager")
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        self.message_history: Dict[str, List[MessageAnalysis]] = {}

        # Personality profiles aligned with existing agents
        self.personality_profiles = {
            "Aria": {  # Creative, supportive agent
                "traits": ["creative", "supportive", "enthusiastic"],
                "response_style": "narrative",
                "formality_level": 0.6,
                "enthusiasm_level": 0.8,
                "humor_level": 0.4
            },
            "AIC": {  # Analytical, professional agent
                "traits": ["analytical", "professional", "logical"],
                "response_style": "structured",
                "formality_level": 0.8,
                "enthusiasm_level": 0.6,
                "humor_level": 0.2
            },
            "Sora": {  # Strategic, planning agent
                "traits": ["strategic", "organized", "proactive"],
                "response_style": "planning",
                "formality_level": 0.7,
                "enthusiasm_level": 0.7,
                "humor_level": 0.3
            },
            "default": {
                "traits": ["supportive", "professional"],
                "response_style": "balanced",
                "formality_level": 0.7,
                "enthusiasm_level": 0.6,
                "humor_level": 0.3
            }
        }

        # Intent patterns (simplified from advanced system)
        self.intent_patterns = {
            IntentType.QUESTION: [
                r'\b(what|how|why|when|where|who|which)\b',
                r'\?',
                r'\b(explain|tell me|help me understand)\b'
            ],
            IntentType.REQUEST: [
                r'\b(please|can you|could you|would you)\b',
                r'\b(help|assist|support)\b',
                r'\b(need|want|require)\b'
            ],
            IntentType.COMMAND: [
                r'\b(do|create|make|generate|build)\b',
                r'\b(start|stop|pause|resume)\b',
                r'\b(show|display|open)\b'
            ],
            IntentType.TASK_RELATED: [
                r'\b(task|todo|project|deadline)\b',
                r'\b(plan|schedule|organize)\b'
            ]
        }

    async def process_message(self, user_id: str, message: str,
                            session_id: str = None,
                            persona: str = "default") -> Dict[str, Any]:
        """
        Process user message through hybrid analysis and response generation.
        Returns response data compatible with existing GUI system.
        """
        try:
            # Step 1: Analyze message using simplified NLP
            analysis = await self._analyze_message(user_id, message, session_id)

            # Step 2: Update conversation context
            context = await self._update_conversation_context(user_id, session_id, analysis)

            # Step 3: Route to appropriate agent using existing routing system
            routing_result = route_user_intent(message)
            agent_persona = routing_result.get("agent", persona) if routing_result else persona

            # Step 4: Generate response using existing AI system with enhanced context
            response_data = await self._generate_enhanced_response(
                analysis, context, agent_persona, message
            )

            # Step 5: Generate proactive suggestions if appropriate
            suggestions = await self._generate_proactive_suggestions(user_id)

            return {
                "response": response_data,
                "analysis": asdict(analysis),
                "context": asdict(context) if context else None,
                "suggestions": suggestions,
                "agent": agent_persona,
                "intent": analysis.intent.value
            }

        except Exception as e:
            self.logger.error(f"Message processing failed: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your message.",
                "error": str(e)
            }

    async def _analyze_message(self, user_id: str, message: str,
                             session_id: str = None) -> MessageAnalysis:
        """Analyze message using pattern-based approach (simplified from advanced system)"""
        try:
            message_id = str(uuid.uuid4())

            if not session_id:
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Determine intent
            intent = self._analyze_intent(message)

            # Estimate emotion (simplified)
            emotion = self._analyze_emotion_basic(message)

            # Calculate sentiment (basic approach)
            sentiment_score = self._calculate_sentiment_basic(message)

            # Extract entities (basic patterns)
            entities = self._extract_entities_basic(message)

            # Extract topics (keyword-based)
            topics = self._extract_topics_basic(message)

            # Calculate levels
            urgency_level = self._calculate_urgency(message, intent, emotion)
            complexity_level = self._calculate_complexity(message, entities, topics)
            requires_action = self._requires_action(intent, message)
            confidence_score = 0.7  # Base confidence for pattern-based analysis

            analysis = MessageAnalysis(
                message_id=message_id,
                user_id=user_id,
                text=message,
                intent=intent,
                emotion=emotion,
                sentiment_score=sentiment_score,
                entities=entities,
                topics=topics,
                urgency_level=urgency_level,
                complexity_level=complexity_level,
                requires_action=requires_action,
                confidence_score=confidence_score,
                timestamp=datetime.now()
            )

            # Store analysis
            if user_id not in self.message_history:
                self.message_history[user_id] = []
            self.message_history[user_id].append(analysis)

            return analysis

        except Exception as e:
            self.logger.error(f"Message analysis failed: {e}")
            return MessageAnalysis(
                message_id=str(uuid.uuid4()),
                user_id=user_id,
                text=message,
                intent=IntentType.QUESTION,
                emotion=EmotionType.NEUTRAL,
                sentiment_score=0.0,
                entities={},
                topics=[],
                urgency_level=5,
                complexity_level=5,
                requires_action=False,
                confidence_score=0.5,
                timestamp=datetime.now()
            )

    def _analyze_intent(self, message: str) -> IntentType:
        """Analyze message intent using pattern matching"""
        message_lower = message.lower()

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent

        return IntentType.QUESTION

    def _analyze_emotion_basic(self, message: str) -> EmotionType:
        """Basic emotion analysis using keyword detection"""
        message_lower = message.lower()

        # Positive emotions
        if any(word in message_lower for word in ['great', 'awesome', 'excellent', 'love', 'excited']):
            return EmotionType.JOY
        elif any(word in message_lower for word in ['happy', 'good', 'nice', 'pleased']):
            return EmotionType.JOY

        # Negative emotions
        elif any(word in message_lower for word in ['frustrated', 'annoyed', 'angry', 'upset']):
            return EmotionType.ANGER
        elif any(word in message_lower for word in ['sad', 'disappointed', 'sorry']):
            return EmotionType.SADNESS
        elif any(word in message_lower for word in ['worried', 'concerned', 'afraid']):
            return EmotionType.FEAR

        # Neutral by default
        return EmotionType.NEUTRAL

    def _calculate_sentiment_basic(self, message: str) -> float:
        """Basic sentiment calculation"""
        positive_words = ['good', 'great', 'excellent', 'awesome', 'love', 'like', 'happy', 'excited']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'angry', 'frustrated', 'worried']

        words = message.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0

        return (positive_count - negative_count) / total_sentiment_words

    def _extract_entities_basic(self, message: str) -> Dict[str, List[str]]:
        """Basic entity extraction using regex patterns"""
        entities = {}

        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            entities['EMAIL'] = emails

        # Date patterns
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, message))
        if dates:
            entities['DATE'] = dates

        return entities

    def _extract_topics_basic(self, message: str) -> List[str]:
        """Basic topic extraction using keywords"""
        topics = []
        message_lower = message.lower()

        topic_keywords = {
            'work': ['work', 'task', 'project', 'meeting', 'deadline'],
            'code': ['code', 'programming', 'software', 'development'],
            'document': ['document', 'file', 'word', 'excel', 'onenote'],
            'planning': ['plan', 'schedule', 'organize', 'priority']
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _calculate_urgency(self, message: str, intent: IntentType, emotion: EmotionType) -> int:
        """Calculate message urgency"""
        urgency = 5

        if intent == IntentType.COMMAND:
            urgency += 2
        elif intent == IntentType.REQUEST:
            urgency += 1

        if emotion == EmotionType.ANGER:
            urgency += 2
        elif emotion == EmotionType.FEAR:
            urgency += 1

        urgent_words = ['urgent', 'asap', 'immediately', 'emergency', 'critical']
        if any(word in message.lower() for word in urgent_words):
            urgency += 2

        return max(1, min(10, urgency))

    def _calculate_complexity(self, message: str, entities: Dict[str, List[str]], topics: List[str]) -> int:
        """Calculate message complexity"""
        complexity = 5

        word_count = len(message.split())
        if word_count > 50:
            complexity += 2
        elif word_count > 20:
            complexity += 1

        entity_count = sum(len(ents) for ents in entities.values())
        complexity += min(2, entity_count)

        complexity += min(2, len(topics))

        return max(1, min(10, complexity))

    def _requires_action(self, intent: IntentType, message: str) -> bool:
        """Determine if message requires action"""
        action_intents = [IntentType.COMMAND, IntentType.REQUEST, IntentType.TASK_RELATED]
        if intent in action_intents:
            return True

        action_words = ['create', 'make', 'build', 'generate', 'help', 'fix', 'solve']
        return any(word in message.lower() for word in action_words)

    async def _update_conversation_context(self, user_id: str, session_id: str,
                                         analysis: MessageAnalysis) -> ConversationContext:
        """Update conversation context"""
        context_key = f"{user_id}_{session_id}"

        if context_key not in self.conversation_contexts:
            self.conversation_contexts[context_key] = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                conversation_history=[],
                current_topic="general",
                user_mood=EmotionType.NEUTRAL,
                conversation_mode=ConversationMode.CASUAL,
                user_preferences={},
                active_tasks=[],
                mentioned_entities={},
                conversation_goals=[],
                last_interaction=datetime.now()
            )

        context = self.conversation_contexts[context_key]

        # Update conversation history
        context.conversation_history.append({
            "message_id": analysis.message_id,
            "text": analysis.text,
            "intent": analysis.intent.value,
            "emotion": analysis.emotion.value,
            "timestamp": analysis.timestamp.isoformat()
        })

        # Keep recent history
        if len(context.conversation_history) > context.context_window:
            context.conversation_history = context.conversation_history[-context.context_window:]

        # Update current topic
        if analysis.topics:
            context.current_topic = analysis.topics[0]

        # Update user mood
        context.user_mood = analysis.emotion

        # Update mentioned entities
        for entity_type, entities in analysis.entities.items():
            if entity_type not in context.mentioned_entities:
                context.mentioned_entities[entity_type] = []
            context.mentioned_entities[entity_type].extend(entities)
            context.mentioned_entities[entity_type] = list(set(
                context.mentioned_entities[entity_type][-10:]
            ))

        context.last_interaction = datetime.now()

        return context

    async def _generate_enhanced_response(self, analysis: MessageAnalysis,
                                        context: ConversationContext,
                                        persona: str, original_message: str) -> str:
        """Generate response using existing AI system with enhanced context"""

        # Prepare enhanced prompt with context information
        enhanced_prompt = self._build_enhanced_prompt(analysis, context, original_message)

        # Use existing AI system to generate response
        # This would integrate with your existing generate_ai_reply function
        try:
            # For now, return a placeholder - would integrate with existing AI system
            response = f"[Enhanced Context] {enhanced_prompt}"

            # Apply personality adjustments
            profile = self.personality_profiles.get(persona, self.personality_profiles["default"])
            response = self._apply_personality_adjustments(response, profile, analysis.emotion)

            return response

        except Exception as e:
            self.logger.error(f"Enhanced response generation failed: {e}")
            return "I understand your message and am processing it."

    def _build_enhanced_prompt(self, analysis: MessageAnalysis,
                              context: ConversationContext, original_message: str) -> str:
        """Build enhanced prompt with context and analysis"""
        prompt_parts = [original_message]

        # Add intent context
        prompt_parts.append(f"[Intent: {analysis.intent.value}]")

        # Add emotion context
        prompt_parts.append(f"[Emotion: {analysis.emotion.value}]")

        # Add urgency/complexity context
        prompt_parts.append(f"[Urgency: {analysis.urgency_level}/10, Complexity: {analysis.complexity_level}/10]")

        # Add topics
        if analysis.topics:
            prompt_parts.append(f"[Topics: {', '.join(analysis.topics)}]")

        # Add conversation context
        if context and context.conversation_history:
            recent_history = context.conversation_history[-3:]  # Last 3 messages
            history_text = "Recent conversation: " + "; ".join([
                f"{msg['intent']} ({msg['emotion']}): {msg['text'][:50]}..."
                for msg in recent_history
            ])
            prompt_parts.append(f"[Context: {history_text}]")

        return " ".join(prompt_parts)

    def _apply_personality_adjustments(self, response: str, profile: Dict[str, Any],
                                     user_emotion: EmotionType) -> str:
        """Apply personality adjustments to response"""
        adjusted_response = response

        # Apply enthusiasm level
        enthusiasm = profile.get("enthusiasm_level", 0.5)
        if enthusiasm > 0.7 and user_emotion in [EmotionType.JOY, EmotionType.NEUTRAL]:
            if not adjusted_response.endswith("!") and not adjusted_response.endswith("?"):
                adjusted_response += "!"

        # Apply formality level
        formality = profile.get("formality_level", 0.5)
        if formality < 0.4:
            # Make more casual
            adjusted_response = adjusted_response.replace("I would", "I'd")
            adjusted_response = adjusted_response.replace("I will", "I'll")

        return adjusted_response

    async def _generate_proactive_suggestions(self, user_id: str) -> List[str]:
        """Generate proactive suggestions based on user patterns"""
        try:
            user_messages = self.message_history.get(user_id, [])
            if len(user_messages) < 3:
                return []

            suggestions = []

            # Analyze recent patterns
            recent_messages = user_messages[-5:]
            intents = [msg.intent for msg in recent_messages]

            # Task-related pattern
            if intents.count(IntentType.TASK_RELATED) >= 2:
                suggestions.append("I notice you've been working on several tasks. Would you like help organizing them?")

            # Question pattern
            if intents.count(IntentType.QUESTION) >= 3:
                suggestions.append("You've been asking several questions. Would you like me to provide a comprehensive overview of the topic?")

            # Time-based suggestions
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 11:
                suggestions.append("Good morning! Would you like to review your priorities for today?")

            return suggestions[:2]  # Return up to 2 suggestions

        except Exception as e:
            self.logger.error(f"Proactive suggestion generation failed: {e}")
            return []

    async def get_conversation_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get conversation analytics for user"""
        try:
            user_messages = self.message_history.get(user_id, [])
            if not user_messages:
                return {"error": "No conversation data available"}

            # Basic analytics
            total_messages = len(user_messages)
            avg_sentiment = sum(msg.sentiment_score for msg in user_messages) / total_messages
            dominant_intent = max(set(msg.intent.value for msg in user_messages),
                                key=lambda x: sum(1 for msg in user_messages if msg.intent.value == x))

            return {
                "total_messages": total_messages,
                "average_sentiment": round(avg_sentiment, 3),
                "dominant_intent": dominant_intent,
                "topics_discussed": list(set(topic for msg in user_messages for topic in msg.topics))
            }

        except Exception as e:
            self.logger.error(f"Analytics generation failed: {e}")
            return {"error": str(e)}

    async def cleanup_old_contexts(self):
        """Clean up old conversation contexts"""
        current_time = datetime.now()
        expired_keys = []

        for context_key, context in self.conversation_contexts.items():
            if (current_time - context.last_interaction).total_seconds() > 86400:  # 24 hours
                expired_keys.append(context_key)

        for key in expired_keys:
            del self.conversation_contexts[key]

        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} old conversation contexts")

# Global conversation manager instance
conversation_manager = ConversationManager()

async def process_conversation_message(user_id: str, message: str,
                                     session_id: str = None,
                                     persona: str = "default") -> Dict[str, Any]:
    """Convenience function to process conversation messages"""
    return await conversation_manager.process_message(user_id, message, session_id, persona)

async def get_conversation_analytics(user_id: str) -> Dict[str, Any]:
    """Convenience function to get conversation analytics"""
    return await conversation_manager.get_conversation_analytics(user_id)
