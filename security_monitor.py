#!/usr/bin/env python3
"""Security Monitor CLI for OS Dashboard AI Assistant."""

import asyncio
import sys
import os
import json
from pathlib import Path
import argparse
from datetime import datetime, timedelta

# Add current directory to path for proper imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from assistant_core.dashboard_engine import DashboardEngine
from assistant_core.security_framework import ComplianceFramework
from config.logging_config import setup_logger

class SecurityMonitor:
    """Command-line interface for security monitoring."""

    def __init__(self):
        self.dashboard_engine = None

    async def initialize(self):
        """Initialize the security monitor."""
        setup_logger()
        self.dashboard_engine = DashboardEngine()
        await self.dashboard_engine.initialize_security_framework()
        print("🔒 Security Monitor initialized")

    async def show_dashboard(self, args):
        """Show security dashboard."""
        try:
            dashboard = await self.dashboard_engine.get_security_dashboard()

            print("\n🔒 Security Dashboard")
            print("=" * 50)
            print(f"Security Score: {dashboard['security_score']}/100")
            print(f"Active Incidents: {dashboard['active_incidents']}")
            print(f"Resolved Incidents: {dashboard['resolved_incidents']}")
            print()

            if dashboard['threat_distribution']:
                print("Threat Distribution:")
                for threat_type, count in dashboard['threat_distribution'].items():
                    print(f"  {threat_type}: {count}")
                print()

            if dashboard['compliance_status']:
                print("Compliance Status:")
                for framework, status in dashboard['compliance_status'].items():
                    score = status['score']
                    compliance = "✅ Compliant" if score >= 80 else "❌ Non-compliant"
                    print(f"  {framework.upper()}: {score}/100 - {compliance}")
                print()

            if dashboard['recent_incidents']:
                print("Recent Security Incidents:")
                for incident in dashboard['recent_incidents'][:5]:
                    print(f"  {incident['detected_at'][:19]} - {incident['title']} ({incident['threat_level']})")

        except Exception as e:
            print(f"❌ Error retrieving security dashboard: {e}")

    async def run_compliance_assessment(self, args):
        """Run compliance assessment."""
        try:
            framework_name = args.framework.lower()
            if framework_name not in [f.value for f in ComplianceFramework]:
                print(f"❌ Unknown framework: {framework_name}")
                print(f"Available frameworks: {[f.value for f in ComplianceFramework]}")
                return

            print(f"📋 Running compliance assessment for {framework_name.upper()}...")

            report = await self.dashboard_engine.run_compliance_assessment(framework_name)

            print(f"\n📊 {framework_name.upper()} Compliance Report")
            print("=" * 50)
            print(f"Assessment Date: {report.assessment_date}")
            print(f"Compliance Score: {report.compliance_score}/100")

            if report.violations:
                print(f"\n❌ Violations Found ({len(report.violations)}):")
                for violation in report.violations[:5]:  # Show first 5
                    print(f"  • {violation['rule_id']}: {violation['description']}")

            if report.recommendations:
                print(f"\n💡 Recommendations ({len(report.recommendations)}):")
                for rec in report.recommendations[:5]:  # Show first 5
                    print(f"  • {rec}")

            print(f"\nNext Assessment: {report.next_assessment}")

        except Exception as e:
            print(f"❌ Error running compliance assessment: {e}")

    async def list_incidents(self, args):
        """List security incidents."""
        try:
            dashboard = await self.dashboard_engine.get_security_dashboard()
            incidents = dashboard.get('recent_incidents', [])

            if not incidents:
                print("✅ No recent security incidents found.")
                return

            print(f"\n🚨 Security Incidents ({len(incidents)} found)")
            print("=" * 60)

            for incident in incidents:
                print(f"ID: {incident['id']}")
                print(f"Title: {incident['title']}")
                print(f"Threat Level: {incident['threat_level']}")
                print(f"Status: {incident['status']}")
                print(f"Detected: {incident['detected_at'][:19]}")
                print("-" * 40)

        except Exception as e:
            print(f"❌ Error retrieving incidents: {e}")

    async def show_audit_trail(self, args):
        """Show audit trail."""
        try:
            # This would require implementing audit trail access in the security framework
            print("📋 Audit Trail Feature")
            print("=" * 30)
            print("Audit trail functionality is integrated into the security framework.")
            print("For detailed audit logs, access the security dashboard or implement")
            print("additional audit trail methods in the security framework.")

            # Show a basic summary
            dashboard = await self.dashboard_engine.get_security_dashboard()
            print(f"\nCurrent Security Score: {dashboard['security_score']}/100")
            print(f"Active Security Incidents: {dashboard['active_incidents']}")

        except Exception as e:
            print(f"❌ Error retrieving audit trail: {e}")

    async def analyze_threats(self, args):
        """Analyze threats from log file."""
        try:
            if not os.path.exists(args.logfile):
                print(f"❌ Log file not found: {args.logfile}")
                return

            print(f"🔍 Analyzing threats in: {args.logfile}")

            # Read log file and analyze for threats
            threats_found = []

            with open(args.logfile, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    # Simple threat detection patterns
                    if any(pattern in line.lower() for pattern in [
                        'failed login', 'unauthorized access', 'suspicious activity',
                        'brute force', 'sql injection', 'xss', 'malware'
                    ]):
                        threats_found.append({
                            'line': line_num,
                            'content': line.strip()[:100],
                            'type': 'log_anomaly'
                        })

            if threats_found:
                print(f"\n🚨 Potential Threats Found ({len(threats_found)}):")
                print("=" * 60)
                for threat in threats_found[:10]:  # Show first 10
                    print(f"Line {threat['line']}: {threat['content']}")
            else:
                print("✅ No obvious threats detected in log file.")

        except Exception as e:
            print(f"❌ Error analyzing log file: {e}")

def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Security Monitor for OS Dashboard AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python security_monitor.py dashboard
  python security_monitor.py compliance gdpr
  python security_monitor.py incidents
  python security_monitor.py audit
  python security_monitor.py analyze-threats /var/log/auth.log
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='Show security dashboard')
    dashboard_parser.set_defaults(func='show_dashboard')

    # Compliance assessment
    compliance_parser = subparsers.add_parser('compliance', help='Run compliance assessment')
    compliance_parser.add_argument('framework', choices=[f.value for f in ComplianceFramework],
                                  help='Compliance framework to assess')
    compliance_parser.set_defaults(func='run_compliance_assessment')

    # List incidents
    incidents_parser = subparsers.add_parser('incidents', help='List security incidents')
    incidents_parser.set_defaults(func='list_incidents')

    # Audit trail
    audit_parser = subparsers.add_parser('audit', help='Show audit trail')
    audit_parser.add_argument('--user', help='Filter by user')
    audit_parser.add_argument('--days', type=int, default=7, help='Days to look back')
    audit_parser.set_defaults(func='show_audit_trail')

    # Threat analysis
    analyze_parser = subparsers.add_parser('analyze-threats', help='Analyze threats in log file')
    analyze_parser.add_argument('logfile', help='Path to log file to analyze')
    analyze_parser.set_defaults(func='analyze_threats')

    return parser

async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        return

    monitor = SecurityMonitor()
    await monitor.initialize()

    # Call the appropriate method
    func_name = args.func
    if hasattr(monitor, func_name):
        await getattr(monitor, func_name)(args)
    else:
        print(f"❌ Unknown command: {func_name}")

if __name__ == "__main__":
    asyncio.run(main())
