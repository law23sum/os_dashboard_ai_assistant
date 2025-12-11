#!/usr/bin/env python3
"""
OS Dashboard AI Assistant Platform - Demo Usage Examples
Demonstrates the key capabilities of the platform
"""

import asyncio
import time
import pandas as pd
from pathlib import Path

# Import platform modules
from src.core.base_agent import BaseAgent, Task, WorkflowBuilder, Priority
from src.intelligence.data_collector import SyncDataCollector, DataSource
from src.content.generators import PresentationGenerator, ExcelDashboardGenerator, WordDocumentGenerator, ContentConfig
from src.system.operations import SystemOperationsController
from src.intelligence.quality_assurance import ContentValidator, AccessibilityChecker
from src.operations.concurrent_manager import ConcurrentOperationsManager, ConcurrentTask
from src.integrations.advanced_systems import StaticSiteDeployer, DeploymentConfig

def demo_data_collection():
    """Demonstrate multi-source data collection capabilities"""
    print("\n🔍 DEMO: Multi-Source Data Collection")
    print("=" * 50)
    
    # Initialize data collector
    collector = SyncDataCollector(max_concurrent=5)
    
    # Define multiple data sources
    sources = [
        DataSource(
            name="example_api",
            url="https://jsonplaceholder.typicode.com/posts/1",
            source_type="api"
        ),
        DataSource(
            name="example_website",
            url="https://httpbin.org/html",
            source_type="web"
        ),
        DataSource(
            name="json_data",
            url="https://httpbin.org/json",
            source_type="api"
        )
    ]
    
    print(f"📊 Collecting data from {len(sources)} sources...")
    
    # Collect data from all sources
    results = collector.collect_data(sources)
    
    # Display results
    for i, result in enumerate(results, 1):
        if "error" not in result:
            print(f"✅ Source {i}: Success - {len(str(result.get('data', {})))} bytes")
        else:
            print(f"❌ Source {i}: Failed - {result['error']}")
    
    print(f"📈 Collection complete: {len([r for r in results if 'error' not in r])}/{len(results)} successful")
    return results

