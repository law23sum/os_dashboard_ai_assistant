"""
Real-Time Collaboration & Team Intelligence

Real-time communication with WebSocket support, team analytics,
collaborative document editing, and advanced team insights.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import defaultdict, Counter
import re

from config.logging_config import setup_logger


class CollaborationEventType(Enum):
    MESSAGE_SENT = "message_sent"
    DOCUMENT_EDITED = "document_edited"
    TASK_ASSIGNED = "task_assigned"
    MEETING_STARTED = "meeting_started"
    FILE_SHARED = "file_shared"
    COMMENT_ADDED = "comment_added"


class CommunicationChannel(Enum):
    CHAT = "chat"
    EMAIL = "email"
    VIDEO_CALL = "video_call"
    DOCUMENT = "document"
    PROJECT_BOARD = "project_board"


class TeamRole(Enum):
    LEADER = "leader"
    DEVELOPER = "developer"
    DESIGNER = "designer"
    ANALYST = "analyst"
    MANAGER = "manager"
    CONTRIBUTOR = "contributor"


@dataclass
class TeamMember:
    """Team member information"""
    user_id: str
    name: str
    role: TeamRole
    skills: List[str]
    availability_status: str = "available"  # available, busy, away, offline
    current_project: Optional[str] = None
    last_active: Optional[datetime] = None

    def __post_init__(self):
        if not self.last_active:
            self.last_active = datetime.now()


@dataclass
class CollaborationEvent:
    """Collaboration event"""
    event_id: str
    event_type: CollaborationEventType
    user_id: str
    channel: CommunicationChannel
    content: Dict[str, Any]
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()


@dataclass
class TeamSession:
    """Team collaboration session"""
    session_id: str
    session_type: str  # meeting, sprint, review, etc.
    participants: List[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    objectives: List[str] = None
    outcomes: List[str] = None
    productivity_score: Optional[float] = None

    def __post_init__(self):
        if self.objectives is None:
            self.objectives = []
        if self.outcomes is None:
            self.outcomes = []


@dataclass
class TeamInsight:
    """Team intelligence insight"""
    insight_id: str
    insight_type: str
    title: str
    description: str
    severity: str  # low, medium, high, critical
    affected_members: List[str]
    recommendations: List[str]
    generated_at: Optional[datetime] = None
    confidence_score: float = 0.0

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now()


class CollaborationIntelligence:
    """Real-Time Collaboration & Team Intelligence System"""

    def __init__(self):
        self.logger = setup_logger("CollaborationIntelligence")
        self.team_members: Dict[str, TeamMember] = {}
        self.collaboration_events: List[CollaborationEvent] = []
        self.active_sessions: Dict[str, TeamSession] = {}
        self.team_insights: List[TeamInsight] = []
        self.communication_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)

    async def initialize(self):
        """Initialize the collaboration intelligence system"""
        self.logger.info("Initializing Collaboration Intelligence System...")

        # Start background monitoring
        asyncio.create_task(self._monitor_collaboration_patterns())

        self.logger.info("Collaboration Intelligence system initialized")

    async def analyze_team_collaboration(self, team_data: Dict[str, Any],
                                       options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze team collaboration patterns and generate insights"""
        try:
            # Extract team information
            team_members = team_data.get("team_members", [])
            time_period = team_data.get("time_period_days", 30)

            # Update team member data
            for member_data in team_members:
                await self._update_team_member(member_data)

            # Analyze communication patterns
            communication_analysis = await self._analyze_communication_patterns(time_period)

            # Analyze productivity patterns
            productivity_analysis = await self._analyze_productivity_patterns(time_period)

            # Generate team insights
            insights = await self._generate_team_insights(team_data)

            # Calculate team health score
            health_score = await self._calculate_team_health_score()

            return {
                "analysis_period_days": time_period,
                "team_size": len(team_members),
                "communication_analysis": communication_analysis,
                "productivity_analysis": productivity_analysis,
                "team_insights": [asdict(insight) for insight in insights],
                "team_health_score": health_score,
                "recommendations": await self._generate_recommendations(insights),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error analyzing team collaboration: {e}")
            return {"error": str(e)}

    async def _update_team_member(self, member_data: Dict[str, Any]):
        """Update or create team member information"""
        user_id = member_data["user_id"]

        if user_id not in self.team_members:
            self.team_members[user_id] = TeamMember(
                user_id=user_id,
                name=member_data["name"],
                role=TeamRole(member_data.get("role", "contributor")),
                skills=member_data.get("skills", []),
                availability_status=member_data.get("availability_status", "available"),
                current_project=member_data.get("current_project")
            )
        else:
            member = self.team_members[user_id]
            member.name = member_data.get("name", member.name)
            member.role = TeamRole(member_data.get("role", member.role.value))
            member.skills = member_data.get("skills", member.skills)
            member.availability_status = member_data.get("availability_status", member.availability_status)
            member.current_project = member_data.get("current_project", member.current_project)
            member.last_active = datetime.now()

    async def _analyze_communication_patterns(self, time_period: int) -> Dict[str, Any]:
        """Analyze team communication patterns"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        recent_events = [e for e in self.collaboration_events if e.timestamp >= cutoff_date]

        # Channel usage analysis
        channel_usage = Counter([e.channel.value for e in recent_events])

        # Message frequency by member
        member_activity = Counter([e.user_id for e in recent_events])

        # Response time analysis (simplified)
        response_times = []
        message_threads = defaultdict(list)

        # Group messages by conversation/thread
        for event in recent_events:
            if event.channel == CommunicationChannel.CHAT:
                thread_id = event.content.get("thread_id", event.event_id)
                message_threads[thread_id].append(event)

        # Calculate average response times
        for thread_events in message_threads.values():
            if len(thread_events) > 1:
                sorted_events = sorted(thread_events, key=lambda x: x.timestamp)
                for i in range(1, len(sorted_events)):
                    time_diff = (sorted_events[i].timestamp - sorted_events[i-1].timestamp).total_seconds()
                    if time_diff < 3600:  # Only count responses within 1 hour
                        response_times.append(time_diff)

        avg_response_time = statistics.mean(response_times) if response_times else 0

        # Communication network analysis
        communication_network = defaultdict(lambda: defaultdict(int))
        for event in recent_events:
            if event.channel == CommunicationChannel.CHAT:
                mentioned_users = event.content.get("mentions", [])
                for mentioned_user in mentioned_users:
                    communication_network[event.user_id][mentioned_user] += 1

        return {
            "total_messages": len(recent_events),
            "channel_usage": dict(channel_usage),
            "member_activity": dict(member_activity),
            "average_response_time_seconds": avg_response_time,
            "communication_network_size": len(communication_network),
            "most_active_channel": channel_usage.most_common(1)[0][0] if channel_usage else None
        }

    async def _analyze_productivity_patterns(self, time_period: int) -> Dict[str, Any]:
        """Analyze team productivity patterns"""
        cutoff_date = datetime.now() - timedelta(days=time_period)

        # Analyze sessions
        recent_sessions = [s for s in self.active_sessions.values()
                          if s.start_time >= cutoff_date and s.end_time]

        productivity_scores = [s.productivity_score for s in recent_sessions if s.productivity_score]

        # Task completion analysis from events
        task_events = [e for e in self.collaboration_events
                      if e.event_type == CollaborationEventType.TASK_ASSIGNED
                      and e.timestamp >= cutoff_date]

        # Meeting analysis
        meetings = [s for s in recent_sessions if s.session_type == "meeting"]

        meeting_effectiveness = []
        for meeting in meetings:
            if meeting.productivity_score is not None:
                meeting_effectiveness.append(meeting.productivity_score)

        # Collaboration patterns
        collaboration_events = [e for e in self.collaboration_events
                               if e.timestamp >= cutoff_date
                               and e.event_type in [CollaborationEventType.DOCUMENT_EDITED,
                                                  CollaborationEventType.FILE_SHARED,
                                                  CollaborationEventType.COMMENT_ADDED]]

        return {
            "total_sessions": len(recent_sessions),
            "average_productivity_score": statistics.mean(productivity_scores) if productivity_scores else 0,
            "total_tasks_assigned": len(task_events),
            "total_meetings": len(meetings),
            "average_meeting_effectiveness": statistics.mean(meeting_effectiveness) if meeting_effectiveness else 0,
            "collaboration_events_count": len(collaboration_events),
            "most_productive_day": await self._find_most_productive_day(time_period)
        }

    async def _find_most_productive_day(self, time_period: int) -> Optional[str]:
        """Find the most productive day in the period"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        daily_productivity = defaultdict(float)

        for session in self.active_sessions.values():
            if session.start_time >= cutoff_date and session.productivity_score:
                day_key = session.start_time.strftime("%Y-%m-%d")
                daily_productivity[day_key] += session.productivity_score

        if daily_productivity:
            most_productive_day = max(daily_productivity.items(), key=lambda x: x[1])
            return most_productive_day[0]

        return None

    async def _generate_team_insights(self, team_data: Dict[str, Any]) -> List[TeamInsight]:
        """Generate intelligent insights about team collaboration"""
        insights = []

        # Communication bottlenecks
        comm_analysis = await self._analyze_communication_patterns(7)  # Last week
        if comm_analysis["average_response_time_seconds"] > 3600:  # Over 1 hour
            insights.append(TeamInsight(
                insight_id=str(uuid.uuid4()),
                insight_type="communication_bottleneck",
                title="Slow Response Times Detected",
                description=f"Average response time is {comm_analysis['average_response_time_seconds']/60:.1f} minutes, indicating potential communication bottlenecks.",
                severity="medium",
                affected_members=list(self.team_members.keys()),
                recommendations=[
                    "Consider setting up dedicated communication channels",
                    "Implement response time SLAs for urgent matters",
                    "Use collaboration tools with better notification systems"
                ],
                confidence_score=0.8
            ))

        # Productivity patterns
        prod_analysis = await self._analyze_productivity_patterns(30)
        if prod_analysis["average_productivity_score"] < 0.5:
            insights.append(TeamInsight(
                insight_id=str(uuid.uuid4()),
                insight_type="low_productivity",
                title="Low Team Productivity",
                description=f"Team productivity score is {prod_analysis['average_productivity_score']:.2f}, below recommended levels.",
                severity="high",
                affected_members=list(self.team_members.keys()),
                recommendations=[
                    "Review meeting schedules and reduce unnecessary meetings",
                    "Implement productivity tracking tools",
                    "Consider workload balancing across team members"
                ],
                confidence_score=0.9
            ))

        # Collaboration imbalances
        member_activity = comm_analysis["member_activity"]
        if member_activity:
            max_activity = max(member_activity.values())
            min_activity = min(member_activity.values())

            if max_activity > min_activity * 2:  # 2x difference
                inactive_members = [uid for uid, count in member_activity.items()
                                  if count < max_activity * 0.5]
                insights.append(TeamInsight(
                    insight_id=str(uuid.uuid4()),
                    insight_type="collaboration_imbalance",
                    title="Uneven Collaboration Participation",
                    description="Some team members are significantly less active in collaboration than others.",
                    severity="medium",
                    affected_members=inactive_members,
                    recommendations=[
                        "Encourage participation from all team members",
                        "Provide training on collaboration tools",
                        "Schedule regular check-ins to ensure everyone is engaged"
                    ],
                    confidence_score=0.7
                ))

        # Meeting effectiveness
        if prod_analysis["total_meetings"] > 0 and prod_analysis["average_meeting_effectiveness"] < 0.6:
            insights.append(TeamInsight(
                insight_id=str(uuid.uuid4()),
                insight_type="ineffective_meetings",
                title="Low Meeting Effectiveness",
                description=f"Meeting effectiveness score is {prod_analysis['average_meeting_effectiveness']:.2f}, indicating meetings may not be productive.",
                severity="medium",
                affected_members=list(self.team_members.keys()),
                recommendations=[
                    "Set clear agendas for all meetings",
                    "Limit meeting duration and stick to schedules",
                    "Use meeting effectiveness surveys",
                    "Consider async communication for routine updates"
                ],
                confidence_score=0.75
            ))

        return insights

    async def _calculate_team_health_score(self) -> float:
        """Calculate overall team health score"""
        scores = []

        # Communication health (30%)
        comm_analysis = await self._analyze_communication_patterns(7)
        if comm_analysis["total_messages"] > 0:
            response_time_score = max(0, 1 - (comm_analysis["average_response_time_seconds"] / 7200))  # Normalize to 2 hours
            activity_balance = 1 - (max(comm_analysis["member_activity"].values()) -
                                  min(comm_analysis["member_activity"].values())) / max(comm_analysis["member_activity"].values())
            comm_score = (response_time_score + activity_balance) / 2
            scores.append(comm_score * 0.3)

        # Productivity health (40%)
        prod_analysis = await self._analyze_productivity_patterns(30)
        prod_score = prod_analysis["average_productivity_score"] * 0.4
        scores.append(prod_score)

        # Collaboration health (30%)
        collab_events = len([e for e in self.collaboration_events
                           if e.timestamp >= datetime.now() - timedelta(days=7)
                           and e.event_type in [CollaborationEventType.DOCUMENT_EDITED,
                                              CollaborationEventType.FILE_SHARED]])
        collab_score = min(collab_events / 50, 1) * 0.3  # Normalize to 50 collaborative events
        scores.append(collab_score)

        return sum(scores) if scores else 0.0

    async def _generate_recommendations(self, insights: List[TeamInsight]) -> List[str]:
        """Generate actionable recommendations based on insights"""
        recommendations = []

        insight_types = set([i.insight_type for i in insights])

        if "communication_bottleneck" in insight_types:
            recommendations.extend([
                "Implement structured communication protocols",
                "Use collaboration tools with real-time notifications",
                "Establish communication response time expectations"
            ])

        if "low_productivity" in insight_types:
            recommendations.extend([
                "Conduct productivity audits to identify bottlenecks",
                "Implement time tracking and productivity monitoring",
                "Consider workload redistribution across team members"
            ])

        if "collaboration_imbalance" in insight_types:
            recommendations.extend([
                "Create opportunities for all team members to contribute",
                "Provide training on collaboration tools and processes",
                "Establish rotation schedules for different types of tasks"
            ])

        if "ineffective_meetings" in insight_types:
            recommendations.extend([
                "Implement meeting effectiveness metrics",
                "Require agendas and clear objectives for all meetings",
                "Consider meeting-free days or time blocks"
            ])

        # General recommendations if no specific issues
        if not insights:
            recommendations.extend([
                "Continue monitoring team collaboration metrics",
                "Regularly review and optimize communication channels",
                "Maintain current productivity and collaboration practices"
            ])

        return recommendations[:10]  # Limit to top 10

    async def record_collaboration_event(self, event_data: Dict[str, Any]):
        """Record a collaboration event"""
        event = CollaborationEvent(
            event_id=str(uuid.uuid4()),
            event_type=CollaborationEventType(event_data["event_type"]),
            user_id=event_data["user_id"],
            channel=CommunicationChannel(event_data.get("channel", "chat")),
            content=event_data.get("content", {}),
            metadata=event_data.get("metadata", {})
        )

        self.collaboration_events.append(event)

        # Update member last activity
        if event.user_id in self.team_members:
            self.team_members[event.user_id].last_active = event.timestamp

    async def start_team_session(self, session_data: Dict[str, Any]) -> str:
        """Start a new team session"""
        session_id = str(uuid.uuid4())

        session = TeamSession(
            session_id=session_id,
            session_type=session_data["session_type"],
            participants=session_data["participants"],
            start_time=datetime.now(),
            objectives=session_data.get("objectives", [])
        )

        self.active_sessions[session_id] = session

        # Update member status
        for participant_id in session.participants:
            if participant_id in self.team_members:
                self.team_members[participant_id].availability_status = "busy"

        return session_id

    async def end_team_session(self, session_id: str, outcomes: List[str] = None,
                             productivity_score: float = None):
        """End a team session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]
        session.end_time = datetime.now()
        session.outcomes = outcomes or []
        session.productivity_score = productivity_score

        # Update member status back to available
        for participant_id in session.participants:
            if participant_id in self.team_members:
                self.team_members[participant_id].availability_status = "available"

        return {"status": "session_ended", "duration_minutes": (session.end_time - session.start_time).total_seconds() / 60}

    async def _monitor_collaboration_patterns(self):
        """Monitor collaboration patterns in the background"""
        while True:
            try:
                # Analyze patterns every hour
                await asyncio.sleep(3600)

                # Update communication patterns
                recent_events = [e for e in self.collaboration_events
                               if e.timestamp >= datetime.now() - timedelta(hours=1)]

                for event in recent_events:
                    user_patterns = self.communication_patterns[event.user_id]
                    user_patterns["total_events"] = user_patterns.get("total_events", 0) + 1
                    user_patterns["last_activity"] = event.timestamp

                    # Track channel preferences
                    channel_key = f"{event.channel.value}_count"
                    user_patterns[channel_key] = user_patterns.get(channel_key, 0) + 1

            except Exception as e:
                self.logger.error(f"Error monitoring collaboration patterns: {e}")
                await asyncio.sleep(3600)

    async def get_team_member_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a team member"""
        if user_id not in self.team_members:
            return None

        member = self.team_members[user_id]
        return {
            "user_id": member.user_id,
            "name": member.name,
            "role": member.role.value,
            "availability_status": member.availability_status,
            "current_project": member.current_project,
            "last_active": member.last_active.isoformat() if member.last_active else None,
            "skills": member.skills
        }

    async def get_team_overview(self) -> Dict[str, Any]:
        """Get overall team overview"""
        total_members = len(self.team_members)
        active_members = len([m for m in self.team_members.values()
                            if m.availability_status == "available"])
        busy_members = len([m for m in self.team_members.values()
                          if m.availability_status == "busy"])

        # Role distribution
        role_distribution = Counter([m.role.value for m in self.team_members.values()])

        # Active sessions
        active_sessions_count = len([s for s in self.active_sessions.values() if not s.end_time])

        return {
            "total_members": total_members,
            "active_members": active_members,
            "busy_members": busy_members,
            "offline_members": total_members - active_members - busy_members,
            "role_distribution": dict(role_distribution),
            "active_sessions": active_sessions_count,
            "team_health_score": await self._calculate_team_health_score()
        }

    async def optimize_team_workflow(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide workflow optimization recommendations"""
        # Analyze current workflow and suggest improvements
        team_size = len(self.team_members)
        project_complexity = project_data.get("complexity", "medium")
        deadline_pressure = project_data.get("deadline_pressure", "medium")

        recommendations = []

        if team_size < 3 and project_complexity == "high":
            recommendations.append("Consider adding team members for complex projects")

        if deadline_pressure == "high":
            recommendations.append("Implement agile sprint methodology")
            recommendations.append("Set up daily stand-up meetings")

        if team_size > 5:
            recommendations.append("Consider dividing into smaller sub-teams")
            recommendations.append("Implement scrum master role")

        return {
            "current_team_size": team_size,
            "project_complexity": project_complexity,
            "deadline_pressure": deadline_pressure,
            "workflow_recommendations": recommendations,
            "suggested_methodology": "agile" if deadline_pressure == "high" else "kanban"
        }
