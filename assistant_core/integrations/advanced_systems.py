"""
Advanced Integration Systems
Office Add-In embedding, static site deployment, API integration, and cross-platform compatibility
"""

import os
import json
import requests
import zipfile
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import logging
import time
import subprocess
import yaml
import base64
from urllib.parse import urljoin, urlparse
import hashlib

@dataclass
class DeploymentConfig:
    """Configuration for deployment operations"""
    platform: str  # 'vercel', 'netlify', 'github-pages', 'aws-s3'
    project_name: str
    domain: Optional[str] = None
    environment_vars: Dict[str, str] = field(default_factory=dict)
    build_command: Optional[str] = None
    output_directory: str = "dist"
    api_key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HostConfig:
    """Host definition for Office add-in manifests."""

    name: str
    version: str = "1.1"
    runtimes: List[str] = field(default_factory=list)


@dataclass
class RequirementSet:
    """Requirement set entry for Office add-ins."""

    name: str
    version: str


@dataclass
class OfficeAddinConfig:
    """Configuration for Office Add-In integration"""
    manifest_id: str
    display_name: str
    description: str
    provider_name: str
    dashboard_url: str
    icon_url: Optional[str] = None
    support_url: Optional[str] = None
    permissions: List[str] = field(default_factory=lambda: ["ReadWriteDocument"])
    hosts: List[HostConfig] = field(default_factory=list)
    requirement_sets: List[RequirementSet] = field(default_factory=list)
    run_on_load: bool = False

    def __post_init__(self) -> None:
        if not self.hosts:
            self.hosts = [HostConfig(name="Workbook")]

