"""
Advanced Microsoft Office automation workflows
Includes intelligent document processing, template management, and cross-app workflows
"""
import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

from apis.microsoft_client import MicrosoftClient
from apis.openai_client import OpenAIClient
from logger import setup_logger

@dataclass
class DocumentTemplate:
    """Document template structure"""
    name: str
    type: str  # word, excel, powerpoint
    template_content: str
    variables: List[str]
    description: str

@dataclass
class WorkflowStep:
    """Workflow step definition"""
    action: str
    parameters: Dict[str, Any]
    condition: Optional[str] = None
    retry_count: int = 3

class AdvancedOfficeAutomation:
    """Advanced Office automation with AI-powered workflows"""
    
    def __init__(self, microsoft_client: MicrosoftClient, openai_client: OpenAIClient):
        self.microsoft = microsoft_client
        self.openai = openai_client
        self.logger = setup_logger("OfficeAutomation")
        self.templates = {}
        self.workflows = {}
        
    async def initialize(self):
        """Initialize automation system"""
        await self._load_templates()
        await self._load_workflows()
        self.logger.info("Office automation system initialized")
    
    # Template Management
    async def _load_templates(self):
        """Load document templates"""
        self.templates = {
            "meeting_notes": DocumentTemplate(
                name="Meeting Notes",
                type="word",
                template_content="""
                # Meeting Notes - {meeting_title}
                
                **Date:** {date}
                **Attendees:** {attendees}
                **Duration:** {duration}
                
                ## Agenda
                {agenda}
                
                ## Discussion Points
                {discussion}
                
                ## Action Items
                {action_items}
                
                ## Next Steps
                {next_steps}
                """,
                variables=["meeting_title", "date", "attendees", "duration", "agenda", "discussion", "action_items", "next_steps"],
                description="Standard meeting notes template"
            ),
            "project_report": DocumentTemplate(
                name="Project Status Report",
                type="word",
                template_content="""
                # Project Status Report - {project_name}
                
                **Report Date:** {report_date}
                **Project Manager:** {pm_name}
                **Status:** {status}
                
                ## Executive Summary
                {executive_summary}
                
                ## Completed Milestones
                {completed_milestones}
                
                ## Current Progress
                {current_progress}
                
                ## Risks and Issues
                {risks_issues}
                
                ## Budget Status
                {budget_status}
                
                ## Next Quarter Goals
                {next_goals}
                """,
                variables=["project_name", "report_date", "pm_name", "status", "executive_summary", 
                          "completed_milestones", "current_progress", "risks_issues", "budget_status", "next_goals"],
                description="Comprehensive project status report"
            ),
            "budget_tracker": DocumentTemplate(
                name="Budget Tracker",
                type="excel",
                template_content="""
                {
                    "worksheets": [
                        {
                            "name": "Summary",
                            "data": {
                                "headers": ["Category", "Budgeted", "Actual", "Variance", "% Used"],
                                "categories": "{budget_categories}"
                            }
                        },
                        {
                            "name": "Monthly_Breakdown",
                            "data": {
                                "headers": ["Month", "Income", "Expenses", "Net", "Cumulative"],
                                "months": "{months_data}"
                            }
                        }
                    ]
                }
                """,
                variables=["budget_categories", "months_data"],
                description="Comprehensive budget tracking spreadsheet"
            )
        }
    
    async def create_from_template(self, template_name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Create document from template with variable substitution"""
        try:
            if template_name not in self.templates:
                raise ValueError(f"Template '{template_name}' not found")
            
            template = self.templates[template_name]
            
            # Substitute variables in template
            content = template.template_content
            for var, value in variables.items():
                content = content.replace(f"{{{var}}}", str(value))
            
            # Create document based on type
            if template.type == "word":
                result = await self.microsoft.create_word_document(
                    title=variables.get("title", template.name),
                    content=content
                )
            elif template.type == "excel":
                # Parse JSON content for Excel
                excel_data = json.loads(content)
                result = await self.microsoft.create_excel_workbook(
                    title=variables.get("title", template.name),
                    worksheets_data=excel_data["worksheets"]
                )
            elif template.type == "powerpoint":
                slides_data = [{"title": template.name, "content": content}]
                result = await self.microsoft.create_powerpoint_presentation(
                    title=variables.get("title", template.name),
                    slides_data=slides_data
                )
            
            self.logger.info(f"Created document from template: {template_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create document from template: {e}")
            raise
    
    # AI-Powered Content Generation
    async def generate_meeting_notes(self, meeting_transcript: str, meeting_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured meeting notes from transcript using AI"""
        try:
            # AI prompt for extracting meeting information
            prompt = f"""
            Analyze this meeting transcript and extract structured information:
            
            Meeting Info:
            - Title: {meeting_info.get('title', 'Unknown')}
            - Date: {meeting_info.get('date', datetime.now().strftime('%Y-%m-%d'))}
            - Attendees: {meeting_info.get('attendees', 'Unknown')}
            
            Transcript:
            {meeting_transcript}
            
            Please extract and format:
            1. Key discussion points (bullet points)
            2. Action items with owners and deadlines
            3. Decisions made
            4. Next steps
            
            Format as JSON with keys: discussion_points, action_items, decisions, next_steps
            """
            
            ai_response = await self.openai.chat_completion(
                prompt,
                system_prompt="You are an expert meeting secretary who creates structured, professional meeting notes."
            )
            
            # Parse AI response
            try:
                extracted_info = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback to structured text parsing
                extracted_info = await self._parse_meeting_content(ai_response)
            
            # Create meeting notes document
            variables = {
                "meeting_title": meeting_info.get('title', 'Meeting'),
                "date": meeting_info.get('date', datetime.now().strftime('%Y-%m-%d')),
                "attendees": meeting_info.get('attendees', 'Unknown'),
                "duration": meeting_info.get('duration', 'Unknown'),
                "agenda": meeting_info.get('agenda', 'See discussion points'),
                "discussion": self._format_list(extracted_info.get('discussion_points', [])),
                "action_items": self._format_list(extracted_info.get('action_items', [])),
                "next_steps": self._format_list(extracted_info.get('next_steps', []))
            }
            
            document = await self.create_from_template("meeting_notes", variables)
            
            return {
                "document": document,
                "extracted_info": extracted_info,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate meeting notes: {e}")
            raise
    
    async def _parse_meeting_content(self, content: str) -> Dict[str, List[str]]:
        """Fallback parser for meeting content"""
        sections = {
            "discussion_points": [],
            "action_items": [],
            "decisions": [],
            "next_steps": []
        }
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if 'discussion' in line.lower():
                current_section = 'discussion_points'
            elif 'action' in line.lower():
                current_section = 'action_items'
            elif 'decision' in line.lower():
                current_section = 'decisions'
            elif 'next' in line.lower():
                current_section = 'next_steps'
            elif line.startswith('-') or line.startswith('•') and current_section:
                sections[current_section].append(line[1:].strip())
        
        return sections
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items for document"""
        if not items:
            return "None specified"
        return '\n'.join(f"- {item}" for item in items)
    
    # Advanced Excel Operations
    async def create_intelligent_dashboard(self, data_sources: List[Dict[str, Any]], 
                                         dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create intelligent Excel dashboard with charts and analysis"""
        try:
            # Analyze data to suggest chart types
            chart_suggestions = await self._analyze_data_for_charts(data_sources)
            
            # Create worksheets
            worksheets = []
            
            # Data worksheet
            for i, source in enumerate(data_sources):
                worksheets.append({
                    "name": f"Data_{i+1}",
                    "data": source["data"],
                    "charts": chart_suggestions.get(f"data_{i+1}", [])
                })
            
            # Dashboard worksheet
            dashboard_worksheet = await self._create_dashboard_worksheet(
                data_sources, chart_suggestions, dashboard_config
            )
            worksheets.append(dashboard_worksheet)
            
            # Create workbook
            workbook = await self.microsoft.create_excel_workbook(
                title=dashboard_config.get("title", "Intelligent Dashboard"),
                worksheets_data=worksheets
            )
            
            return {
                "workbook": workbook,
                "chart_suggestions": chart_suggestions,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create intelligent dashboard: {e}")
            raise
    
    async def _analyze_data_for_charts(self, data_sources: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze data to suggest appropriate chart types"""
        suggestions = {}
        
        for i, source in enumerate(data_sources):
            data = source["data"]
            chart_types = []
            
            # Simple heuristics for chart suggestions
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    # Check for time series data
                    if any('date' in str(key).lower() or 'time' in str(key).lower() for key in data[0].keys()):
                        chart_types.append("line")
                    
                    # Check for categorical data
                    if len(data) <= 20:  # Small dataset good for pie/bar
                        chart_types.extend(["bar", "pie"])
                    else:
                        chart_types.append("bar")
            
            suggestions[f"data_{i+1}"] = chart_types
        
        return suggestions
    
    async def _create_dashboard_worksheet(self, data_sources: List[Dict[str, Any]], 
                                        chart_suggestions: Dict[str, List[str]], 
                                        config: Dict[str, Any]) -> Dict[str, Any]:
        """Create dashboard worksheet layout"""
        return {
            "name": "Dashboard",
            "data": {
                "title": config.get("title", "Dashboard"),
                "summary_metrics": await self._calculate_summary_metrics(data_sources),
                "chart_layout": chart_suggestions,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    async def _calculate_summary_metrics(self, data_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary metrics from data sources"""
        metrics = {
            "total_records": sum(len(source.get("data", [])) for source in data_sources),
            "data_sources": len(data_sources),
            "generated_at": datetime.now().isoformat()
        }
        
        # Add more sophisticated metrics based on data analysis
        for i, source in enumerate(data_sources):
            data = source.get("data", [])
            if data and isinstance(data[0], dict):
                numeric_fields = [k for k, v in data[0].items() if isinstance(v, (int, float))]
                if numeric_fields:
                    for field in numeric_fields:
                        values = [row.get(field, 0) for row in data if isinstance(row.get(field), (int, float))]
                        if values:
                            metrics[f"source_{i+1}_{field}_avg"] = sum(values) / len(values)
                            metrics[f"source_{i+1}_{field}_max"] = max(values)
                            metrics[f"source_{i+1}_{field}_min"] = min(values)
        
        return metrics
    
    # Workflow Management
    async def _load_workflows(self):
        """Load predefined workflows"""
        self.workflows = {
            "weekly_report": [
                WorkflowStep("collect_data", {"sources": ["calendar", "emails", "tasks"]}),
                WorkflowStep("analyze_productivity", {"ai_analysis": True}),
                WorkflowStep("generate_report", {"template": "project_report"}),
                WorkflowStep("schedule_review", {"calendar_event": True})
            ],
            "meeting_followup": [
                WorkflowStep("extract_action_items", {"source": "meeting_notes"}),
                WorkflowStep("create_tasks", {"task_system": "outlook"}),
                WorkflowStep("schedule_followups", {"calendar": True}),
                WorkflowStep("send_summary", {"email": True})
            ]
        }
    
    async def execute_workflow(self, workflow_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a predefined workflow"""
        try:
            if workflow_name not in self.workflows:
                raise ValueError(f"Workflow '{workflow_name}' not found")
            
            workflow = self.workflows[workflow_name]
            results = []
            
            for step in workflow:
                try:
                    # Check condition if specified
                    if step.condition and not self._evaluate_condition(step.condition, context):
                        self.logger.info(f"Skipping step {step.action} - condition not met")
                        continue
                    
                    # Execute step
                    result = await self._execute_workflow_step(step, context)
                    results.append({
                        "step": step.action,
                        "result": result,
                        "status": "success"
                    })
                    
                    # Update context with result
                    context.update(result.get("context_updates", {}))
                    
                except Exception as e:
                    self.logger.error(f"Workflow step {step.action} failed: {e}")
                    if step.retry_count > 0:
                        # Implement retry logic
                        step.retry_count -= 1
                        results.append({
                            "step": step.action,
                            "result": {"error": str(e)},
                            "status": "retry"
                        })
                    else:
                        results.append({
                            "step": step.action,
                            "result": {"error": str(e)},
                            "status": "failed"
                        })
            
            return {
                "workflow": workflow_name,
                "results": results,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate workflow condition"""
        # Simple condition evaluation - can be expanded
        try:
            return eval(condition, {"context": context})
        except:
            return True
    
    async def _execute_workflow_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual workflow step"""
        action = step.action
        params = step.parameters
        
        if action == "collect_data":
            return await self._collect_workflow_data(params, context)
        elif action == "analyze_productivity":
            return await self._analyze_productivity(params, context)
        elif action == "generate_report":
            return await self._generate_workflow_report(params, context)
        elif action == "schedule_review":
            return await self._schedule_workflow_review(params, context)
        else:
            return {"message": f"Unknown action: {action}"}
    
    async def _collect_workflow_data(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data for workflow"""
        # Placeholder for data collection logic
        return {
            "data_collected": True,
            "sources": params.get("sources", []),
            "context_updates": {"data_ready": True}
        }
    
    async def _analyze_productivity(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze productivity using AI"""
        if params.get("ai_analysis"):
            analysis = await self.openai.chat_completion(
                "Analyze productivity metrics and provide insights",
                system_prompt="You are a productivity analyst providing actionable insights."
            )
            return {
                "analysis": analysis,
                "context_updates": {"analysis_complete": True}
            }
        return {"analysis": "Basic analysis completed"}
    
    async def _generate_workflow_report(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report from workflow data"""
        template_name = params.get("template", "project_report")
        variables = context.get("report_variables", {
            "project_name": "Weekly Workflow",
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "In Progress"
        })
        
        document = await self.create_from_template(template_name, variables)
        return {
            "document": document,
            "context_updates": {"report_generated": True}
        }
    
    async def _schedule_workflow_review(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule review meeting"""
        # Placeholder for calendar integration
        return {
            "meeting_scheduled": True,
            "context_updates": {"review_scheduled": True}
        }
    
    # Document Intelligence
    async def analyze_document_sentiment(self, document_id: str) -> Dict[str, Any]:
        """Analyze document sentiment and tone"""
        try:
            # Get document content
            document = await self.microsoft.get_word_document(document_id)
            content = document.get("content", "")
            
            # AI analysis
            analysis = await self.openai.chat_completion(
                f"Analyze the sentiment, tone, and key themes in this document:\n\n{content}",
                system_prompt="You are a document analyst. Provide sentiment analysis, tone assessment, and key themes. Format as JSON."
            )
            
            return {
                "document_id": document_id,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Document sentiment analysis failed: {e}")
            raise
    
    async def extract_action_items_from_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Extract action items from document using AI"""
        try:
            document = await self.microsoft.get_word_document(document_id)
            content = document.get("content", "")
            
            prompt = f"""
            Extract all action items from this document. For each action item, identify:
            1. The task description
            2. Assigned person (if mentioned)
            3. Due date (if mentioned)
            4. Priority level (if indicated)
            
            Document content:
            {content}
            
            Format as JSON array with objects containing: task, assignee, due_date, priority
            """
            
            ai_response = await self.openai.chat_completion(
                prompt,
                system_prompt="You are an expert at extracting actionable tasks from documents."
            )
            
            try:
                action_items = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback parsing
                action_items = self._parse_action_items_fallback(ai_response)
            
            return action_items
            
        except Exception as e:
            self.logger.error(f"Action item extraction failed: {e}")
            raise
    
    def _parse_action_items_fallback(self, content: str) -> List[Dict[str, Any]]:
        """Fallback parser for action items"""
        items = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['todo', 'action', 'task', 'follow up', 'complete']):
                items.append({
                    "task": line,
                    "assignee": "Unknown",
                    "due_date": "Not specified",
                    "priority": "Medium"
                })
        
        return items
    
    async def shutdown(self):
        """Shutdown automation system"""
        self.logger.info("Office automation system shutdown")