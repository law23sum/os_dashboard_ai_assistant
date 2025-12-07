"""AI-powered project insights and risk analysis."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

from .db import AssistantState, Task, Project
from .ai import generate_ai_reply, openai_available, get_agent_model

def analyze_project_risks(state: AssistantState, project_name: str) -> Dict:
    """Analyze risks for a specific project using AI."""
    project = next((p for p in state.projects if p.name == project_name), None)
    if not project:
        return {"error": "Project not found"}
    
    project_tasks = [t for t in state.tasks if t.project == project_name]
    if not project_tasks:
        return {
            "project": project_name,
            "risks": [],
            "risk_level": "low",
            "recommendations": ["No tasks found for this project"]
        }
    
    # Calculate metrics
    total = len(project_tasks)
    done = len([t for t in project_tasks if t.status == "DONE"])
    blocked = len([t for t in project_tasks if t.status == "BLOCKED"])
    overdue = 0
    high_priority_pending = 0
    
    today = datetime.now().date()
    for task in project_tasks:
        if task.due_date and task.status != "DONE":
            try:
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                if due_date < today:
                    overdue += 1
            except Exception:
                pass
        if task.status != "DONE" and task.priority in ["HIGH", "CRITICAL"]:
            high_priority_pending += 1
    
    # Identify risks
    risks = []
    risk_score = 0
    
    if blocked > 0:
        risk_score += 30
        risks.append({
            "type": "blocked_tasks",
            "severity": "high" if blocked > total * 0.2 else "medium",
            "description": f"{blocked} tasks are blocked, potentially blocking {total - done} other tasks",
            "impact": "Project progress may be stalled"
        })
    
    if overdue > 0:
        risk_score += 25
        risks.append({
            "type": "overdue_tasks",
            "severity": "high" if overdue > total * 0.15 else "medium",
            "description": f"{overdue} tasks are overdue",
            "impact": "Project timeline may be at risk"
        })
    
    if high_priority_pending > 0:
        risk_score += 20
        risks.append({
            "type": "high_priority_pending",
            "severity": "medium",
            "description": f"{high_priority_pending} high/critical priority tasks pending",
            "impact": "Critical work may be delayed"
        })
    
    completion_rate = (done / total * 100) if total > 0 else 0
    if completion_rate < 30 and total > 5:
        risk_score += 15
        risks.append({
            "type": "low_progress",
            "severity": "medium",
            "description": f"Only {completion_rate:.1f}% completion with {total} tasks",
            "impact": "Project may be behind schedule"
        })
    
    # Use AI for additional insights if available
    recommendations = []
    if openai_available():
        try:
            context = f"""
Project: {project_name}
Status: {project.status}
Priority: {project.priority}
Total Tasks: {total}
Completed: {done}
Blocked: {blocked}
Overdue: {overdue}
High Priority Pending: {high_priority_pending}
Completion Rate: {completion_rate:.1f}%

Recent tasks:
{chr(10).join([f"- {t.title} ({t.status}, {t.priority})" for t in project_tasks[:10]])}
"""
            prompt = f"""Analyze this project and provide 3-5 specific, actionable recommendations to improve project health and reduce risks. Focus on:
1. Immediate actions to unblock progress
2. Resource allocation suggestions
3. Timeline adjustments if needed
4. Risk mitigation strategies

{context}

Provide recommendations as a numbered list, be concise and actionable."""
            
            ai_response = generate_ai_reply(
                prompt,
                system_prompt="You are a project management expert providing actionable insights.",
                model=get_agent_model("Sora")
            )
            
            # Parse recommendations from AI response
            lines = ai_response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    rec = line.lstrip('0123456789.-• ').strip()
                    if rec:
                        recommendations.append(rec)
        except Exception:
            pass
    
    # Fallback recommendations if AI unavailable
    if not recommendations:
        if blocked > 0:
            recommendations.append(f"Review and resolve {blocked} blocked tasks")
        if overdue > 0:
            recommendations.append(f"Address {overdue} overdue tasks immediately")
        if high_priority_pending > 0:
            recommendations.append(f"Prioritize {high_priority_pending} high-priority tasks")
        if completion_rate < 50:
            recommendations.append("Consider breaking down large tasks or adjusting timeline")
    
    risk_level = "high" if risk_score >= 50 else "medium" if risk_score >= 25 else "low"
    
    return {
        "project": project_name,
        "risks": risks,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "metrics": {
            "total_tasks": total,
            "completed": done,
            "blocked": blocked,
            "overdue": overdue,
            "high_priority_pending": high_priority_pending,
            "completion_rate": round(completion_rate, 1)
        },
        "recommendations": recommendations[:5]  # Top 5 recommendations
    }


def predict_project_completion(state: AssistantState, project_name: str) -> Dict:
    """Predict project completion date based on historical data."""
    project_tasks = [t for t in state.tasks if t.project == project_name]
    if not project_tasks:
        return {"error": "No tasks found for project"}
    
    done_tasks = [t for t in project_tasks if t.status == "DONE"]
    pending_tasks = [t for t in project_tasks if t.status != "DONE"]
    
    if not done_tasks:
        return {
            "project": project_name,
            "predicted_completion": None,
            "confidence": "low",
            "message": "Insufficient data - no completed tasks yet"
        }
    
    # Calculate average time to complete tasks
    today = datetime.now()
    completion_times = []
    
    for task in done_tasks:
        try:
            created = datetime.fromisoformat(task.created_at)
            # Estimate completion time (use time_logged if available, else use created->now)
            if task.time_logged:
                completion_times.append(task.time_logged / 60)  # Convert to hours
            else:
                # Rough estimate: assume task was completed recently if no time logged
                days_diff = (today - created).days
                if days_diff > 0:
                    completion_times.append(days_diff * 8)  # Assume 8 hours per day
        except Exception:
            continue
    
    if not completion_times:
        return {
            "project": project_name,
            "predicted_completion": None,
            "confidence": "low",
            "message": "Cannot calculate - no time data available"
        }
    
    avg_hours_per_task = sum(completion_times) / len(completion_times)
    total_pending_hours = len(pending_tasks) * avg_hours_per_task
    
    # Estimate completion date
    # Assume 8 hours per day of work
    work_days_needed = total_pending_hours / 8
    predicted_date = today + timedelta(days=work_days_needed)
    
    # Calculate confidence based on data quality
    tasks_with_time = len([t for t in done_tasks if t.time_logged])
    confidence = "high" if tasks_with_time > len(done_tasks) * 0.7 else "medium" if tasks_with_time > 0 else "low"
    
    return {
        "project": project_name,
        "predicted_completion": predicted_date.strftime("%Y-%m-%d"),
        "work_days_needed": round(work_days_needed, 1),
        "total_hours_remaining": round(total_pending_hours, 1),
        "avg_hours_per_task": round(avg_hours_per_task, 1),
        "confidence": confidence,
        "pending_tasks": len(pending_tasks)
    }


def get_all_project_insights(state: AssistantState) -> Dict[str, Dict]:
    """Get insights for all projects."""
    insights = {}
    
    for project in state.projects:
        risks = analyze_project_risks(state, project.name)
        prediction = predict_project_completion(state, project.name)
        
        insights[project.name] = {
            "risks": risks,
            "prediction": prediction,
            "summary": {
                "risk_level": risks.get("risk_level", "unknown"),
                "risk_score": risks.get("risk_score", 0),
                "predicted_completion": prediction.get("predicted_completion"),
                "confidence": prediction.get("confidence", "low")
            }
        }
    
    return insights