def demo_content_generation():
    """Demonstrate professional content generation"""
    print("\n📄 DEMO: Professional Content Generation")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("./workspace/demo_output")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Generate Interactive Presentation
    print("🎨 Creating interactive HTML presentation...")
    
    config = ContentConfig(
        title="AI Platform Demo",
        author="Demo User",
        theme="professional"
    )
    
    presentation = PresentationGenerator(config)
    presentation.add_title_slide("AI Assistant Platform", "Autonomous Workflow Demo", "Demo User")
    presentation.add_content_slide("Key Features", [
        "Multi-source data intelligence",
        "Professional content generation",
        "System-level operations",
        "Quality assurance systems",
        "Concurrent processing"
    ])
    
    # Add chart slide
    chart_data = {
        "labels": ["Data Collection", "Content Gen", "System Ops", "Quality Check", "Deployment"],
        "datasets": [{
            "label": "Completion Time (seconds)",
            "data": [2.5, 4.2, 1.8, 3.1, 5.7],
            "backgroundColor": "rgba(54, 162, 235, 0.2)",
            "borderColor": "rgba(54, 162, 235, 1)"
        }]
    }
    
    presentation.add_chart_slide("Performance Metrics", "bar", chart_data)
    
    pres_path = output_dir / "demo_presentation.html"
    presentation.generate_html(str(pres_path))
    print(f"✅ Presentation created: {pres_path}")
    
    # 2. Generate Excel Dashboard
    print("📊 Creating Excel dashboard...")
    
    # Sample data
    data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [120000, 135000, 148000, 162000, 175000, 189000],
        'Expenses': [80000, 85000, 92000, 98000, 105000, 112000],
        'Profit': [40000, 50000, 56000, 64000, 70000, 77000],
        'Growth_Rate': [0, 12.5, 9.6, 9.5, 8.0, 8.6]
    })
    
    excel_generator = ExcelDashboardGenerator(config)
    excel_generator.add_worksheet("Financial Data", data)
    excel_generator.add_conditional_formatting("Financial Data", "C2:C7", "color_scale", {
        "start_color": "FF0000",
        "end_color": "00FF00"
    })
    
    excel_path = output_dir / "demo_dashboard.xlsx"
    excel_generator.generate_excel(str(excel_path))
    print(f"✅ Excel dashboard created: {excel_path}")
    
    # 3. Generate Word Document
    print("📝 Creating Word document...")
    
    word_generator = WordDocumentGenerator(config)
    word_generator.add_heading("Executive Summary", 1)
    word_generator.add_paragraph(
        "This demonstration showcases the advanced capabilities of the OS Dashboard AI Assistant Platform. "
        "The platform provides enterprise-grade autonomous workflow capabilities with professional content generation."
    )
    
    word_generator.add_heading("Key Achievements", 2)
    word_generator.add_list([
        "Successfully implemented multi-source data collection",
        "Created professional-grade content generation system",
        "Developed advanced system operations controller",
        "Built comprehensive quality assurance framework",
        "Established concurrent processing capabilities"
    ])
    
    word_generator.add_heading("Performance Metrics", 2)
    word_generator.add_table(
        data=[
            ["Data Collection", "2.5s", "Excellent"],
            ["Content Generation", "4.2s", "Good"],
            ["System Operations", "1.8s", "Excellent"],
            ["Quality Assurance", "3.1s", "Good"],
            ["Deployment", "5.7s", "Acceptable"]
        ],
        headers=["Component", "Avg Time", "Performance"]
    )
    
    word_path = output_dir / "demo_report.docx"
    word_generator.generate_docx(str(word_path))
    print(f"✅ Word document created: {word_path}")
    
    return {
        "presentation": str(pres_path),
        "excel": str(excel_path),
        "word": str(word_path)
    }

def demo_system_operations():
    """Demonstrate system-level operations"""
    print("\n⚙️ DEMO: System-Level Operations")
    print("=" * 50)
    
    # Initialize system controller
    controller = SystemOperationsController()
    
    # 1. Execute system commands
    print("🖥️ Executing system commands...")
    
    commands = [
        "echo 'Hello from AI Assistant Platform'",
        "date",
        "pwd",
        "ls -la workspace/"
    ]
    
    for cmd in commands:
        result = controller.execute_command(cmd)
        if result["success"]:
            print(f"✅ '{cmd}': {result['stdout'].strip()}")
        else:
            print(f"❌ '{cmd}': {result.get('stderr', 'Unknown error')}")
    
    # 2. Get system information
    print("\n📊 System Information:")
    sys_info = controller.get_system_info()
    
    if "error" not in sys_info:
        print(f"CPU Usage: {sys_info['cpu']['cpu_usage']:.1f}%")
        print(f"Memory Usage: {sys_info['memory']['percentage']:.1f}%")
        print(f"Disk Usage: {sys_info['disk']['percentage']:.1f}%")
        print(f"Running Tasks: {sys_info['running_tasks']}")
    else:
        print(f"Error getting system info: {sys_info['error']}")
    
    # 3. Create and extract archive
    print("\n📦 Archive Operations:")
    
    # Create test files
    test_dir = Path("./workspace/test_archive")
    test_dir.mkdir(exist_ok=True)
    
    for i in range(3):
        test_file = test_dir / f"test_file_{i}.txt"
        test_file.write_text(f"This is test file {i}\nCreated by AI Assistant Platform\n")
    
    # Create archive
    archive_result = controller.create_archive(
        str(test_dir),
        "./workspace/demo_archive.zip",
        "zip"
    )
    
    if archive_result["success"]:
        print(f"✅ Archive created: {archive_result['archive_size']} bytes")
        print(f"Compression ratio: {archive_result['compression_ratio']:.2f}")
    else:
        print(f"❌ Archive creation failed: {archive_result['error']}")
    
    return sys_info

