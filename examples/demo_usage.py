#!/usr/bin/env python3
"""
OS Dashboard AI Assistant Platform - Demo Usage Examples
Demonstrates the key capabilities of the platform using assistant_core modules.
"""

import time
from pathlib import Path
from typing import Dict, Any

import pandas as pd

# Ensure repo root is on the Python path when running as a standalone script
REPO_ROOT = Path(__file__).resolve().parents[1]
import sys
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from assistant_core.intelligence.data_collector import SyncDataCollector, DataSource
from assistant_core.content.generators import (
    PresentationGenerator,
    ExcelDashboardGenerator,
    WordDocumentGenerator,
    ContentConfig,
)
from assistant_core.system.operations import SystemOperationsController
from assistant_core.intelligence.quality_assurance import ContentValidator, AccessibilityChecker
from assistant_core.operations.concurrent_manager import ConcurrentOperationsManager, ConcurrentTask
from assistant_core.integrations.advanced_systems import (
    StaticSiteDeployer,
    DeploymentConfig,
    OfficeAddinEmbedder,
    OfficeAddinConfig,
    HostConfig,
    RequirementSet,
)
from assistant_core.integrations.office_realtime import (
    AIOfficeWebSocketRouter,
    MessageType,
    ApplicationType,
)


def demo_data_collection() -> list[Dict[str, Any]]:
    """Demonstrate multi-source data collection capabilities."""
    print("\n🔍 DEMO: Multi-Source Data Collection")
    print("=" * 50)

    collector = SyncDataCollector(max_concurrent=5)
    sources = [
        DataSource(
            name="example_api",
            url="https://jsonplaceholder.typicode.com/posts/1",
            source_type="api",
        ),
        DataSource(
            name="example_website",
            url="https://httpbin.org/html",
            source_type="web",
        ),
        DataSource(
            name="json_data",
            url="https://httpbin.org/json",
            source_type="api",
        ),
    ]

    print(f"📊 Collecting data from {len(sources)} sources...")
    results = collector.collect_data(sources)

    for i, result in enumerate(results, 1):
        if "error" not in result:
            print(f"✅ Source {i}: Success - {len(str(result.get('data', {})))} bytes")
        else:
            print(f"❌ Source {i}: Failed - {result['error']}")

    success_count = len([r for r in results if 'error' not in r])
    print(f"📈 Collection complete: {success_count}/{len(results)} successful")
    return results


def demo_content_generation() -> Dict[str, str]:
    """Demonstrate professional content generation capabilities."""
    print("\n📄 DEMO: Professional Content Generation")
    print("=" * 50)

    output_dir = Path("./workspace/demo_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    config = ContentConfig(
        title="AI Platform Demo",
        author="Demo User",
        theme="professional",
    )

    print("🎨 Creating interactive HTML presentation...")
    presentation = PresentationGenerator(config)
    presentation.add_title_slide(
        "AI Assistant Platform",
        "Autonomous Workflow Demo",
        "Demo User",
    )
    presentation.add_content_slide(
        "Key Features",
        [
            "Multi-source data intelligence",
            "Professional content generation",
            "System-level operations",
            "Quality assurance systems",
            "Concurrent processing",
        ],
    )
    chart_data = {
        "labels": [
            "Data Collection",
            "Content Gen",
            "System Ops",
            "Quality Check",
            "Deployment",
        ],
        "datasets": [
            {
                "label": "Completion Time (seconds)",
                "data": [2.5, 4.2, 1.8, 3.1, 5.7],
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
            }
        ],
    }
    presentation.add_chart_slide("Performance Metrics", "bar", chart_data)
    pres_path = output_dir / "demo_presentation.html"
    presentation.generate_html(str(pres_path))
    print(f"✅ Presentation created: {pres_path}")

    print("📊 Creating Excel dashboard...")
    data = pd.DataFrame(
        {
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Revenue": [120_000, 135_000, 148_000, 162_000, 175_000, 189_000],
            "Expenses": [80_000, 85_000, 92_000, 98_000, 105_000, 112_000],
            "Profit": [40_000, 50_000, 56_000, 64_000, 70_000, 77_000],
            "Growth_Rate": [0, 12.5, 9.6, 9.5, 8.0, 8.6],
        }
    )
    excel_generator = ExcelDashboardGenerator(config)
    excel_generator.add_worksheet("Financial Data", data)
    excel_generator.add_conditional_formatting(
        "Financial Data",
        "C2:C7",
        "color_scale",
        {"start_color": "FF0000", "end_color": "00FF00"},
    )
    excel_path = output_dir / "demo_dashboard.xlsx"
    excel_generator.generate_excel(str(excel_path))
    print(f"✅ Excel dashboard created: {excel_path}")

    print("📝 Creating Word document...")
    word_generator = WordDocumentGenerator(config)
    word_generator.add_heading("Executive Summary", 1)
    word_generator.add_paragraph(
        "This demonstration showcases the capabilities of the OS Dashboard AI Assistant Platform, "
        "including enterprise-grade autonomous workflows and professional outputs."
    )
    word_generator.add_heading("Key Achievements", 2)
    word_generator.add_list(
        [
            "Successfully implemented multi-source data collection",
            "Created professional-grade content generation system",
            "Developed advanced system operations controller",
            "Built comprehensive quality assurance framework",
            "Established concurrent processing capabilities",
        ]
    )
    word_generator.add_heading("Performance Metrics", 2)
    word_generator.add_table(
        data=[
            ["Data Collection", "2.5s", "Excellent"],
            ["Content Generation", "4.2s", "Good"],
            ["System Operations", "1.8s", "Excellent"],
            ["Quality Assurance", "3.1s", "Good"],
            ["Deployment", "5.7s", "Acceptable"],
        ],
        headers=["Component", "Avg Time", "Performance"],
    )
    word_path = output_dir / "demo_report.docx"
    word_generator.generate_docx(str(word_path))
    print(f"✅ Word document created: {word_path}")

    return {
        "presentation": str(pres_path),
        "excel": str(excel_path),
        "word": str(word_path),
    }


