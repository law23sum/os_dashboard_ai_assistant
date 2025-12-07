"""AI-powered smart task prioritization with context awareness."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

from .db import AssistantState, Task, Project
from .ai import generate_ai_reply, openai_available, get_agent_model


def calculate_task_priority_score(task: Task, state: AssistantState) -> float:
    """Calculate a priority score for a task based on multiple factors."""
    score = 0.0
    
    # Priority weight (40%)
    priority_weights = {
        "CRITICAL": 40.0,
        "HIGH": 30.0,
        "MEDIUM": 15.0,
        "LOW": 5.0
    }
    score += priority_weights.get(task.priority, 15.0)
    
    # Due date urgency (30%)
    if task.due_date:
        try:
            due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            days_until = (due_date - today).days
            
            if days_until < 0:
                score += 30.0  # Overdue
            elif days_until <= 1:
                score += 25.0  # Due today/tomorrow
            elif days_until <= 3:
                score += 20.0  # Due soon
            elif days_until <= 7:
                score += 15.0  # Due this week
            elif days_until <= 14:
                score += 10.0  # Due in 2 weeks
            else:
                score += 5.0  # Not urgent
        except Exception:
            pass
    
    # Dependency status (15%)
    if task.depends_on:
        # Check if dependency is complete
        dep_task = next((t for t in state.tasks if t.id == task.depends_on), None)
        if dep_task and dep_task.status == "DONE":
            score += 15.0  # Ready to start
        elif dep_task and dep_task.status == "BLOCKED":
            score -= 5.0  # Blocked by blocked task
        else:
            score += 5.0  # Has dependency
    else:
        score += 10.0  # No dependencies - can start anytime
    
    # Project priority (10%)
    project = next((p for p in state.projects if p.name == task.project), None)
    if project:
        project_priority_weights = {
            "CRITICAL": 10.0,
            "HIGH": 7.5,
            "MEDIUM": 5.0,
            "LOW": 2.5
        }
        score += project_priority_weights.get(project.priority, 5.0)
    
    # Status weight (5%)
    status_weights = {
        "IN_PROGRESS": 5.0,  # Already started - finish it
        "TODO": 3.0,
        "BLOCKED": 0.0
    }
    score += status_weights.get(task.status, 3.0)
    
    return round(score, 2)


def get_smart_priority_order(state: AssistantState, limit: Optional[int] = None) -> List[Dict]:
    """Get tasks ordered by smart priority score."""
    tasks_with_scores = []
    
    for task in state.tasks:
        if task.status == "DONE":
            continue
        
        score = calculate_task_priority_score(task, state)
        tasks_with_scores.append({
            "task": task,
            "priority_score": score,
            "recommended_order": 0  # Will be set after sorting
        })
    
    # Sort by priority score (descending)
    tasks_with_scores.sort(key=lambda x: x["priority_score"], reverse=True)
    
    # Assign recommended order
    for i, item in enumerate(tasks_with_scores, 1):
        item["recommended_order"] = i
    
    if limit:
        tasks_with_scores = tasks_with_scores[:limit]
    
    return tasks_with_scores


def get_ai_prioritization_recommendations(state: AssistantState, top_n: int = 10) -> List[Dict]:
    """Get AI-powered prioritization recommendations."""
    if not openai_available():
        # Fallback to score-based prioritization
        return get_smart_priority_order(state, limit=top_n)
    
    try:
        # Get context about current tasks
        pending_tasks = [t for t in state.tasks if t.status != "DONE"][:20]
        if not pending_tasks:
            return []
        
        context = f"""
Current pending tasks ({len(pending_tasks)} shown):
{chr(10).join([f"{i+1}. {t.title} (Priority: {t.priority}, Status: {t.status}, Due: {t.due_date or 'None'}, Project: {t.project})" 
                for i, t in enumerate(pending_tasks)])}

Projects:
{chr(10).join([f"- {p.name} (Priority: {p.priority}, Status: {p.status})" for p in state.projects[:10]])}
"""
        
        prompt = f"""Analyze these tasks and recommend the top {top_n} tasks to work on next, considering:
1. Urgency (due dates)
2. Priority levels
3. Dependencies
4. Project priorities
5. Workload balance

{context}

Provide your recommendations as a numbered list with brief reasoning for each."""
        
        ai_response = generate_ai_reply(
            prompt,
            system_prompt="You are an expert task prioritization assistant. Provide clear, actionable recommendations.",
            model=get_agent_model("Sora")
        )
        
        # Parse AI response and match to tasks
        recommendations = []
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                continue
            
            # Try to extract task title or number
            text = line.lstrip('0123456789.-• ').strip()
            
            # Try to match to actual tasks
            for task in pending_tasks:
                if task.title.lower() in text.lower() or text.lower() in task.title.lower():
                    score = calculate_task_priority_score(task, state)
                    recommendations.append({
                        "task": task,
                        "priority_score": score,
                        "ai_reasoning": text,
                        "recommended_order": len(recommendations) + 1
                    })
                    break
        
        # If AI didn't provide enough, fill with score-based
        if len(recommendations) < top_n:
            scored = get_smart_priority_order(state, limit=top_n)
            existing_ids = {r["task"].id for r in recommendations}
            for item in scored:
                if item["task"].id not in existing_ids and len(recommendations) < top_n:
                    recommendations.append({
                        "task": item["task"],
                        "priority_score": item["priority_score"],
                        "ai_reasoning": "Recommended based on priority score",
                        "recommended_order": len(recommendations) + 1
                    })
        
        return recommendations[:top_n]
        
    except Exception as e:
        # Fallback to score-based
        return get_smart_priority_order(state, limit=top_n)


def suggest_task_reordering(state: AssistantState) -> Dict:
    """Suggest optimal task ordering based on multiple factors."""
    smart_order = get_smart_priority_order(state)
    ai_recommendations = get_ai_prioritization_recommendations(state, top_n=10)
    
    return {
        "score_based_order": smart_order[:20],  # Top 20 by score
        "ai_recommendations": ai_recommendations,
        "summary": {
            "total_pending": len([t for t in state.tasks if t.status != "DONE"]),
            "high_priority_pending": len([t for t in state.tasks 
                                          if t.status != "DONE" and t.priority in ["HIGH", "CRITICAL"]]),
            "overdue_count": len([t for t in state.tasks 
                                 if t.due_date and t.status != "DONE" 
                                 and datetime.strptime(t.due_date, "%Y-%m-%d").date() < datetime.now().date()])
        }
    }

