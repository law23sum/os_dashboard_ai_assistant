"""
Advanced email processing and intelligence system
Includes smart filtering, auto-responses, sentiment analysis, and workflow automation
"""
import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from apis.google_client import GoogleClient
from apis.openai_client import OpenAIClient
from logger import setup_logger

class EmailPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class EmailCategory(Enum):
    WORK = "work"
    PERSONAL = "personal"
    MARKETING = "marketing"
    NEWSLETTER = "newsletter"
    SUPPORT = "support"
    MEETING = "meeting"
    ACTION_REQUIRED = "action_required"
    FYI = "fyi"

@dataclass
class EmailInsight:
    """Email analysis insights"""
    priority: EmailPriority
    category: EmailCategory
    sentiment: str
    action_required: bool
    estimated_response_time: int  # minutes
    key_topics: List[str]
    suggested_response: Optional[str] = None
    confidence_score: float = 0.0

@dataclass
class EmailRule:
    """Email processing rule"""
    name: str
    condition: str
    action: str
    parameters: Dict[str, Any]
    enabled: bool = True

class AdvancedEmailIntelligence:
    """Advanced email processing with AI-powered insights"""
    
    def __init__(self, gmail_client: GoogleClient, openai_client: OpenAIClient):
        self.gmail = gmail_client
        self.openai = openai_client
        self.logger = setup_logger("EmailIntelligence")
        self.rules = []
        self.templates = {}
        self.learning_data = {}
        
    async def initialize(self):
        """Initialize email intelligence system"""
        await self._load_email_rules()
        await self._load_response_templates()
        await self._load_learning_data()
        self.logger.info("Email intelligence system initialized")
    
    # Email Analysis and Classification
    async def analyze_email(self, email_data: Dict[str, Any]) -> EmailInsight:
        """Comprehensive email analysis using AI"""
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('from', '')
            
            # Prepare analysis prompt
            analysis_prompt = f"""
            Analyze this email and provide insights:
            
            From: {sender}
            Subject: {subject}
            Body: {body[:1000]}...
            
            Please analyze and provide:
            1. Priority level (low/medium/high/urgent)
            2. Category (work/personal/marketing/newsletter/support/meeting/action_required/fyi)
            3. Sentiment (positive/neutral/negative)
            4. Action required (true/false)
            5. Estimated response time in minutes
            6. Key topics (list)
            7. Confidence score (0-1)
            
            Format as JSON with keys: priority, category, sentiment, action_required, response_time, topics, confidence
            """
            
            ai_response = await self.openai.chat_completion(
                analysis_prompt,
                system_prompt="You are an expert email analyst. Provide accurate, actionable insights about emails."
            )
            
            # Parse AI response
            try:
                analysis_data = json.loads(ai_response)
            except json.JSONDecodeError:
                analysis_data = await self._parse_analysis_fallback(ai_response)
            
            # Create insight object
            insight = EmailInsight(
                priority=EmailPriority(analysis_data.get('priority', 'medium')),
                category=EmailCategory(analysis_data.get('category', 'work')),
                sentiment=analysis_data.get('sentiment', 'neutral'),
                action_required=analysis_data.get('action_required', False),
                estimated_response_time=analysis_data.get('response_time', 60),
                key_topics=analysis_data.get('topics', []),
                confidence_score=analysis_data.get('confidence', 0.7)
            )
            
            # Generate suggested response if action required
            if insight.action_required:
                insight.suggested_response = await self._generate_suggested_response(email_data, insight)
            
            return insight
            
        except Exception as e:
            self.logger.error(f"Email analysis failed: {e}")
            # Return default insight
            return EmailInsight(
                priority=EmailPriority.MEDIUM,
                category=EmailCategory.WORK,
                sentiment="neutral",
                action_required=False,
                estimated_response_time=60,
                key_topics=[]
            )
    
    async def _parse_analysis_fallback(self, content: str) -> Dict[str, Any]:
        """Fallback parser for AI analysis"""
        # Simple keyword-based analysis
        content_lower = content.lower()
        
        # Priority detection
        if any(word in content_lower for word in ['urgent', 'asap', 'immediately']):
            priority = 'urgent'
        elif any(word in content_lower for word in ['important', 'priority']):
            priority = 'high'
        elif any(word in content_lower for word in ['fyi', 'info', 'update']):
            priority = 'low'
        else:
            priority = 'medium'
        
        # Category detection
        if any(word in content_lower for word in ['meeting', 'schedule', 'calendar']):
            category = 'meeting'
        elif any(word in content_lower for word in ['action', 'please', 'need', 'request']):
            category = 'action_required'
        elif any(word in content_lower for word in ['newsletter', 'unsubscribe']):
            category = 'newsletter'
        else:
            category = 'work'
        
        return {
            'priority': priority,
            'category': category,
            'sentiment': 'neutral',
            'action_required': 'action' in content_lower or 'please' in content_lower,
            'response_time': 60,
            'topics': [],
            'confidence': 0.6
        }
    
    # Smart Email Processing
    async def process_inbox_intelligently(self, max_emails: int = 50) -> Dict[str, Any]:
        """Process inbox with intelligent filtering and categorization"""
        try:
            # Get unread emails
            emails = await self.gmail.get_emails("is:unread", max_results=max_emails)
            
            processed_emails = []
            categories = {}
            urgent_emails = []
            action_required = []
            
            for email in emails:
                # Analyze email
                insight = await self.analyze_email(email)
                
                # Apply processing rules
                rule_actions = await self._apply_email_rules(email, insight)
                
                processed_email = {
                    "email": email,
                    "insight": insight,
                    "rule_actions": rule_actions,
                    "processed_at": datetime.now().isoformat()
                }
                
                processed_emails.append(processed_email)
                
                # Categorize
                category = insight.category.value
                if category not in categories:
                    categories[category] = []
                categories[category].append(processed_email)
                
                # Flag urgent and action required
                if insight.priority == EmailPriority.URGENT:
                    urgent_emails.append(processed_email)
                
                if insight.action_required:
                    action_required.append(processed_email)
            
            # Generate summary
            summary = await self._generate_inbox_summary(processed_emails, categories)
            
            return {
                "processed_emails": processed_emails,
                "categories": categories,
                "urgent_emails": urgent_emails,
                "action_required": action_required,
                "summary": summary,
                "total_processed": len(processed_emails)
            }
            
        except Exception as e:
            self.logger.error(f"Intelligent inbox processing failed: {e}")
            raise
    
    async def _generate_inbox_summary(self, emails: List[Dict[str, Any]], 
                                    categories: Dict[str, List]) -> str:
        """Generate AI-powered inbox summary"""
        try:
            summary_data = {
                "total_emails": len(emails),
                "categories": {cat: len(emails) for cat, emails in categories.items()},
                "urgent_count": len([e for e in emails if e["insight"].priority == EmailPriority.URGENT]),
                "action_required_count": len([e for e in emails if e["insight"].action_required])
            }
            
            prompt = f"""
            Create a concise inbox summary based on this data:
            {json.dumps(summary_data, indent=2)}
            
            Provide:
            1. Overview of email volume and categories
            2. Priority items that need attention
            3. Recommended actions
            4. Time estimate for processing
            
            Keep it brief and actionable.
            """
            
            summary = await self.openai.chat_completion(
                prompt,
                system_prompt="You are an executive assistant providing inbox summaries."
            )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}")
            return f"Processed {len(emails)} emails across {len(categories)} categories."
    
    # Email Rules and Automation
    async def _load_email_rules(self):
        """Load email processing rules"""
        self.rules = [
            EmailRule(
                name="Auto-archive newsletters",
                condition="category == 'newsletter' and priority == 'low'",
                action="archive",
                parameters={"label": "newsletters"}
            ),
            EmailRule(
                name="Flag urgent emails",
                condition="priority == 'urgent'",
                action="flag",
                parameters={"importance": "high"}
            ),
            EmailRule(
                name="Auto-respond to support requests",
                condition="category == 'support'",
                action="auto_respond",
                parameters={"template": "support_acknowledgment"}
            ),
            EmailRule(
                name="Schedule meeting requests",
                condition="category == 'meeting' and action_required == True",
                action="create_calendar_event",
                parameters={"auto_schedule": True}
            )
        ]
    
    async def _apply_email_rules(self, email: Dict[str, Any], insight: EmailInsight) -> List[Dict[str, Any]]:
        """Apply email processing rules"""
        actions_taken = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                # Evaluate rule condition
                if self._evaluate_rule_condition(rule.condition, email, insight):
                    # Execute rule action
                    action_result = await self._execute_rule_action(rule, email, insight)
                    actions_taken.append({
                        "rule": rule.name,
                        "action": rule.action,
                        "result": action_result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                self.logger.error(f"Rule execution failed for {rule.name}: {e}")
                actions_taken.append({
                    "rule": rule.name,
                    "action": rule.action,
                    "result": {"error": str(e)},
                    "timestamp": datetime.now().isoformat()
                })
        
        return actions_taken
    
    def _evaluate_rule_condition(self, condition: str, email: Dict[str, Any], insight: EmailInsight) -> bool:
        """Evaluate rule condition"""
        try:
            # Create evaluation context
            context = {
                "category": insight.category.value,
                "priority": insight.priority.value,
                "action_required": insight.action_required,
                "sentiment": insight.sentiment,
                "sender": email.get("from", ""),
                "subject": email.get("subject", ""),
                "confidence": insight.confidence_score
            }
            
            # Simple condition evaluation
            return eval(condition, {"__builtins__": {}}, context)
            
        except Exception as e:
            self.logger.error(f"Condition evaluation failed: {e}")
            return False
    
    async def _execute_rule_action(self, rule: EmailRule, email: Dict[str, Any], 
                                 insight: EmailInsight) -> Dict[str, Any]:
        """Execute rule action"""
        action = rule.action
        params = rule.parameters
        
        if action == "archive":
            return await self._archive_email(email, params)
        elif action == "flag":
            return await self._flag_email(email, params)
        elif action == "auto_respond":
            return await self._auto_respond_email(email, params, insight)
        elif action == "create_calendar_event":
            return await self._create_calendar_from_email(email, params, insight)
        else:
            return {"message": f"Unknown action: {action}"}
    
    async def _archive_email(self, email: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Archive email with optional labeling"""
        try:
            # In a real implementation, you would use Gmail API to archive
            return {
                "action": "archived",
                "email_id": email.get("id"),
                "label": params.get("label")
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _flag_email(self, email: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Flag email as important"""
        try:
            # In a real implementation, you would use Gmail API to flag
            return {
                "action": "flagged",
                "email_id": email.get("id"),
                "importance": params.get("importance", "high")
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _auto_respond_email(self, email: Dict[str, Any], params: Dict[str, Any], 
                                insight: EmailInsight) -> Dict[str, Any]:
        """Send automatic response"""
        try:
            template_name = params.get("template", "default")
            
            if template_name in self.templates:
                response_body = self.templates[template_name]
            else:
                # Generate response using AI
                response_body = await self._generate_auto_response(email, insight)
            
            # Send response (placeholder)
            return {
                "action": "auto_responded",
                "email_id": email.get("id"),
                "response_sent": True,
                "template_used": template_name
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _create_calendar_from_email(self, email: Dict[str, Any], params: Dict[str, Any], 
                                        insight: EmailInsight) -> Dict[str, Any]:
        """Create calendar event from email"""
        try:
            # Extract meeting details using AI
            meeting_details = await self._extract_meeting_details(email)
            
            return {
                "action": "calendar_event_created",
                "email_id": email.get("id"),
                "meeting_details": meeting_details
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    # Response Generation
    async def _load_response_templates(self):
        """Load email response templates"""
        self.templates = {
            "support_acknowledgment": """
            Thank you for contacting support. We have received your request and will respond within 24 hours.
            
            Your ticket number is: {ticket_number}
            
            Best regards,
            Support Team
            """,
            "meeting_confirmation": """
            Thank you for the meeting invitation. I have added this to my calendar.
            
            Meeting: {meeting_title}
            Date: {meeting_date}
            Time: {meeting_time}
            
            Looking forward to our discussion.
            
            Best regards
            """,
            "out_of_office": """
            Thank you for your email. I am currently out of the office and will return on {return_date}.
            
            For urgent matters, please contact {backup_contact}.
            
            I will respond to your email upon my return.
            
            Best regards
            """
        }
    
    async def _generate_suggested_response(self, email: Dict[str, Any], insight: EmailInsight) -> str:
        """Generate AI-powered response suggestion"""
        try:
            prompt = f"""
            Generate a professional email response for this email:
            
            From: {email.get('from', '')}
            Subject: {email.get('subject', '')}
            Body: {email.get('body', '')[:500]}...
            
            Context:
            - Category: {insight.category.value}
            - Priority: {insight.priority.value}
            - Sentiment: {insight.sentiment}
            - Key topics: {', '.join(insight.key_topics)}
            
            Generate a professional, helpful response that addresses the main points.
            Keep it concise and appropriate for the context.
            """
            
            response = await self.openai.chat_completion(
                prompt,
                system_prompt="You are a professional email assistant. Generate appropriate, helpful email responses."
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            return "Thank you for your email. I will review and respond shortly."
    
    async def _generate_auto_response(self, email: Dict[str, Any], insight: EmailInsight) -> str:
        """Generate automatic response"""
        return await self._generate_suggested_response(email, insight)
    
    # Meeting and Calendar Integration
    async def _extract_meeting_details(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meeting details from email using AI"""
        try:
            content = f"Subject: {email.get('subject', '')}\nBody: {email.get('body', '')}"
            
            prompt = f"""
            Extract meeting details from this email:
            
            {content}
            
            Extract:
            1. Meeting title/subject
            2. Date and time
            3. Duration
            4. Location (if mentioned)
            5. Attendees (if mentioned)
            6. Agenda items (if any)
            
            Format as JSON with keys: title, date, time, duration, location, attendees, agenda
            """
            
            ai_response = await self.openai.chat_completion(
                prompt,
                system_prompt="You are an expert at extracting meeting information from emails."
            )
            
            try:
                meeting_details = json.loads(ai_response)
            except json.JSONDecodeError:
                meeting_details = {
                    "title": email.get('subject', 'Meeting'),
                    "date": "TBD",
                    "time": "TBD",
                    "duration": "1 hour",
                    "location": "TBD",
                    "attendees": [],
                    "agenda": []
                }
            
            return meeting_details
            
        except Exception as e:
            self.logger.error(f"Meeting detail extraction failed: {e}")
            return {"error": str(e)}
    
    # Learning and Adaptation
    async def _load_learning_data(self):
        """Load learning data for improving accuracy"""
        self.learning_data = {
            "sender_patterns": {},
            "subject_patterns": {},
            "response_effectiveness": {},
            "user_preferences": {}
        }
    
    async def learn_from_user_feedback(self, email_id: str, predicted_insight: EmailInsight, 
                                     actual_insight: EmailInsight, user_action: str):
        """Learn from user feedback to improve predictions"""
        try:
            feedback_data = {
                "email_id": email_id,
                "predicted": {
                    "priority": predicted_insight.priority.value,
                    "category": predicted_insight.category.value,
                    "action_required": predicted_insight.action_required
                },
                "actual": {
                    "priority": actual_insight.priority.value,
                    "category": actual_insight.category.value,
                    "action_required": actual_insight.action_required
                },
                "user_action": user_action,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store feedback for future model improvement
            self.learning_data["feedback"] = self.learning_data.get("feedback", [])
            self.learning_data["feedback"].append(feedback_data)
            
            self.logger.info(f"Learned from user feedback for email {email_id}")
            
        except Exception as e:
            self.logger.error(f"Learning from feedback failed: {e}")
    
    # Analytics and Reporting
    async def generate_email_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Generate email analytics and insights"""
        try:
            # Get emails from the specified period
            start_date = datetime.now() - timedelta(days=days)
            emails = await self.gmail.get_emails(
                f"after:{start_date.strftime('%Y/%m/%d')}", 
                max_results=1000
            )
            
            analytics = {
                "period_days": days,
                "total_emails": len(emails),
                "daily_average": len(emails) / days,
                "categories": {},
                "priorities": {},
                "response_times": [],
                "top_senders": {},
                "busiest_hours": {},
                "sentiment_distribution": {}
            }
            
            # Analyze each email (sample for performance)
            sample_emails = emails[:100] if len(emails) > 100 else emails
            
            for email in sample_emails:
                insight = await self.analyze_email(email)
                
                # Category distribution
                cat = insight.category.value
                analytics["categories"][cat] = analytics["categories"].get(cat, 0) + 1
                
                # Priority distribution
                pri = insight.priority.value
                analytics["priorities"][pri] = analytics["priorities"].get(pri, 0) + 1
                
                # Sentiment distribution
                sent = insight.sentiment
                analytics["sentiment_distribution"][sent] = analytics["sentiment_distribution"].get(sent, 0) + 1
                
                # Top senders
                sender = email.get("from", "Unknown")
                analytics["top_senders"][sender] = analytics["top_senders"].get(sender, 0) + 1
            
            # Generate insights summary
            insights_summary = await self._generate_analytics_summary(analytics)
            analytics["insights_summary"] = insights_summary
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Email analytics generation failed: {e}")
            raise
    
    async def _generate_analytics_summary(self, analytics: Dict[str, Any]) -> str:
        """Generate AI-powered analytics summary"""
        try:
            prompt = f"""
            Analyze these email analytics and provide insights:
            
            {json.dumps(analytics, indent=2)}
            
            Provide:
            1. Key patterns and trends
            2. Productivity insights
            3. Recommendations for improvement
            4. Time management suggestions
            
            Keep it actionable and concise.
            """
            
            summary = await self.openai.chat_completion(
                prompt,
                system_prompt="You are an email productivity analyst providing actionable insights."
            )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Analytics summary generation failed: {e}")
            return "Analytics summary generation failed."
    
    async def shutdown(self):
        """Shutdown email intelligence system"""
        self.logger.info("Email intelligence system shutdown")