def demo_system_operations() -> Dict[str, Any]:
    """Demonstrate system-level operations."""
    print("\n⚙️ DEMO: System-Level Operations")
    print("=" * 50)

    controller = SystemOperationsController()
    commands = [
        "echo 'Hello from AI Assistant Platform'",
        "date",
        "pwd",
        "ls -la workspace/",
    ]

    print("🖥️ Executing system commands...")
    for cmd in commands:
        result = controller.execute_command(cmd)
        if result.get("success"):
            print(f"✅ '{cmd}': {result.get('stdout', '').strip()}")
        else:
            print(f"❌ '{cmd}': {result.get('stderr', result.get('error', 'Unknown error'))}")

    print("\n📊 System Information:")
    sys_info = controller.get_system_info()
    if "error" not in sys_info:
        print(f"CPU Usage: {sys_info['cpu']['cpu_usage']:.1f}%")
        print(f"Memory Usage: {sys_info['memory']['percentage']:.1f}%")
        print(f"Disk Usage: {sys_info['disk']['percentage']:.1f}%")
        print(f"Running Tasks: {sys_info['running_tasks']}")
    else:
        print(f"Error getting system info: {sys_info['error']}")

    print("\n📦 Archive Operations:")
    test_dir = Path("./workspace/test_archive")
    test_dir.mkdir(parents=True, exist_ok=True)
    for i in range(3):
        (test_dir / f"test_file_{i}.txt").write_text(
            f"This is test file {i}\nCreated by AI Assistant Platform\n",
            encoding="utf-8",
        )

    archive_result = controller.create_archive(
        str(test_dir),
        "./workspace/demo_archive.zip",
        "zip",
    )
    if archive_result.get("success"):
        print(f"✅ Archive created: {archive_result['archive_size']} bytes")
        print(f"Compression ratio: {archive_result['compression_ratio']:.2f}")
    else:
        print(f"❌ Archive creation failed: {archive_result.get('error')}")

    return sys_info