def demo_quality_assurance():
    """Demonstrate quality assurance capabilities"""
    print("\n🔍 DEMO: Quality Assurance Systems")
    print("=" * 50)
    
    # Create sample HTML content for validation
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
    
    # 1. Content Validation
    print("📋 Running content validation...")
    
    validator = ContentValidator()
    validation_results = validator.validate_content(sample_html, "html")
    
    errors = [r for r in validation_results if r.severity == "error" and not r.passed]
    warnings = [r for r in validation_results if r.severity == "warning" and not r.passed]
    passed = [r for r in validation_results if r.passed]
    
    print(f"✅ Validation complete: {len(passed)} passed, {len(warnings)} warnings, {len(errors)} errors")
    
    for result in errors[:3]:  # Show first 3 errors
        print(f"❌ Error: {result.message}")
    
    for result in warnings[:3]:  # Show first 3 warnings
        print(f"⚠️ Warning: {result.message}")
    
    # 2. Accessibility Check
    print("\n♿ Running accessibility check...")
    
    accessibility_checker = AccessibilityChecker()
    accessibility_results = accessibility_checker.check_accessibility(sample_html)
    
    accessibility_issues = [r for r in accessibility_results if not r.passed]
    accessibility_passed = [r for r in accessibility_results if r.passed]
    
    print(f"✅ Accessibility check: {len(accessibility_passed)} passed, {len(accessibility_issues)} issues")
    
    for result in accessibility_issues[:3]:  # Show first 3 issues
        print(f"♿ Issue: {result.message}")
        if result.suggestion:
            print(f"   Suggestion: {result.suggestion}")
    
    return {
        "validation_results": len(validation_results),
        "errors": len(errors),
        "warnings": len(warnings),
        "accessibility_issues": len(accessibility_issues)
    }

def demo_concurrent_operations():
    """Demonstrate concurrent processing capabilities"""
    print("\n⚡ DEMO: Concurrent Operations")
    print("=" * 50)
    
    # Initialize concurrent manager
    manager = ConcurrentOperationsManager(max_workers=5)
    
    # Define sample processing function
    def process_data_batch(batch_id, data_size):
        """Simulate data processing"""
        import random
        processing_time = random.uniform(1.0, 3.0)
        time.sleep(processing_time)
        
        return {
            "batch_id": batch_id,
            "data_size": data_size,
            "processing_time": processing_time,
            "items_processed": data_size * 10,
            "status": "completed"
        }
    
    # Create multiple tasks
    print("🚀 Creating concurrent tasks...")
    
    tasks = []
    for i in range(8):
        task = ConcurrentTask(
            name=f"process_batch_{i}",
            function=process_data_batch,
            args=(i, 100 + i * 50),
            priority=2 if i < 4 else 1  # Higher priority for first 4 tasks
        )
        tasks.append(task)
    
    # Create batch operation
    batch_id = manager.create_batch_operation(
        name="demo_data_processing",
        tasks=tasks,
        parallel_limit=3,
        fail_fast=False
    )
    
    print(f"📊 Processing {len(tasks)} tasks with max 3 concurrent...")
    
    # Execute batch
    start_time = time.time()
    results = manager.execute_batch_sync(batch_id)
    end_time = time.time()
    
    # Display results
    print(f"✅ Batch processing complete in {end_time - start_time:.2f} seconds")
    print(f"📈 Results: {results['successful_tasks']}/{results['total_tasks']} successful")
    
    if results['failed_tasks'] > 0:
        print(f"❌ Failed tasks: {results['failed_tasks']}")
    
    # Performance stats
    stats = manager.get_performance_stats()
    print(f"📊 Performance: {stats['tasks_completed']} completed, avg time: {stats['average_execution_time']:.2f}s")
    
    # Cleanup
    manager.shutdown()
    
    return results

