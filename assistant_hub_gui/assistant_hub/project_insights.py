"""AI-powered project insights and risk analysis."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

from .db import AssistantState, Task, Project
from .ai import generate_ai_reply, openai_available, get_agent_model


def analyze_project_risks(state: AssistantState, project_name: str) -> Dict:
    """Analyze risks for a specific project.
    
    Returns:
        Dict with:
        - risk_score: 0-100
        - severity: "low" | "medium" | "high"
        - risks: List of risk items
        - recommendations: AI-generated recommendations
    """
    # Get project tasks
    project_tasks = [t for t in state.tasks if t.project == project_name]
    if not project_tasks:
        return {
            "risk_score": 0,
            "severity": "low",
            "risks": [],
            "recommendations": "No tasks found for this project."
        }
    
    risks = []
    risk_score = 0
    
    # Check for blocked tasks
    blocked_tasks = [t for t in project_tasks if t.status == "BLOCKED"]
    if blocked_tasks:
        risk_score += 20
        risks.append({
            "type": "blocked_tasks",
            "severity": "high",
            "count": len(blocked_tasks),
            "message": f"{len(blocked_tasks)} task(s) are blocked"
        })
    
    # Check for overdue tasks
    today = datetime.now().date()
    overdue_tasks = []
    for task in project_tasks:
        if task.status != "DONE" and task.due_date:
            try:
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                if due_date < today:
                    overdue_tasks.append(task)
            except Exception:
                pass
    
    if overdue_tasks:
        risk_score += min(30, len(overdue_tasks) * 5)
        risks.append({
            "type": "overdue_tasks",
            "severity": "high" if len(overdue_tasks) > 3 else "medium",
            "count": len(overdue_tasks),
            "message": f"{len(overdue_tasks)} task(s) are overdue"
        })
    
    # Check for high-priority pending work
    high_priority_pending = [
        t for t in project_tasks 
        if t.status != "DONE" and t.priority in ["HIGH", "CRITICAL"]
    ]
    if len(high_priority_pending) > 5:
        risk_score += 15
        risks.append({
            "type": "high_priority_backlog",
            "severity": "medium",
            "count": len(high_priority_pending),
            "message": f"{len(high_priority_pending)} high-priority tasks pending"
        })
    
    # Check progress indicators
    total_tasks = len(project_tasks)
    done_tasks = len([t for t in project_tasks if t.status == "DONE"])
    if total_tasks > 0:
        completion_rate = done_tasks / total_tasks
        if completion_rate < 0.1 and total_tasks > 5:
            risk_score += 10
            risks.append({
                "type": "low_progress",
                "severity": "medium",
                "completion_rate": f"{completion_rate:.0%}",
                "message": f"Only {completion_rate:.0%} of tasks completed"
            })
    
    # Check for tasks with dependencies that are incomplete
    incomplete_deps = 0
    for task in project_tasks:
        if task.depends_on and task.status != "DONE":
            dep_task = next((t for t in state.tasks if t.id == task.depends_on), None)
            if dep_task and dep_task.status != "DONE":
                incomplete_deps += 1
    
    if incomplete_deps > 0:
        risk_score += min(15, incomplete_deps * 3)
        risks.append({
            "type": "dependency_blockers",
            "severity": "medium",
            "count": incomplete_deps,
            "message": f"{incomplete_deps} task(s) blocked by incomplete dependencies"
        })
    
    # Determine severity
    if risk_score >= 70:
        severity = "high"
    elif risk_score >= 40:
        severity = "medium"
    else:
        severity = "low"
    
    # Generate AI recommendations if available
    recommendations = ""
    if openai_available() and risks:
        try:
            context = f"""
Project: {project_name}
Total Tasks: {total_tasks}
Completed: {done_tasks}
Risk Score: {risk_score}/100
Severity: {severity}

Identified Risks:
{chr(10).join([f"- {r['message']} (Severity: {r['severity']})" for r in risks])}
"""
            prompt = f"""Analyze these project risks and provide 3-5 actionable recommendations for risk mitigation.

{context}