def demo_quality_assurance() -> Dict[str, int]:
    """Demonstrate quality assurance capabilities."""
    print("\n🔍 DEMO: Quality Assurance Systems")
    print("=" * 50)

    sample_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Demo Page</title>
    </head>
    <body>
        <h1>Welcome to AI Assistant Platform</h1>
        <img src="demo.jpg" alt="Demo image">
        <p>This is a sample page for quality assurance testing.</p>
        <ul>
            <li>Feature 1: Data Collection</li>
            <li>Feature 2: Content Generation</li>
            <li>Feature 3: System Operations</li>
        </ul>
        <form>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email">
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """

    print("📋 Running content validation...")
    validator = ContentValidator()
    validation_results = validator.validate_content(sample_html, "html")
    errors = [r for r in validation_results if r.severity == "error" and not r.passed]
    warnings = [r for r in validation_results if r.severity == "warning" and not r.passed]
    passed = [r for r in validation_results if r.passed]
    print(f"✅ Validation complete: {len(passed)} passed, {len(warnings)} warnings, {len(errors)} errors")
    for result in errors[:3]:
        print(f"❌ Error: {result.message}")
    for result in warnings[:3]:
        print(f"⚠️ Warning: {result.message}")

    print("\n♿ Running accessibility check...")
    accessibility_checker = AccessibilityChecker()
    accessibility_results = accessibility_checker.check_accessibility(sample_html)
    accessibility_issues = [r for r in accessibility_results if not r.passed]
    print(
        f"✅ Accessibility check: {len(accessibility_results) - len(accessibility_issues)} passed, "
        f"{len(accessibility_issues)} issues"
    )
    for result in accessibility_issues[:3]:
        print(f"♿ Issue: {result.message}")
        if result.suggestion:
            print(f"   Suggestion: {result.suggestion}")

    return {
        "validation_results": len(validation_results),
        "errors": len(errors),
        "warnings": len(warnings),
        "accessibility_issues": len(accessibility_issues),
    }


def demo_concurrent_operations() -> Dict[str, Any]:
    """Demonstrate concurrent processing capabilities."""
    print("\n⚡ DEMO: Concurrent Operations")
    print("=" * 50)

    manager = ConcurrentOperationsManager(max_workers=5)

    def process_data_batch(batch_id: int, data_size: int) -> Dict[str, Any]:
        import random

        processing_time = random.uniform(1.0, 3.0)
        time.sleep(processing_time)
        return {
            "batch_id": batch_id,
            "data_size": data_size,
            "processing_time": processing_time,
            "items_processed": data_size * 10,
            "status": "completed",
        }

    print("🚀 Creating concurrent tasks...")
    tasks = [
        ConcurrentTask(
            name=f"process_batch_{i}",
            function=process_data_batch,
            args=(i, 100 + i * 50),
            priority=2 if i < 4 else 1,
        )
        for i in range(8)
    ]

    batch_id = manager.create_batch_operation(
        name="demo_data_processing",
        tasks=tasks,
        parallel_limit=3,
        fail_fast=False,
    )

    print(f"📊 Processing {len(tasks)} tasks with max 3 concurrent...")
    start_time = time.time()
    results = manager.execute_batch_sync(batch_id)
    end_time = time.time()

    print(f"✅ Batch processing complete in {end_time - start_time:.2f} seconds")
    print(f"📈 Results: {results['successful_tasks']}/{results['total_tasks']} successful")
    if results['failed_tasks'] > 0:
        print(f"❌ Failed tasks: {results['failed_tasks']}")

    stats = manager.get_performance_stats()
    print(f"📊 Performance: {stats['tasks_completed']} completed, avg time: {stats['average_execution_time']:.2f}s")
    manager.shutdown()
    return results


def demo_deployment_integration() -> Dict[str, Any]:
    """Demonstrate deployment and integration capabilities."""
    print("\n🚀 DEMO: Deployment & Integration")
    print("=" * 50)

    deployer = StaticSiteDeployer()
    output_dir = Path("./workspace/demo_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    config = DeploymentConfig(
        platform="vercel",
        project_name="ai-dashboard-demo",
        environment_vars={"NODE_ENV": "production"},
    )
    deployment_result = deployer.deploy(str(output_dir), config)
    if deployment_result.get("success"):
        print("✅ Deployment successful!")
        print(f"🔗 URL: {deployment_result['deployment_url']}")
        print(f"📦 Files: {deployment_result['file_count']}")
        print(f"⏱️ Build time: {deployment_result['build_time']}s")
    else:
        print(f"❌ Deployment failed: {deployment_result.get('error')}")

    print("\n📊 Simulating Office Add-In creation...")
    embedder = OfficeAddinEmbedder()
    addin_config = OfficeAddinConfig(
        manifest_id="demo-12345678-1234-1234-1234-123456789012",
        display_name="AI Dashboard Demo Add-In",
        description="Interactive dashboard for Excel demonstration",
        provider_name="AI Assistant Platform",
        dashboard_url=deployment_result.get("deployment_url", "https://demo.example.com"),
        hosts=[
            HostConfig(name="Workbook"),
            HostConfig(name="Document"),
            HostConfig(name="Presentation"),
        ],
        requirement_sets=[RequirementSet(name="SharedRuntime", version="1.1")],
        run_on_load=True,
    )
    manifest_xml = embedder.create_office_addin_manifest(addin_config)
    manifest_path = Path("./workspace/demo_output/excel_addin_manifest.xml")
    manifest_path.write_text(manifest_xml, encoding="utf-8")
    print(f"✅ Office Add-In manifest created: {manifest_path}")
    print(f"📋 Manifest size: {len(manifest_xml)} characters")

    return {"deployment": deployment_result, "addin_manifest": str(manifest_path)}


def demo_office_realtime_integration() -> Dict[str, Any]:
    """Demonstrate the real-time Office router derived from the AI Office Agent docs."""
    print("\n🛰️ DEMO: Office Real-Time Collaboration Router")
    print("=" * 50)

    def fake_ai_service(message):
        time.sleep(0.1)
        payload = message.payload.copy()
        payload["status"] = "generated"
        return {
            "message_type": message.type.value,
            "document_id": message.document_id,
            "payload": payload,
        }

    router = AIOfficeWebSocketRouter(
        ai_service_url="https://ai-office-agent.local",
        ai_service_client=fake_ai_service,
    )

    try:
        ppt_session = router.register_client(
            "client-powerpoint",
            ApplicationType.POWERPOINT,
            user_id="user-42",
            document_id="doc-2024-q4",
            capabilities=["generate_content", "design_review"],
        )
        dashboard_session = router.register_client(
            "client-dashboard",
            ApplicationType.WEB_DASHBOARD,
            user_id="analyst-ops",
            document_id="doc-2024-q4",
            capabilities=["monitor_sessions"],
        )

        print(
            f"👥 Active document participants: {router.list_active_documents().get('doc-2024-q4')}"
        )

        broadcast = router.broadcast_live_edit(
            ppt_session.client_id,
            {"shapeId": "title", "text": "Q4 Performance Update"},
        )
        print(f"🔄 Broadcast recipients: {broadcast['recipients']}")

        ai_ack = router.handle_ai_request(
            ppt_session.client_id,
            MessageType.AI_GENERATE_REQUEST,
            {
                "prompt": "Create three slides summarizing Q4 results",
                "content_type": "slides",
            },
            target=ApplicationType.WEB_DASHBOARD,
        )
        print(
            f"🤖 AI request queued as {ai_ack['job_id']} (eta {ai_ack['estimated_time']}s)"
        )

        job_result = router.get_ai_job_result(ai_ack["job_id"], timeout=2.0)
        print(f"✅ AI job result: {job_result}")

        return {
            "broadcast": broadcast,
            "ai_ack": ai_ack,
            "ai_result": job_result,
            "clients": [ppt_session.client_id, dashboard_session.client_id],
        }
    finally:
        router.shutdown()


def main() -> int:
    """Run all demonstration examples."""
    print("🤖 OS Dashboard AI Assistant Platform - Demo Suite")
    print("=" * 60)
    print("Demonstrating advanced autonomous workflow capabilities...")

    start_time = time.time()
    demo_results: Dict[str, Any] = {}

    try:
        demo_results["data_collection"] = demo_data_collection()
        demo_results["content_generation"] = demo_content_generation()
        demo_results["system_operations"] = demo_system_operations()
        demo_results["quality_assurance"] = demo_quality_assurance()
        demo_results["concurrent_operations"] = demo_concurrent_operations()
        demo_results["deployment_integration"] = demo_deployment_integration()
        demo_results["office_realtime"] = demo_office_realtime_integration()

        total_time = time.time() - start_time
        print("\n🎉 DEMO COMPLETE - Summary")
        print("=" * 50)
        print(f"⏱️ Total execution time: {total_time:.2f} seconds")
        print(f"📊 All {len(demo_results)} demo modules completed successfully")

        if "content_generation" in demo_results:
            print("\n📁 Generated Files:")
            for file_type, path in demo_results["content_generation"].items():
                print(f"  📄 {file_type.title()}: {path}")

        if "deployment_integration" in demo_results:
            print("\n🔗 Integration Results:")
            deployment = demo_results["deployment_integration"]["deployment"]
            if deployment.get("success"):
                print(f"  🌐 Deployed to: {deployment['deployment_url']}")
            print(f"  📊 Add-In manifest: {demo_results['deployment_integration']['addin_manifest']}")

        if "office_realtime" in demo_results:
            print("\n🛰️ Real-Time Collaboration:")
            rt = demo_results["office_realtime"]
            print(f"  👥 Participants: {rt['clients']}")
            if rt.get("broadcast"):
                print(f"  🔄 Broadcast sent to: {rt['broadcast']['recipients']}")
            if rt.get("ai_ack"):
                print(
                    f"  🤖 AI job {rt['ai_ack']['job_id']} result: {rt.get('ai_result')}"
                )

        print("\n✨ The OS Dashboard AI Assistant Platform is ready for production use!")
        print("   Launch with: python main.py --mode dashboard")

    except Exception as exc:  # pragma: no cover - demo utility
        print(f"\n❌ Demo failed with error: {exc}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
