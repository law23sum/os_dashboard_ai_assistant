"""
Advanced main application demonstrating all OS Dashboard AI Assistant features
"""
import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

from api_manager import get_api_manager
from advanced.office_automation import AdvancedOfficeAutomation
from advanced.email_intelligence import AdvancedEmailIntelligence
from advanced.smart_calendar import SmartCalendarManager
from advanced.git_workflow_automation import AdvancedGitWorkflowAutomation
from workflows.cross_app_sync import CrossAppSynchronization
from ui.dashboard_components import DashboardUIGenerator
from logger import setup_logger

class AdvancedOSDashboard:
    """Advanced OS Dashboard AI Assistant with full feature set"""
    
    def __init__(self):
        self.logger = setup_logger("AdvancedOSDashboard")
        self.api_manager = None
        self.office_automation = None
        self.email_intelligence = None
        self.smart_calendar = None
        self.git_automation = None
        self.cross_app_sync = None
        self.dashboard_ui = None
        
    async def initialize(self):
        """Initialize all advanced systems"""
        self.logger.info("🚀 Initializing Advanced OS Dashboard AI Assistant...")
        
        # Initialize API Manager
        self.api_manager = await get_api_manager()
        init_results = await self.api_manager.initialize()
        
        available_apis = [api for api, status in init_results.items() if status]
        self.logger.info(f"✅ Available APIs: {available_apis}")
        
        # Initialize advanced modules
        if "microsoft" in self.api_manager.clients and "openai" in self.api_manager.clients:
            self.office_automation = AdvancedOfficeAutomation(
                self.api_manager.clients["microsoft"],
                self.api_manager.clients["openai"]
            )
            await self.office_automation.initialize()
            self.logger.info("✅ Office Automation initialized")
        
        if "google" in self.api_manager.clients and "openai" in self.api_manager.clients:
            self.email_intelligence = AdvancedEmailIntelligence(
                self.api_manager.clients["google"],
                self.api_manager.clients["openai"]
            )
            await self.email_intelligence.initialize()
            self.logger.info("✅ Email Intelligence initialized")
            
            self.smart_calendar = SmartCalendarManager(
                self.api_manager.clients["google"],
                self.api_manager.clients["openai"],
                self.api_manager.clients.get("apple_calendar")
            )
            await self.smart_calendar.initialize()
            self.logger.info("✅ Smart Calendar initialized")
        
        if "git" in self.api_manager.clients and "openai" in self.api_manager.clients:
            self.git_automation = AdvancedGitWorkflowAutomation(
                self.api_manager.clients["git"],
                self.api_manager.clients["openai"]
            )
            await self.git_automation.initialize()
            self.logger.info("✅ Git Workflow Automation initialized")
        
        # Initialize cross-app synchronization
        self.cross_app_sync = CrossAppSynchronization(self.api_manager)
        await self.cross_app_sync.initialize()
        self.logger.info("✅ Cross-App Synchronization initialized")
        
        # Initialize dashboard UI
        self.dashboard_ui = DashboardUIGenerator(self.api_manager)
        await self.dashboard_ui.initialize()
        self.logger.info("✅ Dashboard UI initialized")
        
        self.logger.info("🎉 Advanced OS Dashboard AI Assistant fully initialized!")
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration of all features"""
        self.logger.info("🎬 Starting Comprehensive Feature Demonstration...")
        
        # Demo 1: Intelligent Email Processing
        await self._demo_email_intelligence()
        
        # Demo 2: Smart Calendar Management
        await self._demo_smart_calendar()
        
        # Demo 3: Office Automation Workflows
        await self._demo_office_automation()
        
        # Demo 4: Git Workflow Automation
        await self._demo_git_automation()
        
        # Demo 5: Cross-App Synchronization
        await self._demo_cross_app_sync()
        
        # Demo 6: Dashboard Generation
        await self._demo_dashboard_generation()
        
        self.logger.info("🏁 Comprehensive demonstration completed!")
    
    async def _demo_email_intelligence(self):
        """Demonstrate email intelligence features"""
        if not self.email_intelligence:
            self.logger.warning("⚠️ Email Intelligence not available - skipping demo")
            return
        
        self.logger.info("\n📧 === EMAIL INTELLIGENCE DEMO ===")
        
        try:
            # Process inbox intelligently
            self.logger.info("🔍 Processing inbox with AI analysis...")
            inbox_analysis = await self.email_intelligence.process_inbox_intelligently(max_emails=10)
            
            self.logger.info(f"📊 Processed {inbox_analysis['total_processed']} emails")
            self.logger.info(f"🚨 Found {len(inbox_analysis['urgent_emails'])} urgent emails")
            self.logger.info(f"⚡ Found {len(inbox_analysis['action_required'])} emails requiring action")
            
            # Show categories
            for category, emails in inbox_analysis['categories'].items():
                self.logger.info(f"📁 {category.title()}: {len(emails)} emails")
            
            # Generate analytics
            self.logger.info("📈 Generating email analytics...")
            analytics = await self.email_intelligence.generate_email_analytics(days=7)
            
            self.logger.info(f"📊 Weekly Analytics:")
            self.logger.info(f"   • Total emails: {analytics['total_emails']}")
            self.logger.info(f"   • Daily average: {analytics['daily_average']:.1f}")
            self.logger.info(f"   • Categories: {list(analytics['categories'].keys())}")
            
        except Exception as e:
            self.logger.error(f"❌ Email Intelligence demo failed: {e}")
    
    async def _demo_smart_calendar(self):
        """Demonstrate smart calendar features"""
        if not self.smart_calendar:
            self.logger.warning("⚠️ Smart Calendar not available - skipping demo")
            return
        
        self.logger.info("\n📅 === SMART CALENDAR DEMO ===")
        
        try:
            # Detect calendar conflicts
            self.logger.info("🔍 Detecting calendar conflicts...")
            conflicts = await self.smart_calendar.detect_calendar_conflicts(days_ahead=7)
            
            self.logger.info(f"⚠️ Found {len(conflicts)} potential conflicts")
            for conflict in conflicts[:3]:
                self.logger.info(f"   • {conflict.conflict_type.value}: {conflict.suggestion}")
            
            # Optimize weekly schedule
            self.logger.info("🎯 Optimizing weekly schedule...")
            optimization = await self.smart_calendar.optimize_weekly_schedule()
            
            current_analysis = optimization['current_analysis']
            self.logger.info(f"📊 Current Schedule Analysis:")
            self.logger.info(f"   • Total events: {current_analysis['total_events']}")
            self.logger.info(f"   • Productivity score: {current_analysis.get('productivity_score', 'N/A')}")
            
            suggestions = optimization['optimization_suggestions']
            self.logger.info(f"💡 Got {len(suggestions)} optimization suggestions")
            
            # Create smart event from natural language
            self.logger.info("🤖 Creating event from natural language...")
            event_request = "Schedule a team standup meeting for tomorrow at 9 AM for 30 minutes"
            smart_event = await self.smart_calendar.create_smart_event(event_request)
            
            self.logger.info(f"✅ Created event: {smart_event['created_event']['title']}")
            
        except Exception as e:
            self.logger.error(f"❌ Smart Calendar demo failed: {e}")
    
    async def _demo_office_automation(self):
        """Demonstrate office automation features"""
        if not self.office_automation:
            self.logger.warning("⚠️ Office Automation not available - skipping demo")
            return
        
        self.logger.info("\n📄 === OFFICE AUTOMATION DEMO ===")
        
        try:
            # Create document from template
            self.logger.info("📝 Creating document from template...")
            variables = {
                "meeting_title": "AI Dashboard Review",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "attendees": "Development Team",
                "duration": "1 hour",
                "agenda": "Review dashboard features and plan next iteration",
                "discussion": "Discussed current implementation and user feedback",
                "action_items": "Implement user suggestions and optimize performance",
                "next_steps": "Deploy updated version and gather more feedback"
            }
            
            document = await self.office_automation.create_from_template("meeting_notes", variables)
            self.logger.info(f"✅ Created document: {document.get('name', 'Meeting Notes')}")
            
            # Generate meeting notes from transcript
            self.logger.info("🎤 Generating meeting notes from transcript...")
            transcript = """
            John: Let's start with the dashboard review. The new email intelligence feature is working well.
            Sarah: I agree, but we should add more calendar integration features.
            Mike: The Git automation is saving us a lot of time. Can we expand it to include deployment?
            John: Good point. Let's add that to our backlog.
            Sarah: We should also improve the UI responsiveness.
            """
            
            meeting_info = {
                "title": "Dashboard Review Meeting",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "attendees": "John, Sarah, Mike"
            }
            
            notes_result = await self.office_automation.generate_meeting_notes(transcript, meeting_info)
            self.logger.info(f"✅ Generated meeting notes with AI analysis")
            
            # Execute workflow
            self.logger.info("⚙️ Executing automated workflow...")
            workflow_context = {
                "project_name": "OS Dashboard AI Assistant",
                "report_variables": {
                    "project_name": "OS Dashboard AI Assistant",
                    "report_date": datetime.now().strftime("%Y-%m-%d"),
                    "pm_name": "AI Assistant",
                    "status": "In Progress",
                    "executive_summary": "Dashboard development proceeding well with positive user feedback",
                    "completed_milestones": "Email intelligence, Calendar optimization, Git automation",
                    "current_progress": "UI improvements and cross-app synchronization",
                    "risks_issues": "None identified",
                    "budget_status": "On track",
                    "next_goals": "Enhanced analytics and mobile support"
                }
            }
            
            workflow_result = await self.office_automation.execute_workflow("weekly_report", workflow_context)
            self.logger.info(f"✅ Workflow executed: {workflow_result['status']}")
            
        except Exception as e:
            self.logger.error(f"❌ Office Automation demo failed: {e}")
    
    async def _demo_git_automation(self):
        """Demonstrate Git workflow automation"""
        if not self.git_automation:
            self.logger.warning("⚠️ Git Automation not available - skipping demo")
            return
        
        self.logger.info("\n🔧 === GIT WORKFLOW AUTOMATION DEMO ===")
        
        try:
            # Get repositories for analysis
            repos = await self.api_manager.clients["git"].get_repositories()
            if not repos:
                self.logger.warning("⚠️ No repositories found - using demo data")
                return
            
            repo_name = repos[0]["full_name"]
            self.logger.info(f"🔍 Analyzing repository: {repo_name}")
            
            # Analyze code changes
            self.logger.info("🔬 Performing AI code analysis...")
            code_analysis = await self.git_automation.analyze_code_changes(repo_name)
            
            self.logger.info(f"📊 Code Analysis Results:")
            self.logger.info(f"   • Quality Score: {code_analysis.quality_score}/10")
            self.logger.info(f"   • Complexity Score: {code_analysis.complexity_score}/10")
            self.logger.info(f"   • Maintainability: {code_analysis.maintainability.value}")
            self.logger.info(f"   • Security Issues: {len(code_analysis.security_issues)}")
            self.logger.info(f"   • Performance Issues: {len(code_analysis.performance_issues)}")
            
            # Analyze project health
            self.logger.info("🏥 Analyzing project health...")
            project_health = await self.git_automation.analyze_project_health(repos[0]["name"])
            
            self.logger.info(f"🎯 Project Health:")
            self.logger.info(f"   • Health Score: {project_health.health_score}/10")
            self.logger.info(f"   • Activity Level: {project_health.activity_level}")
            self.logger.info(f"   • Open Issues: {project_health.open_issues}")
            self.logger.info(f"   • Code Quality: {project_health.code_quality.value}")
            
            # Execute workflow (simulation)
            self.logger.info("⚙️ Executing Git workflow...")
            workflow_context = {
                "feature_name": "advanced-dashboard",
                "auto_execute_all": False  # Don't actually execute for demo
            }
            
            workflow_result = await self.git_automation.execute_workflow(
                "feature_development", repo_name, workflow_context
            )
            self.logger.info(f"✅ Workflow planned: {len(workflow_result['results'])} steps")
            
        except Exception as e:
            self.logger.error(f"❌ Git Automation demo failed: {e}")
    
    async def _demo_cross_app_sync(self):
        """Demonstrate cross-app synchronization"""
        if not self.cross_app_sync:
            self.logger.warning("⚠️ Cross-App Sync not available - skipping demo")
            return
        
        self.logger.info("\n🔄 === CROSS-APP SYNCHRONIZATION DEMO ===")
        
        try:
            # Get sync status
            self.logger.info("📊 Checking synchronization status...")
            sync_status = await self.cross_app_sync.get_sync_status()
            
            self.logger.info(f"🔄 Sync Status:")
            self.logger.info(f"   • Total Rules: {sync_status['total_rules']}")
            self.logger.info(f"   • Enabled Rules: {sync_status['enabled_rules']}")
            self.logger.info(f"   • Recent Executions: {sync_status['recent_executions']}")
            self.logger.info(f"   • Sync Health: {sync_status['sync_health']}")
            
            # Execute a sync rule
            self.logger.info("⚡ Executing sync rule...")
            sync_result = await self.cross_app_sync.execute_sync_rule("Calendar to Task Sync")
            
            self.logger.info(f"✅ Sync Result:")
            self.logger.info(f"   • Status: {sync_result.status.value}")
            self.logger.info(f"   • Records Processed: {sync_result.records_processed}")
            self.logger.info(f"   • Records Synced: {sync_result.records_synced}")
            self.logger.info(f"   • Execution Time: {sync_result.execution_time:.2f}s")
            
            if sync_result.errors:
                self.logger.warning(f"⚠️ Errors: {sync_result.errors}")
            
        except Exception as e:
            self.logger.error(f"❌ Cross-App Sync demo failed: {e}")
    
    async def _demo_dashboard_generation(self):
        """Demonstrate dashboard generation"""
        if not self.dashboard_ui:
            self.logger.warning("⚠️ Dashboard UI not available - skipping demo")
            return
        
        self.logger.info("\n📊 === DASHBOARD GENERATION DEMO ===")
        
        try:
            # Create default dashboard
            self.logger.info("🎨 Creating dashboard configuration...")
            widgets = await self.dashboard_ui.create_default_dashboard()
            
            self.logger.info(f"📱 Dashboard Widgets:")
            for widget in widgets:
                self.logger.info(f"   • {widget.title} ({widget.type})")
            
            # Generate dashboard HTML
            self.logger.info("🔧 Generating dashboard HTML...")
            dashboard_file = await self.dashboard_ui.save_dashboard_to_file(
                widgets, 
                theme="modern_dark", 
                filename="advanced_dashboard.html"
            )
            
            self.logger.info(f"✅ Dashboard saved to: {dashboard_file}")
            self.logger.info("🌐 Open the HTML file in your browser to view the dashboard!")
            
            # Generate light theme version
            light_dashboard_file = await self.dashboard_ui.save_dashboard_to_file(
                widgets, 
                theme="light_professional", 
                filename="advanced_dashboard_light.html"
            )
            
            self.logger.info(f"✅ Light theme dashboard saved to: {light_dashboard_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Dashboard Generation demo failed: {e}")
    
    async def run_interactive_mode(self):
        """Run interactive mode with advanced features"""
        self.logger.info("\n🎮 === INTERACTIVE MODE ===")
        self.logger.info("Available advanced commands:")
        self.logger.info("1. email-analysis - Run email intelligence analysis")
        self.logger.info("2. calendar-optimize - Optimize calendar schedule")
        self.logger.info("3. office-workflow <workflow_name> - Execute office workflow")
        self.logger.info("4. git-analyze <repo_name> - Analyze Git repository")
        self.logger.info("5. sync-execute <rule_name> - Execute sync rule")
        self.logger.info("6. dashboard-generate - Generate dashboard")
        self.logger.info("7. status - Show system status")
        self.logger.info("8. demo - Run full demonstration")
        self.logger.info("9. quit - Exit")
        
        while True:
            try:
                command = input("\n🤖 > ").strip().split()
                
                if not command:
                    continue
                
                if command[0] == "quit":
                    break
                elif command[0] == "demo":
                    await self.run_comprehensive_demo()
                elif command[0] == "email-analysis":
                    await self._demo_email_intelligence()
                elif command[0] == "calendar-optimize":
                    await self._demo_smart_calendar()
                elif command[0] == "office-workflow":
                    workflow_name = command[1] if len(command) > 1 else "weekly_report"
                    if self.office_automation:
                        result = await self.office_automation.execute_workflow(workflow_name, {})
                        print(f"✅ Workflow result: {result['status']}")
                    else:
                        print("❌ Office automation not available")
                elif command[0] == "git-analyze":
                    repo_name = command[1] if len(command) > 1 else None
                    if self.git_automation and repo_name:
                        analysis = await self.git_automation.analyze_code_changes(repo_name)
                        print(f"📊 Quality: {analysis.quality_score}/10, Complexity: {analysis.complexity_score}/10")
                    else:
                        print("❌ Git automation not available or repo name required")
                elif command[0] == "sync-execute":
                    rule_name = " ".join(command[1:]) if len(command) > 1 else "Calendar to Task Sync"
                    if self.cross_app_sync:
                        result = await self.cross_app_sync.execute_sync_rule(rule_name)
                        print(f"✅ Sync result: {result.status.value} - {result.records_synced} records")
                    else:
                        print("❌ Cross-app sync not available")
                elif command[0] == "dashboard-generate":
                    if self.dashboard_ui:
                        widgets = await self.dashboard_ui.create_default_dashboard()
                        filename = await self.dashboard_ui.save_dashboard_to_file(widgets)
                        print(f"✅ Dashboard generated: {filename}")
                    else:
                        print("❌ Dashboard UI not available")
                elif command[0] == "status":
                    await self._show_system_status()
                else:
                    print("❓ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"❌ Command failed: {e}")
    
    async def _show_system_status(self):
        """Show comprehensive system status"""
        print("\n📊 === SYSTEM STATUS ===")
        
        # API Status
        api_status = await self.api_manager.get_status()
        print("🔌 API Connections:")
        for name, status in api_status.items():
            status_icon = "✅" if status.connected else "❌"
            print(f"   {status_icon} {name}: {'Connected' if status.connected else 'Disconnected'}")
        
        # Module Status
        print("\n🧩 Advanced Modules:")
        modules = [
            ("Office Automation", self.office_automation),
            ("Email Intelligence", self.email_intelligence),
            ("Smart Calendar", self.smart_calendar),
            ("Git Automation", self.git_automation),
            ("Cross-App Sync", self.cross_app_sync),
            ("Dashboard UI", self.dashboard_ui)
        ]
        
        for name, module in modules:
            status_icon = "✅" if module else "❌"
            print(f"   {status_icon} {name}: {'Available' if module else 'Not Available'}")
        
        # Sync Status
        if self.cross_app_sync:
            sync_status = await self.cross_app_sync.get_sync_status()
            print(f"\n🔄 Synchronization Health: {sync_status['sync_health']}")
    
    async def shutdown(self):
        """Shutdown all systems"""
        self.logger.info("🔄 Shutting down Advanced OS Dashboard AI Assistant...")
        
        # Shutdown advanced modules
        if self.office_automation:
            await self.office_automation.shutdown()
        if self.email_intelligence:
            await self.email_intelligence.shutdown()
        if self.smart_calendar:
            await self.smart_calendar.shutdown()
        if self.git_automation:
            await self.git_automation.shutdown()
        if self.cross_app_sync:
            await self.cross_app_sync.shutdown()
        if self.dashboard_ui:
            await self.dashboard_ui.shutdown()
        
        # Shutdown API manager
        if self.api_manager:
            await self.api_manager.shutdown()
        
        self.logger.info("✅ Shutdown complete")

async def main():
    """Main application entry point"""
    dashboard = AdvancedOSDashboard()
    
    try:
        await dashboard.initialize()
        
        if len(sys.argv) > 1:
            if sys.argv[1] == "demo":
                await dashboard.run_comprehensive_demo()
            elif sys.argv[1] == "interactive":
                await dashboard.run_interactive_mode()
            elif sys.argv[1] == "dashboard":
                # Generate dashboard only
                if dashboard.dashboard_ui:
                    widgets = await dashboard.dashboard_ui.create_default_dashboard()
                    filename = await dashboard.dashboard_ui.save_dashboard_to_file(widgets)
                    print(f"✅ Dashboard generated: {filename}")
                else:
                    print("❌ Dashboard UI not available")
        else:
            # Default: run demo
            await dashboard.run_comprehensive_demo()
            
    except KeyboardInterrupt:
        print("\n⚠️ Application interrupted by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
    finally:
        await dashboard.shutdown()

if __name__ == "__main__":
    asyncio.run(main())