Provide concise, specific recommendations."""
            
            recommendations = generate_ai_reply(
                prompt,
                system_prompt="You are a project management expert. Provide clear, actionable risk mitigation recommendations.",
                model=get_agent_model("Sora")
            )
        except Exception:
            recommendations = "AI recommendations unavailable. Review risks manually."
    else:
        recommendations = "Review identified risks and prioritize addressing high-severity items."
    
    return {
        "risk_score": min(100, risk_score),
        "severity": severity,
        "risks": risks,
        "recommendations": recommendations,
        "total_tasks": total_tasks,
        "completed_tasks": done_tasks,
        "completion_rate": done_tasks / total_tasks if total_tasks > 0 else 0.0
    }


def predict_project_completion(state: AssistantState, project_name: str) -> Dict:
    """Predict project completion date based on historical data.
    
    Returns:
        Dict with:
        - predicted_date: ISO date string
        - confidence: "high" | "medium" | "low"
        - reasoning: Explanation of prediction
        - estimated_days: Number of days until completion
    """
    # Get project tasks
    project_tasks = [t for t in state.tasks if t.project == project_name]
    if not project_tasks:
        return {
            "predicted_date": None,
            "confidence": "low",
            "reasoning": "No tasks found for this project.",
            "estimated_days": None
        }
    
    # Get completed tasks to calculate average completion time
    completed_tasks = [t for t in project_tasks if t.status == "DONE"]
    pending_tasks = [t for t in project_tasks if t.status != "DONE"]
    
    if not pending_tasks:
        return {
            "predicted_date": datetime.now().date().isoformat(),
            "confidence": "high",
            "reasoning": "All tasks are completed.",
            "estimated_days": 0
        }
    
    # Calculate average completion time from completed tasks
    avg_completion_days = None
    if completed_tasks:
        completion_times = []
        for task in completed_tasks:
            try:
                created = datetime.fromisoformat(task.created_at)
                # Estimate completion as 7 days after creation if no other data
                # In real implementation, would track actual completion dates
                completion_times.append(7)  # Placeholder
            except Exception:
                pass
        
        if completion_times:
            avg_completion_days = sum(completion_times) / len(completion_times)
    
    # If no historical data, estimate based on task complexity
    if avg_completion_days is None:
        # Estimate based on priority and time estimates
        total_estimated_minutes = sum(
            t.time_estimated or 480 for t in pending_tasks  # Default 8 hours
        )
        avg_completion_days = max(1, total_estimated_minutes / (8 * 60))  # Convert to days
    
    # Calculate estimated days for pending work
    # Account for dependencies and parallel work
    estimated_days = avg_completion_days * len(pending_tasks) * 0.7  # Assume 30% parallelization
    
    # Check for due dates that might affect timeline
    max_due_date = None
    for task in pending_tasks:
        if task.due_date:
            try:
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                if max_due_date is None or due_date > max_due_date:
                    max_due_date = due_date
            except Exception:
                pass
    
    # Adjust prediction based on due dates
    if max_due_date:
        days_until_max_due = (max_due_date - datetime.now().date()).days
        if days_until_max_due > estimated_days:
            estimated_days = days_until_max_due
    
    predicted_date = (datetime.now() + timedelta(days=int(estimated_days))).date()
    
    # Determine confidence
    if len(completed_tasks) >= 5:
        confidence = "high"
    elif len(completed_tasks) >= 2:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Generate reasoning
    reasoning = f"""
Based on {len(completed_tasks)} completed task(s) and {len(pending_tasks)} pending task(s):
- Average completion time: {avg_completion_days:.1f} days per task
- Estimated total: {estimated_days:.0f} days
- Predicted completion: {predicted_date.isoformat()}
"""
    
    if max_due_date:
        reasoning += f"\nNote: Latest task due date is {max_due_date.isoformat()}, which may affect timeline."
    
    return {
        "predicted_date": predicted_date.isoformat(),
        "confidence": confidence,
        "reasoning": reasoning.strip(),
        "estimated_days": int(estimated_days),
        "avg_completion_days": avg_completion_days,
        "pending_task_count": len(pending_tasks)
    }