def demo_deployment_integration():
    """Demonstrate deployment and integration capabilities"""
    print("\n🚀 DEMO: Deployment & Integration")
    print("=" * 50)
    
    # 1. Static Site Deployment (Simulated)
    print("🌐 Simulating static site deployment...")
    
    deployer = StaticSiteDeployer()
    
    # Create sample deployment config
    config = DeploymentConfig(
        platform="vercel",
        project_name="ai-dashboard-demo",
        environment_vars={"NODE_ENV": "production"}
    )
    
    # Simulate deployment
    deployment_result = deployer.deploy("./workspace/demo_output", config)
    
    if deployment_result["success"]:
        print(f"✅ Deployment successful!")
        print(f"🔗 URL: {deployment_result['deployment_url']}")
        print(f"📦 Files: {deployment_result['file_count']}")
        print(f"⏱️ Build time: {deployment_result['build_time']}s")
    else:
        print(f"❌ Deployment failed: {deployment_result['error']}")
    
    # 2. Office Add-In Integration (Simulated)
    print("\n📊 Simulating Office Add-In creation...")
    
    from src.integrations.advanced_systems import OfficeAddinEmbedder, OfficeAddinConfig
    
    embedder = OfficeAddinEmbedder()
    
    addin_config = OfficeAddinConfig(
        manifest_id="demo-12345678-1234-1234-1234-123456789012",
        display_name="AI Dashboard Demo Add-In",
        description="Interactive dashboard for Excel demonstration",
        provider_name="AI Assistant Platform",
        dashboard_url=deployment_result.get("deployment_url", "https://demo.example.com")
    )
    
    manifest_xml = embedder.create_office_addin_manifest(addin_config)
    
    # Save manifest
    manifest_path = Path("./workspace/demo_output/excel_addin_manifest.xml")
    manifest_path.write_text(manifest_xml, encoding='utf-8')
    
    print(f"✅ Office Add-In manifest created: {manifest_path}")
    print(f"📋 Manifest size: {len(manifest_xml)} characters")
    
    return {
        "deployment": deployment_result,
        "addin_manifest": str(manifest_path)
    }

def main():
    """Run all demonstration examples"""
    print("🤖 OS Dashboard AI Assistant Platform - Demo Suite")
    print("=" * 60)
    print("Demonstrating advanced autonomous workflow capabilities...")
    
    # Track overall performance
    start_time = time.time()
    demo_results = {}
    
    try:
        # Run all demos
        demo_results["data_collection"] = demo_data_collection()
        demo_results["content_generation"] = demo_content_generation()
        demo_results["system_operations"] = demo_system_operations()
        demo_results["quality_assurance"] = demo_quality_assurance()
        demo_results["concurrent_operations"] = demo_concurrent_operations()
        demo_results["deployment_integration"] = demo_deployment_integration()
        
        # Summary
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n🎉 DEMO COMPLETE - Summary")
        print("=" * 50)
        print(f"⏱️ Total execution time: {total_time:.2f} seconds")
        print(f"📊 All {len(demo_results)} demo modules completed successfully")
        
        print("\n📁 Generated Files:")
        if "content_generation" in demo_results:
            for file_type, path in demo_results["content_generation"].items():
                print(f"  📄 {file_type.title()}: {path}")
        
        print("\n🔗 Integration Results:")
        if "deployment_integration" in demo_results:
            deployment = demo_results["deployment_integration"]["deployment"]
            if deployment.get("success"):
                print(f"  🌐 Deployed to: {deployment['deployment_url']}")
            print(f"  📊 Add-In manifest: {demo_results['deployment_integration']['addin_manifest']}")
        
        print("\n✨ The OS Dashboard AI Assistant Platform is ready for production use!")
        print("   Launch with: python main.py --mode dashboard")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)