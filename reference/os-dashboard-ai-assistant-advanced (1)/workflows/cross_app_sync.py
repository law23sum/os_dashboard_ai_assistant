"""
Cross-application data synchronization and workflow automation
Orchestrates data flow between different applications
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from api_manager import APIManager
from logger import setup_logger

class SyncDirection(Enum):
    BIDIRECTIONAL = "bidirectional"
    ONE_WAY = "one_way"
    SOURCE_TO_TARGET = "source_to_target"

class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"

@dataclass
class SyncRule:
    """Data synchronization rule"""
    name: str
    source_app: str
    target_app: str
    data_type: str
    direction: SyncDirection
    frequency: str  # cron-like expression
    field_mapping: Dict[str, str]
    filters: Dict[str, Any] = None
    transformations: List[str] = None
    enabled: bool = True

@dataclass
class SyncResult:
    """Synchronization result"""
    rule_name: str
    status: SyncStatus
    records_processed: int
    records_synced: int
    conflicts: List[Dict[str, Any]]
    errors: List[str]
    execution_time: float
    timestamp: datetime

class CrossAppSynchronization:
    """Cross-application data synchronization system"""
    
    def __init__(self, api_manager: APIManager):
        self.api_manager = api_manager
        self.logger = setup_logger("CrossAppSync")
        self.sync_rules = []
        self.sync_history = []
        self.conflict_resolution_strategies = {}
        
    async def initialize(self):
        """Initialize synchronization system"""
        await self._load_sync_rules()
        await self._load_conflict_strategies()
        self.logger.info("Cross-app synchronization system initialized")
    
    # Synchronization Rules Management
    async def _load_sync_rules(self):
        """Load predefined synchronization rules"""
        self.sync_rules = [
            SyncRule(
                name="Calendar to Task Sync",
                source_app="google_calendar",
                target_app="microsoft_todo",
                data_type="events",
                direction=SyncDirection.ONE_WAY,
                frequency="*/15 * * * *",  # Every 15 minutes
                field_mapping={
                    "title": "subject",
                    "start_time": "due_date",
                    "description": "body"
                },
                filters={"event_type": "task"},
                transformations=["convert_datetime_format", "extract_action_items"]
            ),
            SyncRule(
                name="Email to CRM Sync",
                source_app="gmail",
                target_app="salesforce",
                data_type="contacts",
                direction=SyncDirection.BIDIRECTIONAL,
                frequency="0 */2 * * *",  # Every 2 hours
                field_mapping={
                    "from": "email",
                    "sender_name": "name",
                    "company": "account"
                },
                filters={"label": "customer"},
                transformations=["extract_contact_info", "deduplicate"]
            ),
            SyncRule(
                name="Git Issues to Project Management",
                source_app="github",
                target_app="microsoft_project",
                data_type="issues",
                direction=SyncDirection.ONE_WAY,
                frequency="0 9 * * *",  # Daily at 9 AM
                field_mapping={
                    "title": "task_name",
                    "body": "description",
                    "assignee": "assigned_to",
                    "labels": "categories"
                },
                transformations=["estimate_effort", "categorize_priority"]
            ),
            SyncRule(
                name="Meeting Notes to Knowledge Base",
                source_app="microsoft_onenote",
                target_app="confluence",
                data_type="notes",
                direction=SyncDirection.ONE_WAY,
                frequency="0 18 * * *",  # Daily at 6 PM
                field_mapping={
                    "title": "page_title",
                    "content": "content",
                    "tags": "labels"
                },
                filters={"section": "meeting_notes"},
                transformations=["extract_action_items", "format_markdown"]
            )
        ]
    
    async def execute_sync_rule(self, rule_name: str, force: bool = False) -> SyncResult:
        """Execute specific synchronization rule"""
        try:
            rule = next((r for r in self.sync_rules if r.name == rule_name), None)
            if not rule:
                raise ValueError(f"Sync rule '{rule_name}' not found")
            
            if not rule.enabled and not force:
                raise ValueError(f"Sync rule '{rule_name}' is disabled")
            
            start_time = datetime.now()
            self.logger.info(f"Starting sync: {rule_name}")
            
            # Get source data
            source_data = await self._get_source_data(rule)
            
            # Apply filters
            filtered_data = await self._apply_filters(source_data, rule.filters or {})
            
            # Apply transformations
            transformed_data = await self._apply_transformations(filtered_data, rule.transformations or [])
            
            # Map fields
            mapped_data = await self._map_fields(transformed_data, rule.field_mapping)
            
            # Sync to target
            sync_result = await self._sync_to_target(mapped_data, rule)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = SyncResult(
                rule_name=rule_name,
                status=SyncStatus.COMPLETED,
                records_processed=len(source_data),
                records_synced=sync_result["synced_count"],
                conflicts=sync_result.get("conflicts", []),
                errors=sync_result.get("errors", []),
                execution_time=execution_time,
                timestamp=datetime.now()
            )
            
            self.sync_history.append(result)
            self.logger.info(f"Sync completed: {rule_name} - {result.records_synced}/{result.records_processed} records")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Sync execution failed for {rule_name}: {e}")
            
            result = SyncResult(
                rule_name=rule_name,
                status=SyncStatus.FAILED,
                records_processed=0,
                records_synced=0,
                conflicts=[],
                errors=[str(e)],
                execution_time=0,
                timestamp=datetime.now()
            )
            
            self.sync_history.append(result)
            return result
    
    async def _get_source_data(self, rule: SyncRule) -> List[Dict[str, Any]]:
        """Get data from source application"""
        source_app = rule.source_app
        data_type = rule.data_type
        
        if source_app == "google_calendar" and data_type == "events":
            return await self._get_calendar_events()
        elif source_app == "gmail" and data_type == "contacts":
            return await self._get_email_contacts()
        elif source_app == "github" and data_type == "issues":
            return await self._get_github_issues()
        elif source_app == "microsoft_onenote" and data_type == "notes":
            return await self._get_onenote_pages()
        else:
            raise ValueError(f"Unsupported source: {source_app}/{data_type}")
    
    async def _get_calendar_events(self) -> List[Dict[str, Any]]:
        """Get calendar events from Google Calendar"""
        try:
            if "google" in self.api_manager.clients:
                events = await self.api_manager.clients["google"].get_calendar_events(max_results=100)
                return events
            return []
        except Exception as e:
            self.logger.error(f"Failed to get calendar events: {e}")
            return []
    
    async def _get_email_contacts(self) -> List[Dict[str, Any]]:
        """Get contacts from Gmail"""
        try:
            if "google" in self.api_manager.clients:
                emails = await self.api_manager.clients["google"].get_emails(max_results=50)
                # Extract unique contacts
                contacts = []
                seen_emails = set()
                
                for email in emails:
                    sender_email = email.get("from", "")
                    if sender_email and sender_email not in seen_emails:
                        contacts.append({
                            "email": sender_email,
                            "name": self._extract_name_from_email(sender_email),
                            "last_contact": email.get("date", ""),
                            "source": "gmail"
                        })
                        seen_emails.add(sender_email)
                
                return contacts
            return []
        except Exception as e:
            self.logger.error(f"Failed to get email contacts: {e}")
            return []
    
    def _extract_name_from_email(self, email_address: str) -> str:
        """Extract name from email address"""
        if "<" in email_address and ">" in email_address:
            return email_address.split("<")[0].strip().strip('"')
        return email_address.split("@")[0].replace(".", " ").title()
    
    async def _get_github_issues(self) -> List[Dict[str, Any]]:
        """Get issues from GitHub"""
        try:
            if "git" in self.api_manager.clients:
                repos = await self.api_manager.clients["git"].get_repositories()
                all_issues = []
                
                for repo in repos[:5]:  # Limit to first 5 repos
                    issues = await self.api_manager.clients["git"].get_issues(
                        repo["full_name"], state="open"
                    )
                    for issue in issues:
                        issue["repository"] = repo["name"]
                        all_issues.append(issue)
                
                return all_issues
            return []
        except Exception as e:
            self.logger.error(f"Failed to get GitHub issues: {e}")
            return []
    
    async def _get_onenote_pages(self) -> List[Dict[str, Any]]:
        """Get pages from OneNote"""
        try:
            if "microsoft" in self.api_manager.clients:
                notebooks = await self.api_manager.clients["microsoft"].get_onenote_notebooks()
                # Simplified - would need to get actual pages
                return [
                    {
                        "title": f"Meeting Notes - {datetime.now().strftime('%Y-%m-%d')}",
                        "content": "Sample meeting notes content",
                        "notebook": notebook["name"],
                        "created_date": datetime.now().isoformat()
                    }
                    for notebook in notebooks[:3]
                ]
            return []
        except Exception as e:
            self.logger.error(f"Failed to get OneNote pages: {e}")
            return []
    
    async def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to data"""
        if not filters:
            return data
        
        filtered_data = []
        for item in data:
            include_item = True
            
            for filter_key, filter_value in filters.items():
                item_value = item.get(filter_key)
                
                if isinstance(filter_value, str):
                    if item_value != filter_value:
                        include_item = False
                        break
                elif isinstance(filter_value, list):
                    if item_value not in filter_value:
                        include_item = False
                        break
                elif isinstance(filter_value, dict):
                    # Complex filter logic
                    if not self._evaluate_complex_filter(item_value, filter_value):
                        include_item = False
                        break
            
            if include_item:
                filtered_data.append(item)
        
        return filtered_data
    
    def _evaluate_complex_filter(self, value: Any, filter_config: Dict[str, Any]) -> bool:
        """Evaluate complex filter conditions"""
        operator = filter_config.get("operator", "equals")
        filter_value = filter_config.get("value")
        
        if operator == "equals":
            return value == filter_value
        elif operator == "contains":
            return filter_value in str(value)
        elif operator == "starts_with":
            return str(value).startswith(filter_value)
        elif operator == "greater_than":
            return value > filter_value
        elif operator == "less_than":
            return value < filter_value
        else:
            return True
    
    async def _apply_transformations(self, data: List[Dict[str, Any]], 
                                   transformations: List[str]) -> List[Dict[str, Any]]:
        """Apply data transformations"""
        transformed_data = data.copy()
        
        for transformation in transformations:
            if transformation == "convert_datetime_format":
                transformed_data = await self._convert_datetime_format(transformed_data)
            elif transformation == "extract_action_items":
                transformed_data = await self._extract_action_items(transformed_data)
            elif transformation == "extract_contact_info":
                transformed_data = await self._extract_contact_info(transformed_data)
            elif transformation == "deduplicate":
                transformed_data = await self._deduplicate_data(transformed_data)
            elif transformation == "estimate_effort":
                transformed_data = await self._estimate_effort(transformed_data)
            elif transformation == "categorize_priority":
                transformed_data = await self._categorize_priority(transformed_data)
            elif transformation == "format_markdown":
                transformed_data = await self._format_markdown(transformed_data)
        
        return transformed_data
    
    async def _convert_datetime_format(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert datetime formats"""
        for item in data:
            for key, value in item.items():
                if isinstance(value, str) and self._is_datetime_string(value):
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        item[key] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
        return data
    
    def _is_datetime_string(self, value: str) -> bool:
        """Check if string is a datetime"""
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        ]
        return any(re.match(pattern, value) for pattern in datetime_patterns)
    
    async def _extract_action_items(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract action items using AI"""
        if "openai" not in self.api_manager.clients:
            return data
        
        for item in data:
            content = item.get("content", "") or item.get("description", "") or item.get("body", "")
            if content:
                try:
                    action_items = await self.api_manager.clients["openai"].chat_completion(
                        f"Extract action items from this text: {content[:500]}",
                        system_prompt="Extract actionable tasks as a JSON array of strings."
                    )
                    
                    try:
                        parsed_actions = json.loads(action_items)
                        item["action_items"] = parsed_actions if isinstance(parsed_actions, list) else [action_items]
                    except:
                        item["action_items"] = [action_items] if action_items else []
                except:
                    item["action_items"] = []
        
        return data
    
    async def _extract_contact_info(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and enhance contact information"""
        for item in data:
            email = item.get("email", "")
            if email and "@" in email:
                domain = email.split("@")[1]
                item["company_domain"] = domain
                item["company_name"] = domain.split(".")[0].title()
        
        return data
    
    async def _deduplicate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate records"""
        seen = set()
        deduplicated = []
        
        for item in data:
            # Create a hash key for deduplication
            key_fields = ["email", "title", "name", "id"]
            key_values = []
            
            for field in key_fields:
                if field in item:
                    key_values.append(str(item[field]))
            
            if key_values:
                key = "|".join(key_values)
                if key not in seen:
                    seen.add(key)
                    deduplicated.append(item)
        
        return deduplicated
    
    async def _estimate_effort(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Estimate effort for tasks using AI"""
        if "openai" not in self.api_manager.clients:
            # Fallback estimation
            for item in data:
                item["estimated_hours"] = 2  # Default estimate
            return data
        
        for item in data:
            title = item.get("title", "")
            description = item.get("body", "") or item.get("description", "")
            
            if title:
                try:
                    estimate = await self.api_manager.clients["openai"].chat_completion(
                        f"Estimate effort in hours for this task: {title}. Description: {description[:200]}",
                        system_prompt="Provide only a number representing estimated hours (1-40)."
                    )
                    
                    try:
                        hours = float(re.findall(r'\d+\.?\d*', estimate)[0])
                        item["estimated_hours"] = min(40, max(1, hours))
                    except:
                        item["estimated_hours"] = 4  # Default
                except:
                    item["estimated_hours"] = 4
        
        return data
    
    async def _categorize_priority(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Categorize priority using AI"""
        if "openai" not in self.api_manager.clients:
            for item in data:
                item["priority"] = "medium"
            return data
        
        for item in data:
            title = item.get("title", "")
            labels = item.get("labels", [])
            
            if title:
                try:
                    priority = await self.api_manager.clients["openai"].chat_completion(
                        f"Categorize priority (low/medium/high/urgent) for: {title}. Labels: {labels}",
                        system_prompt="Respond with only one word: low, medium, high, or urgent."
                    )
                    
                    priority = priority.strip().lower()
                    if priority in ["low", "medium", "high", "urgent"]:
                        item["priority"] = priority
                    else:
                        item["priority"] = "medium"
                except:
                    item["priority"] = "medium"
        
        return data
    
    async def _format_markdown(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format content as markdown"""
        for item in data:
            content = item.get("content", "")
            if content:
                # Simple markdown formatting
                formatted = content.replace("\n\n", "\n\n---\n\n")
                item["content_markdown"] = formatted
        
        return data
    
    async def _map_fields(self, data: List[Dict[str, Any]], field_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """Map fields according to mapping configuration"""
        mapped_data = []
        
        for item in data:
            mapped_item = {}
            
            # Map specified fields
            for source_field, target_field in field_mapping.items():
                if source_field in item:
                    mapped_item[target_field] = item[source_field]
            
            # Copy unmapped fields
            for key, value in item.items():
                if key not in field_mapping and key not in mapped_item:
                    mapped_item[key] = value
            
            mapped_data.append(mapped_item)
        
        return mapped_data
    
    async def _sync_to_target(self, data: List[Dict[str, Any]], rule: SyncRule) -> Dict[str, Any]:
        """Sync data to target application"""
        target_app = rule.target_app
        data_type = rule.data_type
        
        synced_count = 0
        conflicts = []
        errors = []
        
        try:
            if target_app == "microsoft_todo" and data_type == "events":
                synced_count = await self._sync_to_microsoft_todo(data)
            elif target_app == "salesforce" and data_type == "contacts":
                synced_count = await self._sync_to_salesforce(data)
            elif target_app == "microsoft_project" and data_type == "issues":
                synced_count = await self._sync_to_microsoft_project(data)
            elif target_app == "confluence" and data_type == "notes":
                synced_count = await self._sync_to_confluence(data)
            else:
                errors.append(f"Unsupported target: {target_app}/{data_type}")
        
        except Exception as e:
            errors.append(str(e))
        
        return {
            "synced_count": synced_count,
            "conflicts": conflicts,
            "errors": errors
        }
    
    async def _sync_to_microsoft_todo(self, data: List[Dict[str, Any]]) -> int:
        """Sync data to Microsoft To-Do"""
        # Placeholder implementation
        self.logger.info(f"Syncing {len(data)} items to Microsoft To-Do")
        return len(data)
    
    async def _sync_to_salesforce(self, data: List[Dict[str, Any]]) -> int:
        """Sync data to Salesforce"""
        # Placeholder implementation
        self.logger.info(f"Syncing {len(data)} contacts to Salesforce")
        return len(data)
    
    async def _sync_to_microsoft_project(self, data: List[Dict[str, Any]]) -> int:
        """Sync data to Microsoft Project"""
        # Placeholder implementation
        self.logger.info(f"Syncing {len(data)} tasks to Microsoft Project")
        return len(data)
    
    async def _sync_to_confluence(self, data: List[Dict[str, Any]]) -> int:
        """Sync data to Confluence"""
        # Placeholder implementation
        self.logger.info(f"Syncing {len(data)} pages to Confluence")
        return len(data)
    
    # Conflict Resolution
    async def _load_conflict_strategies(self):
        """Load conflict resolution strategies"""
        self.conflict_resolution_strategies = {
            "timestamp_wins": self._resolve_by_timestamp,
            "source_wins": self._resolve_source_wins,
            "target_wins": self._resolve_target_wins,
            "merge_fields": self._resolve_merge_fields,
            "manual_review": self._resolve_manual_review
        }
    
    async def _resolve_by_timestamp(self, source_record: Dict[str, Any], 
                                  target_record: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict by choosing most recent record"""
        source_time = source_record.get("updated_at", source_record.get("created_at", ""))
        target_time = target_record.get("updated_at", target_record.get("created_at", ""))
        
        if source_time > target_time:
            return source_record
        else:
            return target_record
    
    async def _resolve_source_wins(self, source_record: Dict[str, Any], 
                                 target_record: Dict[str, Any]) -> Dict[str, Any]:
        """Source record always wins"""
        return source_record
    
    async def _resolve_target_wins(self, source_record: Dict[str, Any], 
                                 target_record: Dict[str, Any]) -> Dict[str, Any]:
        """Target record always wins"""
        return target_record
    
    async def _resolve_merge_fields(self, source_record: Dict[str, Any], 
                                  target_record: Dict[str, Any]) -> Dict[str, Any]:
        """Merge non-conflicting fields"""
        merged = target_record.copy()
        
        for key, value in source_record.items():
            if key not in merged or not merged[key]:
                merged[key] = value
        
        return merged
    
    async def _resolve_manual_review(self, source_record: Dict[str, Any], 
                                   target_record: Dict[str, Any]) -> Dict[str, Any]:
        """Mark for manual review"""
        return {
            "conflict_resolution": "manual_review_required",
            "source_record": source_record,
            "target_record": target_record,
            "timestamp": datetime.now().isoformat()
        }
    
    # Batch Operations
    async def execute_all_sync_rules(self, force: bool = False) -> List[SyncResult]:
        """Execute all enabled synchronization rules"""
        results = []
        
        for rule in self.sync_rules:
            if rule.enabled or force:
                try:
                    result = await self.execute_sync_rule(rule.name, force)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to execute sync rule {rule.name}: {e}")
                    results.append(SyncResult(
                        rule_name=rule.name,
                        status=SyncStatus.FAILED,
                        records_processed=0,
                        records_synced=0,
                        conflicts=[],
                        errors=[str(e)],
                        execution_time=0,
                        timestamp=datetime.now()
                    ))
        
        return results
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get overall synchronization status"""
        total_rules = len(self.sync_rules)
        enabled_rules = len([r for r in self.sync_rules if r.enabled])
        recent_executions = [r for r in self.sync_history if r.timestamp > datetime.now() - timedelta(hours=24)]
        
        successful_syncs = len([r for r in recent_executions if r.status == SyncStatus.COMPLETED])
        failed_syncs = len([r for r in recent_executions if r.status == SyncStatus.FAILED])
        
        return {
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "recent_executions": len(recent_executions),
            "successful_syncs_24h": successful_syncs,
            "failed_syncs_24h": failed_syncs,
            "last_execution": self.sync_history[-1].timestamp.isoformat() if self.sync_history else None,
            "sync_health": "healthy" if failed_syncs == 0 else "issues" if failed_syncs < successful_syncs else "critical"
        }
    
    async def shutdown(self):
        """Shutdown synchronization system"""
        self.logger.info("Cross-app synchronization system shutdown")