class StaticSiteDeployer:
    """
    Advanced static site deployment with multiple platform support
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.deployment_history = []
    
    def deploy_to_vercel(self, source_directory: str, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Deploy static site to Vercel
        """
        try:
            # Prepare deployment package
            deployment_package = self._prepare_deployment_package(source_directory, config)
            
            # Simulate Vercel deployment (in real implementation, use Vercel API)
            deployment_url = f"https://{config.project_name}-{self._generate_hash()}.vercel.app"
            
            deployment_result = {
                "success": True,
                "platform": "vercel",
                "project_name": config.project_name,
                "deployment_url": deployment_url,
                "deployment_id": self._generate_deployment_id(),
                "deployed_at": time.time(),
                "build_time": 45.2,  # Simulated build time
                "file_count": len(list(Path(source_directory).rglob('*'))),
                "package_size": self._get_directory_size(source_directory)
            }
            
            # Store deployment history
            self.deployment_history.append(deployment_result)
            
            self.logger.info(f"Successfully deployed to Vercel: {deployment_url}")
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"Vercel deployment failed: {e}")
            return {
                "success": False,
                "platform": "vercel",
                "error": str(e)
            }
    
    def deploy_to_netlify(self, source_directory: str, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Deploy static site to Netlify
        """
        try:
            # Prepare deployment
            deployment_package = self._prepare_deployment_package(source_directory, config)
            
            # Simulate Netlify deployment
            deployment_url = f"https://{config.project_name}-{self._generate_hash()}.netlify.app"
            
            deployment_result = {
                "success": True,
                "platform": "netlify",
                "project_name": config.project_name,
                "deployment_url": deployment_url,
                "deployment_id": self._generate_deployment_id(),
                "deployed_at": time.time(),
                "build_time": 38.7,
                "file_count": len(list(Path(source_directory).rglob('*'))),
                "package_size": self._get_directory_size(source_directory),
                "features": ["https", "cdn", "forms", "functions"]
            }
            
            self.deployment_history.append(deployment_result)
            
            self.logger.info(f"Successfully deployed to Netlify: {deployment_url}")
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"Netlify deployment failed: {e}")
            return {
                "success": False,
                "platform": "netlify",
                "error": str(e)
            }
    
    def deploy_to_github_pages(self, source_directory: str, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Deploy static site to GitHub Pages
        """
        try:
            # Prepare deployment
            deployment_package = self._prepare_deployment_package(source_directory, config)
            
            # Simulate GitHub Pages deployment
            deployment_url = f"https://{config.metadata.get('github_username', 'user')}.github.io/{config.project_name}"
            
            deployment_result = {
                "success": True,
                "platform": "github-pages",
                "project_name": config.project_name,
                "deployment_url": deployment_url,
                "deployment_id": self._generate_deployment_id(),
                "deployed_at": time.time(),
                "build_time": 120.5,  # GitHub Pages typically slower
                "file_count": len(list(Path(source_directory).rglob('*'))),
                "package_size": self._get_directory_size(source_directory),
                "repository": f"{config.metadata.get('github_username', 'user')}/{config.project_name}"
            }
            
            self.deployment_history.append(deployment_result)
            
            self.logger.info(f"Successfully deployed to GitHub Pages: {deployment_url}")
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"GitHub Pages deployment failed: {e}")
            return {
                "success": False,
                "platform": "github-pages",
                "error": str(e)
            }
    
    def deploy_to_aws_s3(self, source_directory: str, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Deploy static site to AWS S3 with CloudFront
        """
        try:
            # Prepare deployment
            deployment_package = self._prepare_deployment_package(source_directory, config)
            
            # Simulate AWS S3 deployment
            bucket_name = f"{config.project_name}-{self._generate_hash()}"
            deployment_url = f"https://{bucket_name}.s3-website.amazonaws.com"
            
            if config.domain:
                deployment_url = f"https://{config.domain}"
            
            deployment_result = {
                "success": True,
                "platform": "aws-s3",
                "project_name": config.project_name,
                "deployment_url": deployment_url,
                "deployment_id": self._generate_deployment_id(),
                "deployed_at": time.time(),
                "build_time": 67.3,
                "file_count": len(list(Path(source_directory).rglob('*'))),
                "package_size": self._get_directory_size(source_directory),
                "bucket_name": bucket_name,
                "cloudfront_enabled": True,
                "custom_domain": config.domain
            }
            
            self.deployment_history.append(deployment_result)
            
            self.logger.info(f"Successfully deployed to AWS S3: {deployment_url}")
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"AWS S3 deployment failed: {e}")
            return {
                "success": False,
                "platform": "aws-s3",
                "error": str(e)
            }
    
    def deploy(self, source_directory: str, config: DeploymentConfig) -> Dict[str, Any]:
        """
        Deploy to specified platform
        """
        platform_deployers = {
            "vercel": self.deploy_to_vercel,
            "netlify": self.deploy_to_netlify,
            "github-pages": self.deploy_to_github_pages,
            "aws-s3": self.deploy_to_aws_s3
        }
        
        if config.platform not in platform_deployers:
            return {
                "success": False,
                "error": f"Unsupported platform: {config.platform}"
            }
        
        deployer = platform_deployers[config.platform]
        return deployer(source_directory, config)
    
    def _prepare_deployment_package(self, source_directory: str, config: DeploymentConfig) -> str:
        """Prepare deployment package"""
        source_path = Path(source_directory)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source directory not found: {source_directory}")
        
        # Create temporary deployment directory
        temp_dir = tempfile.mkdtemp(prefix="deployment_")
        
        try:
            # Copy source files
            shutil.copytree(source_directory, os.path.join(temp_dir, "source"))
            
            # Create deployment configuration
            deployment_config = {
                "name": config.project_name,
                "version": "1.0.0",
                "build": {
                    "command": config.build_command,
                    "output": config.output_directory
                },
                "environment": config.environment_vars,
                "created_at": time.time()
            }
            
            # Write deployment config
            with open(os.path.join(temp_dir, "deployment.json"), 'w') as f:
                json.dump(deployment_config, f, indent=2)
            
            return temp_dir
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
    
    def _generate_hash(self) -> str:
        """Generate deployment hash"""
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    
    def _generate_deployment_id(self) -> str:
        """Generate unique deployment ID"""
        return f"dep_{int(time.time())}_{self._generate_hash()}"
    
    def _get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def get_deployment_history(self) -> List[Dict[str, Any]]:
        """Get deployment history"""
        return self.deployment_history.copy()
    
    def rollback_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Rollback to previous deployment"""
        # Find deployment
        deployment = None
        for dep in self.deployment_history:
            if dep.get("deployment_id") == deployment_id:
                deployment = dep
                break
        
        if not deployment:
            return {
                "success": False,
                "error": f"Deployment {deployment_id} not found"
            }
        
        # Simulate rollback
        rollback_result = {
            "success": True,
            "action": "rollback",
            "original_deployment_id": deployment_id,
            "rollback_deployment_id": self._generate_deployment_id(),
            "platform": deployment["platform"],
            "deployment_url": deployment["deployment_url"],
            "rolled_back_at": time.time()
        }
        
        self.logger.info(f"Rolled back deployment: {deployment_id}")
        return rollback_result

class OfficeAddinEmbedder:
    """
    Office Add-In embedding system for Excel dashboards
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_office_addin_manifest(self, config: OfficeAddinConfig) -> str:
        """
        Create Office Add-In manifest XML
        """
        permissions_value = " ".join(config.permissions) if config.permissions else "ReadWriteDocument"
        hosts_xml = "\n".join(f"    <Host Name=\"{host.name}\" />" for host in config.hosts)
        if not hosts_xml:
            hosts_xml = "    <Host Name=\"Workbook\" />"

        requirements_xml = ""
        if config.requirement_sets:
            requirement_lines = "\n".join(
                f"      <Set Name=\"{req.name}\" MinVersion=\"{req.version}\" />"
                for req in config.requirement_sets
            )
            requirements_xml = f"""
  <Requirements>
    <Sets>
{requirement_lines}
    </Sets>
  </Requirements>
"""

        version_override_hosts = "\n".join(
            self._render_version_override_host(host, config)
            for host in config.hosts
        )
        if not version_override_hosts:
            version_override_hosts = self._render_version_override_host(HostConfig(name="Workbook"), config)

        manifest_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<OfficeApp xmlns="http://schemas.microsoft.com/office/appforoffice/1.1"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:bt="http://schemas.microsoft.com/office/officeappbasictypes/1.0"
           xmlns:ov="http://schemas.microsoft.com/office/taskpaneappversionoverrides"
           xsi:type="TaskPaneApp">

  <Id>{config.manifest_id}</Id>
  <Version>1.0.0.0</Version>
  <ProviderName>{config.provider_name}</ProviderName>
  <DefaultLocale>en-US</DefaultLocale>
  <DisplayName DefaultValue="{config.display_name}" />
  <Description DefaultValue="{config.description}" />
  <IconUrl DefaultValue="{config.icon_url or 'https://example.com/icon.png'}" />
  <HighResolutionIconUrl DefaultValue="{config.icon_url or 'https://example.com/icon-hi-res.png'}" />
  <SupportUrl DefaultValue="{config.support_url or 'https://example.com/support'}" />
  <AppDomains>
    <AppDomain>{urlparse(config.dashboard_url).netloc}</AppDomain>
  </AppDomains>
{requirements_xml}  <Hosts>
{hosts_xml}
  </Hosts>
  <DefaultSettings>
    <SourceLocation DefaultValue="{config.dashboard_url}" />
  </DefaultSettings>
  <Permissions>{permissions_value}</Permissions>

  <VersionOverrides xmlns="http://schemas.microsoft.com/office/taskpaneappversionoverrides" xsi:type="VersionOverridesV1_0">
    <Hosts>
{version_override_hosts}
    </Hosts>
    <Resources>
      <bt:Images>
        <bt:Image id="Icon.16x16" DefaultValue="{config.icon_url or 'https://example.com/icon-16.png'}" />
        <bt:Image id="Icon.32x32" DefaultValue="{config.icon_url or 'https://example.com/icon-32.png'}" />
        <bt:Image id="Icon.80x80" DefaultValue="{config.icon_url or 'https://example.com/icon-80.png'}" />
      </bt:Images>
      <bt:Urls>
        <bt:Url id="Commands.Url" DefaultValue="{config.dashboard_url}/commands.html" />
        <bt:Url id="Taskpane.Url" DefaultValue="{config.dashboard_url}" />
      </bt:Urls>
      <bt:ShortStrings>
        <bt:String id="GroupLabel" DefaultValue="{config.display_name}" />
        <bt:String id="TaskpaneButton.Label" DefaultValue="Open Dashboard" />
      </bt:ShortStrings>
      <bt:LongStrings>
        <bt:String id="TaskpaneButton.Tooltip" DefaultValue="Open the interactive dashboard in a task pane." />
      </bt:LongStrings>
    </Resources>
  </VersionOverrides>

</OfficeApp>"""

        return manifest_xml

    def _render_version_override_host(self, host: HostConfig, config: OfficeAddinConfig) -> str:
        host_type = host.name if host.name in {"Workbook", "Document", "Presentation"} else "Workbook"
        run_on_load_xml = "          <RunOnLoad>true</RunOnLoad>\n" if config.run_on_load else ""
        return f"""
      <Host xsi:type="{host_type}">
        <DesktopFormFactor>
          <FunctionFile resid="Commands.Url" />
          <ExtensionPoint xsi:type="PrimaryCommandSurface">
            <OfficeTab id="TabHome">
              <Group id="Contoso.Group1">
                <Label resid="GroupLabel" />
                <Icon>
                  <bt:Image size="16" resid="Icon.16x16" />
                  <bt:Image size="32" resid="Icon.32x32" />
                  <bt:Image size="80" resid="Icon.80x80" />
                </Icon>
                <Control xsi:type="Button" id="Contoso.TaskpaneButton">
                  <Label resid="TaskpaneButton.Label" />
                  <Supertip>
                    <Title resid="TaskpaneButton.Label" />
                    <Description resid="TaskpaneButton.Tooltip" />
                  </Supertip>
                  <Icon>
                    <bt:Image size="16" resid="Icon.16x16" />
                    <bt:Image size="32" resid="Icon.32x32" />
                    <bt:Image size="80" resid="Icon.80x80" />
                  </Icon>
                  <Action xsi:type="ShowTaskpane">
                    <SourceLocation resid="Taskpane.Url" />
                  </Action>
                </Control>
              </Group>
            </OfficeTab>
          </ExtensionPoint>
{run_on_load_xml}        </DesktopFormFactor>
      </Host>
"""
    
    def embed_dashboard_in_excel(self, excel_file_path: str, config: OfficeAddinConfig,
                                output_path: str = None) -> Dict[str, Any]:
        """
        Embed dashboard as Office Add-In in Excel file
        """
        try:
            # Create manifest
            manifest_xml = self.create_office_addin_manifest(config)
            
            # Create output path if not provided
            if not output_path:
                base_name = Path(excel_file_path).stem
                output_path = f"{base_name}_with_dashboard.xlsx"
            
            # Copy original Excel file
            shutil.copy2(excel_file_path, output_path)
            
            # Create add-in package
            addin_package = self._create_addin_package(manifest_xml, config)
            
            # Embed add-in reference in Excel file (simplified simulation)
            # In real implementation, this would modify the Excel file structure
            
            result = {
                "success": True,
                "excel_file": output_path,
                "dashboard_url": config.dashboard_url,
                "manifest_id": config.manifest_id,
                "addin_package": addin_package,
                "embedded_at": time.time(),
                "instructions": [
                    "1. Open the Excel file",
                    "2. Go to Insert > Office Add-ins",
                    "3. Upload the manifest file",
                    "4. The dashboard will appear in the task pane"
                ]
            }
            
            self.logger.info(f"Dashboard embedded in Excel: {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to embed dashboard in Excel: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_addin_package(self, manifest_xml: str, config: OfficeAddinConfig) -> str:
        """Create Office Add-In package"""
        # Create temporary directory for add-in package
        temp_dir = tempfile.mkdtemp(prefix="office_addin_")
        
        try:
            # Write manifest file
            manifest_path = os.path.join(temp_dir, "manifest.xml")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(manifest_xml)
            
            # Create commands.html for function file
            commands_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=Edge" />
    <script src="https://appsforoffice.microsoft.com/lib/1/hosted/office.js"></script>
</head>
<body>
    <script>
        Office.onReady(() => {
            // Add-in is ready
        });
        
        function openDashboard() {
            // Function to open dashboard
            Office.ribbon.requestUpdate({
                tabs: [{
                    id: "TabHome",
                    groups: [{
                        id: "Contoso.Group1",
                        controls: [{
                            id: "Contoso.TaskpaneButton",
                            enabled: true
                        }]
                    }]
                }]
            });
        }
    </script>
</body>
</html>
            """
            
            commands_path = os.path.join(temp_dir, "commands.html")
            with open(commands_path, 'w', encoding='utf-8') as f:
                f.write(commands_html)
            
            # Create package info
            package_info = {
                "name": config.display_name,
                "version": "1.0.0",
                "manifest": "manifest.xml",
                "commands": "commands.html",
                "dashboard_url": config.dashboard_url,
                "created_at": time.time()
            }
            
            package_info_path = os.path.join(temp_dir, "package.json")
            with open(package_info_path, 'w') as f:
                json.dump(package_info, f, indent=2)
            
            return temp_dir
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise

class APIIntegrationManager:
    """
    Advanced API integration manager for live data feeds
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_connections = {}
        self.data_cache = {}
    
    def register_api_connection(self, name: str, base_url: str, 
                              auth_config: Dict[str, Any] = None,
                              rate_limit: float = 1.0) -> str:
        """
        Register an API connection
        """
        connection_id = f"api_{name}_{int(time.time())}"
        
        self.api_connections[connection_id] = {
            "name": name,
            "base_url": base_url,
            "auth_config": auth_config or {},
            "rate_limit": rate_limit,
            "last_request": 0,
            "request_count": 0,
            "error_count": 0,
            "created_at": time.time()
        }
        
        self.logger.info(f"API connection registered: {name}")
        return connection_id
    
    def create_live_data_feed(self, connection_id: str, endpoint: str,
                            refresh_interval: int = 300,
                            data_transformer: Callable = None) -> str:
        """
        Create a live data feed from API endpoint
        """
        if connection_id not in self.api_connections:
            raise ValueError(f"API connection {connection_id} not found")
        
        feed_id = f"feed_{int(time.time())}"
        
        # Create data feed configuration
        feed_config = {
            "connection_id": connection_id,
            "endpoint": endpoint,
            "refresh_interval": refresh_interval,
            "data_transformer": data_transformer,
            "last_update": 0,
            "update_count": 0,
            "status": "active",
            "created_at": time.time()
        }
        
        # Start background data fetching (simplified)
        self._start_data_feed(feed_id, feed_config)
        
        self.logger.info(f"Live data feed created: {feed_id}")
        return feed_id
    
    def _start_data_feed(self, feed_id: str, config: Dict[str, Any]):
        """Start background data fetching for feed"""
        # In real implementation, this would use a proper scheduler
        # For now, we'll simulate the data feed setup
        
        connection = self.api_connections[config["connection_id"]]
        
        # Simulate initial data fetch
        mock_data = {
            "timestamp": time.time(),
            "data": [
                {"id": 1, "value": 100, "status": "active"},
                {"id": 2, "value": 250, "status": "active"},
                {"id": 3, "value": 175, "status": "inactive"}
            ],
            "metadata": {
                "source": connection["name"],
                "endpoint": config["endpoint"],
                "refresh_interval": config["refresh_interval"]
            }
        }
        
        # Apply data transformer if provided
        if config["data_transformer"]:
            mock_data = config["data_transformer"](mock_data)
        
        # Cache the data
        self.data_cache[feed_id] = mock_data
        
        self.logger.info(f"Data feed started: {feed_id}")
    
    def get_live_data(self, feed_id: str) -> Dict[str, Any]:
        """Get current data from live feed"""
        if feed_id not in self.data_cache:
            return {"error": f"Data feed {feed_id} not found"}
        
        return self.data_cache[feed_id]
    
    def create_webhook_endpoint(self, name: str, callback_function: Callable,
                              authentication: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create webhook endpoint for receiving data
        """
        webhook_id = f"webhook_{int(time.time())}"
        webhook_url = f"https://api.example.com/webhooks/{webhook_id}"
        
        webhook_config = {
            "id": webhook_id,
            "name": name,
            "url": webhook_url,
            "callback_function": callback_function,
            "authentication": authentication or {},
            "created_at": time.time(),
            "request_count": 0,
            "last_request": None
        }
        
        # Register webhook (simplified)
        self.api_connections[webhook_id] = webhook_config
        
        self.logger.info(f"Webhook endpoint created: {webhook_url}")
        
        return {
            "webhook_id": webhook_id,
            "webhook_url": webhook_url,
            "status": "active",
            "authentication_required": bool(authentication)
        }

class CrossPlatformCompatibilityManager:
    """
    Ensure cross-platform compatibility and universal access
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compatibility_checks = []
    
    def validate_cross_platform_compatibility(self, file_path: str,
                                            target_platforms: List[str] = None) -> Dict[str, Any]:
        """
        Validate cross-platform compatibility
        """
        if target_platforms is None:
            target_platforms = ["windows", "macos", "linux", "web", "mobile"]
        
        compatibility_results = {}
        
        for platform in target_platforms:
            compatibility_results[platform] = self._check_platform_compatibility(file_path, platform)
        
        # Overall compatibility score
        total_score = sum(result["score"] for result in compatibility_results.values())
        average_score = total_score / len(compatibility_results)
        
        return {
            "file_path": file_path,
            "overall_score": average_score,
            "platform_results": compatibility_results,
            "recommendations": self._generate_compatibility_recommendations(compatibility_results),
            "checked_at": time.time()
        }
    
    def _check_platform_compatibility(self, file_path: str, platform: str) -> Dict[str, Any]:
        """Check compatibility for specific platform"""
        file_extension = Path(file_path).suffix.lower()
        
        # Platform-specific compatibility rules
        compatibility_rules = {
            "windows": {
                ".xlsx": {"score": 100, "native": True},
                ".docx": {"score": 100, "native": True},
                ".html": {"score": 95, "native": False, "requires": "web_browser"},
                ".pdf": {"score": 90, "native": False, "requires": "pdf_reader"}
            },
            "macos": {
                ".xlsx": {"score": 95, "native": False, "requires": "office_suite"},
                ".docx": {"score": 95, "native": False, "requires": "office_suite"},
                ".html": {"score": 100, "native": True},
                ".pdf": {"score": 100, "native": True}
            },
            "linux": {
                ".xlsx": {"score": 80, "native": False, "requires": "libreoffice"},
                ".docx": {"score": 80, "native": False, "requires": "libreoffice"},
                ".html": {"score": 100, "native": True},
                ".pdf": {"score": 95, "native": False, "requires": "pdf_viewer"}
            },
            "web": {
                ".xlsx": {"score": 70, "native": False, "requires": "office_online"},
                ".docx": {"score": 70, "native": False, "requires": "office_online"},
                ".html": {"score": 100, "native": True},
                ".pdf": {"score": 85, "native": False, "requires": "pdf_js"}
            },
            "mobile": {
                ".xlsx": {"score": 60, "native": False, "requires": "mobile_office_app"},
                ".docx": {"score": 60, "native": False, "requires": "mobile_office_app"},
                ".html": {"score": 90, "native": True, "notes": "responsive_design_recommended"},
                ".pdf": {"score": 80, "native": False, "requires": "pdf_viewer_app"}
            }
        }
        
        platform_rules = compatibility_rules.get(platform, {})
        file_rule = platform_rules.get(file_extension, {"score": 50, "native": False})
        
        return {
            "platform": platform,
            "file_type": file_extension,
            "score": file_rule["score"],
            "native_support": file_rule.get("native", False),
            "requirements": file_rule.get("requires"),
            "notes": file_rule.get("notes"),
            "status": "excellent" if file_rule["score"] >= 90 else 
                     "good" if file_rule["score"] >= 70 else
                     "fair" if file_rule["score"] >= 50 else "poor"
        }
    
    def _generate_compatibility_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate compatibility improvement recommendations"""
        recommendations = []
        
        # Check for low scores
        low_score_platforms = [
            platform for platform, result in results.items() 
            if result["score"] < 70
        ]
        
        if low_score_platforms:
            recommendations.append(
                f"Consider providing alternative formats for better compatibility with: {', '.join(low_score_platforms)}"
            )
        
        # Check for mobile compatibility
        mobile_result = results.get("mobile", {})
        if mobile_result.get("score", 0) < 80:
            recommendations.append("Optimize for mobile devices with responsive design")
        
        # Check for web compatibility
        web_result = results.get("web", {})
        if web_result.get("score", 0) < 90:
            recommendations.append("Consider HTML format for better web compatibility")
        
        # Check for requirements
        required_software = set()
        for result in results.values():
            if result.get("requirements"):
                required_software.add(result["requirements"])
        
        if required_software:
            recommendations.append(
                f"Users may need to install: {', '.join(required_software)}"
            )
        
        return recommendations
    
    def create_universal_package(self, source_files: List[str], 
                               package_name: str) -> Dict[str, Any]:
        """
        Create universal package with multiple format support
        """
        package_dir = tempfile.mkdtemp(prefix=f"{package_name}_")
        
        try:
            # Create package structure
            formats_dir = os.path.join(package_dir, "formats")
            os.makedirs(formats_dir, exist_ok=True)
            
            # Copy source files
            for file_path in source_files:
                file_name = Path(file_path).name
                dest_path = os.path.join(formats_dir, file_name)
                shutil.copy2(file_path, dest_path)
            
            # Create package manifest
            manifest = {
                "package_name": package_name,
                "version": "1.0.0",
                "created_at": time.time(),
                "files": [],
                "compatibility": {}
            }
            
            # Analyze each file
            for file_path in source_files:
                file_name = Path(file_path).name
                compatibility = self.validate_cross_platform_compatibility(file_path)
                
                manifest["files"].append({
                    "name": file_name,
                    "path": f"formats/{file_name}",
                    "compatibility_score": compatibility["overall_score"],
                    "platform_support": compatibility["platform_results"]
                })
            
            # Create README
            readme_content = self._generate_package_readme(manifest)
            readme_path = os.path.join(package_dir, "README.md")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Write manifest
            manifest_path = os.path.join(package_dir, "manifest.json")
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Create ZIP package
            zip_path = f"{package_name}_universal.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(package_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, package_dir)
                        zipf.write(file_path, arcname)
            
            return {
                "success": True,
                "package_name": package_name,
                "package_path": zip_path,
                "package_size": os.path.getsize(zip_path),
                "file_count": len(source_files),
                "manifest": manifest
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
        finally:
            shutil.rmtree(package_dir, ignore_errors=True)
    
    def _generate_package_readme(self, manifest: Dict[str, Any]) -> str:
        """Generate README for universal package"""
        readme_lines = [
            f"# {manifest['package_name']}",
            "",
            f"Universal package created on {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(manifest['created_at']))}",
            "",
            "## Contents",
            ""
        ]
        
        for file_info in manifest["files"]:
            readme_lines.append(f"- **{file_info['name']}** (Compatibility: {file_info['compatibility_score']:.1f}/100)")
            
            # Add platform support details
            for platform, support in file_info["platform_support"].items():
                status_emoji = "✅" if support["score"] >= 90 else "⚠️" if support["score"] >= 70 else "❌"
                readme_lines.append(f"  - {platform.title()}: {status_emoji} {support['score']}/100")
            
            readme_lines.append("")
        
        readme_lines.extend([
            "## Usage Instructions",
            "",
            "1. Extract the package to your desired location",
            "2. Choose the appropriate format for your platform:",
            "   - Windows: Use .xlsx or .docx files",
            "   - macOS/Linux: Use .html files or install LibreOffice for Office formats",
            "   - Web browsers: Use .html files",
            "   - Mobile devices: Use .html files for best experience",
            "",
            "## Requirements",
            "",
            "Some formats may require additional software:",
            "- Office documents: Microsoft Office, LibreOffice, or Office Online",
            "- PDF files: PDF viewer (built into most systems)",
            "- HTML files: Web browser (available on all platforms)",
            "",
            "For questions or support, please refer to the documentation."
        ])
        
        return "\n".join(readme_lines)

# Example usage
if __name__ == "__main__":
    # Example static site deployment
    deployer = StaticSiteDeployer()
    
    config = DeploymentConfig(
        platform="vercel",
        project_name="my-dashboard",
        environment_vars={"NODE_ENV": "production"}
    )
    
    # Simulate deployment
    result = deployer.deploy("./dist", config)
    print(f"Deployment result: {result}")
    
    # Example Office Add-In embedding
    addin_embedder = OfficeAddinEmbedder()
    
    addin_config = OfficeAddinConfig(
        manifest_id="12345678-1234-1234-1234-123456789012",
        display_name="Interactive Dashboard",
        description="Real-time data dashboard for Excel",
        provider_name="AI Assistant",
        dashboard_url="https://my-dashboard.vercel.app"
    )
    
    # Create manifest
    manifest = addin_embedder.create_office_addin_manifest(addin_config)
    print("Office Add-In manifest created successfully")
