"""
Documentation and Developer Portal System

Comprehensive developer portal with interactive documentation, code examples, and support
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import markdown
import jinja2
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from config.logging_config import setup_logger


class DocumentationType(Enum):
    API_REFERENCE = "api_reference"
    TUTORIAL = "tutorial"
    GUIDE = "guide"
    FAQ = "faq"
    CHANGELOG = "changelog"
    SDK_DOCS = "sdk_docs"


class ContentStatus(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SupportTicketType(Enum):
    TECHNICAL = "technical"
    SUPPORT = "support"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL = "general"


@dataclass
class DocumentationPage:
    """Documentation page structure"""
    id: str
    title: str
    slug: str
    content: str
    type: DocumentationType
    status: ContentStatus
    author: str
    tags: List[str]
    parent_id: Optional[str]
    order: int
    created_at: datetime
    updated_at: datetime
    version: str = "1.0"
    metadata: Dict[str, Any] = None


@dataclass
class CodeExample:
    """Code example with multiple language support"""
    id: str
    title: str
    description: str
    languages: Dict[str, str]  # language -> code
    tags: List[str]
    category: str
    difficulty: str  # beginner, intermediate, advanced
    created_at: datetime


@dataclass
class APIEndpoint:
    """API endpoint documentation"""
    id: str
    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    examples: List[Dict[str, Any]]
    tags: List[str]
    deprecated: bool = False


@dataclass
class DeveloperTicket:
    """Developer support ticket"""
    id: str
    developer_id: str
    type: SupportTicketType
    title: str
    description: str
    priority: str
    status: str
    assigned_to: str
    created_at: datetime
    updated_at: datetime
    resolution: str = ""


class DeveloperPortalSystem:
    """Comprehensive developer portal and documentation system"""

    def __init__(self):
        self.logger = setup_logger("DeveloperPortal")

        # Content storage
        self.documentation_pages: Dict[str, DocumentationPage] = {}
        self.code_examples: Dict[str, CodeExample] = {}
        self.api_endpoints: Dict[str, APIEndpoint] = {}
        self.developer_tickets: Dict[str, DeveloperTicket] = {}

        # Template engine
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        # Configuration
        self.config = {
            "portal_url": "https://developers.dashboard-ai.com",
            "api_base_url": "https://api.dashboard-ai.com/v1",
            "support_email": "support@dashboard-ai.com",
            "search_enabled": True,
            "analytics_enabled": True,
            "feedback_enabled": True,
            "auto_generate_sdk": True
        }

        # Analytics
        self.page_views: Dict[str, int] = {}
        self.search_queries: List[Dict[str, Any]] = []
        self.feedback_data: List[Dict[str, Any]] = []

    async def initialize(self):
        """Initialize developer portal system"""
        await self._load_documentation()
        await self._load_api_endpoints()
        await self._load_code_examples()
        await self._setup_templates()

        # Start background tasks
        asyncio.create_task(self._update_search_index())
        asyncio.create_task(self._generate_analytics_reports())

        self.logger.info("Developer Portal System initialized")

    # Documentation Management

    async def create_documentation_page(self, page_data: Dict[str, Any]) -> str:
        """Create new documentation page"""
        try:
            page_id = str(uuid.uuid4())

            page = DocumentationPage(
                id=page_id,
                title=page_data['title'],
                slug=self._generate_slug(page_data['title']),
                content=page_data['content'],
                type=DocumentationType(page_data['type']),
                status=ContentStatus(page_data.get('status', 'draft')),
                author=page_data['author'],
                tags=page_data.get('tags', []),
                parent_id=page_data.get('parent_id'),
                order=page_data.get('order', 0),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=page_data.get('version', '1.0'),
                metadata=page_data.get('metadata', {})
            )

            self.documentation_pages[page_id] = page
            await self._save_documentation_page(page)

            # Update search index
            await self._index_page_for_search(page)

            self.logger.info(f"Documentation page created: {page.title}")
            return page_id

        except Exception as e:
            self.logger.error(f"Documentation page creation failed: {e}")
            raise

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    async def update_documentation_page(self, page_id: str, updates: Dict[str, Any]) -> bool:
        """Update documentation page"""
        try:
            page = self.documentation_pages.get(page_id)
            if not page:
                raise Exception(f"Page {page_id} not found")

            # Update fields
            for field, value in updates.items():
                if hasattr(page, field):
                    setattr(page, field, value)

            page.updated_at = datetime.now()

            await self._save_documentation_page(page)
            await self._index_page_for_search(page)

            self.logger.info(f"Documentation page updated: {page.title}")
            return True

        except Exception as e:
            self.logger.error(f"Documentation page update failed: {e}")
            return False

    async def get_documentation_tree(self) -> Dict[str, Any]:
        """Get hierarchical documentation structure"""
        try:
            # Build tree structure
            tree = {}
            root_pages = []

            # Get published pages only
            published_pages = [
                page for page in self.documentation_pages.values()
                if page.status == ContentStatus.PUBLISHED
            ]

            # Group by type and parent
            for page in published_pages:
                if not page.parent_id:
                    root_pages.append(page)

            # Sort by order
            root_pages.sort(key=lambda x: x.order)

            # Build tree recursively
            def build_subtree(parent_id: str) -> List[Dict[str, Any]]:
                children = [
                    page for page in published_pages
                    if page.parent_id == parent_id
                ]
                children.sort(key=lambda x: x.order)

                result = []
                for child in children:
                    child_data = {
                        "id": child.id,
                        "title": child.title,
                        "slug": child.slug,
                        "type": child.type.value,
                        "children": build_subtree(child.id)
                    }
                    result.append(child_data)

                return result

            # Build final tree
            for page in root_pages:
                tree[page.type.value] = tree.get(page.type.value, [])
                page_data = {
                    "id": page.id,
                    "title": page.title,
                    "slug": page.slug,
                    "type": page.type.value,
                    "children": build_subtree(page.id)
                }
                tree[page.type.value].append(page_data)

            return tree

        except Exception as e:
            self.logger.error(f"Documentation tree generation failed: {e}")
            return {}

    # API Documentation

    async def create_api_endpoint(self, endpoint_data: Dict[str, Any]) -> str:
        """Create API endpoint documentation"""
        try:
            endpoint_id = str(uuid.uuid4())

            endpoint = APIEndpoint(
                id=endpoint_id,
                path=endpoint_data['path'],
                method=endpoint_data['method'].upper(),
                summary=endpoint_data['summary'],
                description=endpoint_data['description'],
                parameters=endpoint_data.get('parameters', []),
                request_body=endpoint_data.get('request_body'),
                responses=endpoint_data.get('responses', {}),
                examples=endpoint_data.get('examples', []),
                tags=endpoint_data.get('tags', []),
                deprecated=endpoint_data.get('deprecated', False)
            )

            self.api_endpoints[endpoint_id] = endpoint
            await self._save_api_endpoint(endpoint)

            # Auto-generate documentation page
            await self._generate_endpoint_documentation(endpoint)

            self.logger.info(f"API endpoint created: {endpoint.method} {endpoint.path}")
            return endpoint_id

        except Exception as e:
            self.logger.error(f"API endpoint creation failed: {e}")
            raise

    async def _generate_endpoint_documentation(self, endpoint: APIEndpoint):
        """Auto-generate documentation page for API endpoint"""
        try:
            # Generate markdown content
            content = f"""
# {endpoint.method} {endpoint.path}

{endpoint.description}

## Parameters

"""

            if endpoint.parameters:
                content += "| Name | Type | Required | Description |\n"
                content += "|------|------|----------|-------------|\n"

                for param in endpoint.parameters:
                    required = "Yes" if param.get('required', False) else "No"
                    content += f"| {param['name']} | {param.get('type', 'string')} | {required} | {param.get('description', '')} |\n"
            else:
                content += "No parameters required.\n"

            # Add request body
            if endpoint.request_body:
                content += "\n## Request Body\n\n"
                content += "```json\n"
                content += json.dumps(endpoint.request_body, indent=2)
                content += "\n```\n"

            # Add responses
            content += "\n## Responses\n\n"
            for status_code, response in endpoint.responses.items():
                content += f"### {status_code}\n\n"
                content += f"{response.get('description', '')}\n\n"

                if 'schema' in response:
                    content += "```json\n"
                    content += json.dumps(response['schema'], indent=2)
                    content += "\n```\n\n"

            # Add examples
            if endpoint.examples:
                content += "\n## Examples\n\n"
                for example in endpoint.examples:
                    content += f"### {example.get('title', 'Example')}\n\n"
                    content += "```bash\n"
                    content += f"curl -X {endpoint.method} \\\n"
                    content += f"  {self.config['api_base_url']}{endpoint.path} \\\n"
                    content += f"  -H 'Authorization: Bearer YOUR_API_KEY'\n"
                    content += "```\n\n"

            # Create documentation page
            page_data = {
                "title": f"{endpoint.method} {endpoint.path}",
                "content": content,
                "type": "api_reference",
                "status": "published",
                "author": "system",
                "tags": endpoint.tags + ["api", endpoint.method.lower()],
                "metadata": {
                    "endpoint_id": endpoint.id,
                    "auto_generated": True
                }
            }

            await self.create_documentation_page(page_data)

        except Exception as e:
            self.logger.error(f"Endpoint documentation generation failed: {e}")

    async def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI specification from endpoints"""
        try:
            spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": "Dashboard AI API",
                    "version": "1.0.0",
                    "description": "Comprehensive API for Dashboard AI Assistant",
                    "contact": {
                        "email": self.config["support_email"]
                    }
                },
                "servers": [
                    {
                        "url": self.config["api_base_url"],
                        "description": "Production server"
                    }
                ],
                "paths": {},
                "components": {
                    "securitySchemes": {
                        "bearerAuth": {
                            "type": "http",
                            "scheme": "bearer",
                            "bearerFormat": "JWT"
                        }
                    }
                }
            }

            # Add endpoints
            for endpoint in self.api_endpoints.values():
                if endpoint.path not in spec["paths"]:
                    spec["paths"][endpoint.path] = {}

                method = endpoint.method.lower()
                spec["paths"][endpoint.path][method] = {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "parameters": endpoint.parameters,
                    "responses": endpoint.responses,
                    "security": [{"bearerAuth": []}]
                }

                if endpoint.request_body:
                    spec["paths"][endpoint.path][method]["requestBody"] = endpoint.request_body

                if endpoint.deprecated:
                    spec["paths"][endpoint.path][method]["deprecated"] = True

            return spec

        except Exception as e:
            self.logger.error(f"OpenAPI spec generation failed: {e}")
            return {}

    # Code Examples

    async def create_code_example(self, example_data: Dict[str, Any]) -> str:
        """Create code example"""
        try:
            example_id = str(uuid.uuid4())

            example = CodeExample(
                id=example_id,
                title=example_data['title'],
                description=example_data['description'],
                languages=example_data['languages'],
                tags=example_data.get('tags', []),
                category=example_data.get('category', 'general'),
                difficulty=example_data.get('difficulty', 'beginner'),
                created_at=datetime.now()
            )

            self.code_examples[example_id] = example
            await self._save_code_example(example)

            self.logger.info(f"Code example created: {example.title}")
            return example_id

        except Exception as e:
            self.logger.error(f"Code example creation failed: {e}")
            raise

    async def get_code_examples_by_category(self, category: str = None) -> List[Dict[str, Any]]:
        """Get code examples by category"""
        try:
            examples = list(self.code_examples.values())

            if category:
                examples = [ex for ex in examples if ex.category == category]

            # Convert to dict format
            result = []
            for example in examples:
                result.append({
                    "id": example.id,
                    "title": example.title,
                    "description": example.description,
                    "category": example.category,
                    "difficulty": example.difficulty,
                    "languages": list(example.languages.keys()),
                    "tags": example.tags
                })

            return result

        except Exception as e:
            self.logger.error(f"Code examples retrieval failed: {e}")
            return []

    # Search Functionality

    async def search_documentation(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search documentation content"""
        try:
            # Record search query for analytics
            self.search_queries.append({
                "query": query,
                "timestamp": datetime.now(),
                "filters": filters or {}
            })

            results = []
            query_lower = query.lower()

            # Search documentation pages
            for page in self.documentation_pages.values():
                if page.status != ContentStatus.PUBLISHED:
                    continue

                score = 0

                # Title match (highest weight)
                if query_lower in page.title.lower():
                    score += 10

                # Content match
                if query_lower in page.content.lower():
                    score += 5

                # Tag match
                for tag in page.tags:
                    if query_lower in tag.lower():
                        score += 3

                # Apply filters
                if filters:
                    if 'type' in filters and page.type.value != filters['type']:
                        continue
                    if 'tags' in filters and not any(tag in page.tags for tag in filters['tags']):
                        continue

                if score > 0:
                    results.append({
                        "id": page.id,
                        "title": page.title,
                        "slug": page.slug,
                        "type": page.type.value,
                        "excerpt": self._generate_excerpt(page.content, query),
                        "score": score,
                        "url": f"/docs/{page.slug}"
                    })

            # Search API endpoints
            for endpoint in self.api_endpoints.values():
                score = 0

                if query_lower in endpoint.path.lower():
                    score += 8
                if query_lower in endpoint.summary.lower():
                    score += 6
                if query_lower in endpoint.description.lower():
                    score += 4

                if score > 0:
                    results.append({
                        "id": endpoint.id,
                        "title": f"{endpoint.method} {endpoint.path}",
                        "type": "api_endpoint",
                        "excerpt": endpoint.summary,
                        "score": score,
                        "url": f"/api-reference/{endpoint.method.lower()}-{endpoint.path.replace('/', '-')}"
                    })

            # Sort by score
            results.sort(key=lambda x: x['score'], reverse=True)

            return results[:20]  # Return top 20 results

        except Exception as e:
            self.logger.error(f"Documentation search failed: {e}")
            return []

    def _generate_excerpt(self, content: str, query: str, max_length: int = 200) -> str:
        """Generate search result excerpt"""
        try:
            query_lower = query.lower()
            content_lower = content.lower()

            # Find query position
            pos = content_lower.find(query_lower)
            if pos == -1:
                return content[:max_length] + "..." if len(content) > max_length else content

            # Extract excerpt around query
            start = max(0, pos - max_length // 2)
            end = min(len(content), start + max_length)

            excerpt = content[start:end]

            # Add ellipsis if needed
            if start > 0:
                excerpt = "..." + excerpt
            if end < len(content):
                excerpt = excerpt + "..."

            return excerpt

        except Exception as e:
            self.logger.error(f"Excerpt generation failed: {e}")
            return content[:max_length]

    # Portal Generation

    async def generate_portal_html(self, page_slug: str = None) -> str:
        """Generate HTML for developer portal"""
        try:
            if page_slug:
                # Generate specific page
                page = None
                for p in self.documentation_pages.values():
                    if p.slug == page_slug and p.status == ContentStatus.PUBLISHED:
                        page = p
                        break

                if not page:
                    return await self._generate_404_page()

                return await self._generate_documentation_page_html(page)
            else:
                # Generate homepage
                return await self._generate_homepage_html()

        except Exception as e:
            self.logger.error(f"Portal HTML generation failed: {e}")
            return "<html><body><h1>Error generating page</h1></body></html>"

    async def _generate_homepage_html(self) -> str:
        """Generate homepage HTML"""
        try:
            # Get documentation tree
            doc_tree = await self.get_documentation_tree()

            # Get popular pages
            popular_pages = await self._get_popular_pages()

            # Get recent updates
            recent_updates = await self._get_recent_updates()

            template = self.jinja_env.get_template("homepage.html")

            html = template.render(
                title="Developer Portal - Dashboard AI",
                doc_tree=doc_tree,
                popular_pages=popular_pages,
                recent_updates=recent_updates,
                config=self.config
            )

            return html

        except Exception as e:
            self.logger.error(f"Homepage generation failed: {e}")
            return "<html><body><h1>Welcome to Dashboard AI Developer Portal</h1></body></html>"

    async def _generate_documentation_page_html(self, page: DocumentationPage) -> str:
        """Generate HTML for documentation page"""
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(
                page.content,
                extensions=['codehilite', 'toc', 'tables', 'fenced_code']
            )

            # Get navigation
            doc_tree = await self.get_documentation_tree()

            # Track page view
            self.page_views[page.id] = self.page_views.get(page.id, 0) + 1

            template = self.jinja_env.get_template("documentation_page.html")

            html = template.render(
                title=page.title,
                content=html_content,
                page=page,
                doc_tree=doc_tree,
                config=self.config
            )

            return html

        except Exception as e:
            self.logger.error(f"Documentation page generation failed: {e}")
            return f"<html><body><h1>{page.title}</h1><p>Error rendering content</p></body></html>"

    async def _generate_404_page(self) -> str:
        """Generate 404 error page"""
        return """
        <html>
        <head><title>Page Not Found - Dashboard AI</title></head>
        <body>
            <h1>Page Not Found</h1>
            <p>The requested documentation page could not be found.</p>
            <a href="/">Return to Homepage</a>
        </body>
        </html>
        """

    # Support System

    async def create_support_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Create developer support ticket"""
        try:
            ticket_id = str(uuid.uuid4())

            ticket = DeveloperTicket(
                id=ticket_id,
                developer_id=ticket_data['developer_id'],
                type=SupportTicketType(ticket_data['type']),
                title=ticket_data['title'],
                description=ticket_data['description'],
                priority=ticket_data.get('priority', 'medium'),
                status='open',
                assigned_to='',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            self.developer_tickets[ticket_id] = ticket
            await self._save_support_ticket(ticket)

            # Send notification
            await self._send_ticket_notification(ticket)

            self.logger.info(f"Support ticket created: {ticket_id}")
            return ticket_id

        except Exception as e:
            self.logger.error(f"Support ticket creation failed: {e}")
            raise

    # Analytics and Feedback

    async def record_feedback(self, page_id: str, feedback_data: Dict[str, Any]):
        """Record user feedback"""
        try:
            feedback = {
                "id": str(uuid.uuid4()),
                "page_id": page_id,
                "rating": feedback_data.get('rating'),
                "comment": feedback_data.get('comment', ''),
                "helpful": feedback_data.get('helpful'),
                "timestamp": datetime.now(),
                "user_id": feedback_data.get('user_id', 'anonymous')
            }

            self.feedback_data.append(feedback)
            await self._save_feedback(feedback)

        except Exception as e:
            self.logger.error(f"Feedback recording failed: {e}")

    async def get_analytics_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate analytics report"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # Page views
            total_views = sum(self.page_views.values())

            # Popular pages
            popular_pages = sorted(
                self.page_views.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            # Search analytics
            recent_searches = [
                s for s in self.search_queries
                if s['timestamp'] > cutoff_date
            ]

            search_terms = {}
            for search in recent_searches:
                query = search['query'].lower()
                search_terms[query] = search_terms.get(query, 0) + 1

            # Feedback analytics
            recent_feedback = [
                f for f in self.feedback_data
                if f['timestamp'] > cutoff_date
            ]

            ratings = [f['rating'] for f in recent_feedback if f['rating']]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0

            return {
                "period_days": days,
                "total_page_views": total_views,
                "total_searches": len(recent_searches),
                "total_feedback": len(recent_feedback),
                "average_rating": round(avg_rating, 2),
                "popular_pages": [
                    {
                        "page_id": page_id,
                        "views": views,
                        "title": self._get_page_title(page_id)
                    }
                    for page_id, views in popular_pages
                ],
                "top_search_terms": sorted(
                    search_terms.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "documentation_stats": {
                    "total_pages": len(self.documentation_pages),
                    "published_pages": len([
                        p for p in self.documentation_pages.values()
                        if p.status == ContentStatus.PUBLISHED
                    ]),
                    "api_endpoints": len(self.api_endpoints),
                    "code_examples": len(self.code_examples)
                }
            }

        except Exception as e:
            self.logger.error(f"Analytics report generation failed: {e}")
            return {}

    def _get_page_title(self, page_id: str) -> str:
        """Get page title by ID"""
        page = self.documentation_pages.get(page_id)
        return page.title if page else "Unknown Page"

    # Background Tasks

    async def _update_search_index(self):
        """Update search index periodically"""
        while True:
            try:
                # In production, update search index (Elasticsearch, etc.)
                self.logger.debug("Search index updated")
                await asyncio.sleep(3600)  # Update every hour

            except Exception as e:
                self.logger.error(f"Search index update failed: {e}")
                await asyncio.sleep(300)

    async def _generate_analytics_reports(self):
        """Generate periodic analytics reports"""
        while True:
            try:
                # Generate daily analytics
                report = await self.get_analytics_report(1)
                await self._save_analytics_report(report)

                await asyncio.sleep(86400)  # Generate daily

            except Exception as e:
                self.logger.error(f"Analytics report generation failed: {e}")
                await asyncio.sleep(3600)

    # Helper Methods

    async def _get_popular_pages(self) -> List[Dict[str, Any]]:
        """Get popular documentation pages"""
        try:
            popular = sorted(
                self.page_views.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            result = []
            for page_id, views in popular:
                page = self.documentation_pages.get(page_id)
                if page and page.status == ContentStatus.PUBLISHED:
                    result.append({
                        "title": page.title,
                        "slug": page.slug,
                        "views": views,
                        "type": page.type.value
                    })

            return result

        except Exception as e:
            self.logger.error(f"Popular pages retrieval failed: {e}")
            return []

    async def _get_recent_updates(self) -> List[Dict[str, Any]]:
        """Get recently updated pages"""
        try:
            recent = sorted(
                [p for p in self.documentation_pages.values() if p.status == ContentStatus.PUBLISHED],
                key=lambda x: x.updated_at,
                reverse=True
            )[:5]

            return [
                {
                    "title": page.title,
                    "slug": page.slug,
                    "updated_at": page.updated_at.strftime("%Y-%m-%d"),
                    "type": page.type.value
                }
                for page in recent
            ]

        except Exception as e:
            self.logger.error(f"Recent updates retrieval failed: {e}")
            return []

    # Data Management

    async def _load_documentation(self):
        """Load documentation from storage"""
        # Sample documentation pages
        sample_pages = [
            {
                "title": "Getting Started",
                "content": """

# Getting Started with Dashboard AI API

Welcome to the Dashboard AI API! This guide will help you get up and running quickly.

## Authentication

All API requests require authentication using an API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.dashboard-ai.com/v1/
```

## Quick Start

1. Sign up for an account
2. Generate your API key
3. Make your first API call
4. Explore the documentation

## Next Steps

- [API Reference](/docs/api-reference)
- [Code Examples](/docs/examples)
- [SDKs](/docs/sdks)

""",
                "type": "guide",
                "status": "published",
                "author": "Dashboard AI Team",
                "tags": ["getting-started", "authentication", "quickstart"]
            }
        ]

        for page_data in sample_pages:
            await self.create_documentation_page(page_data)

    async def _load_api_endpoints(self):
        """Load API endpoints"""
        # Sample API endpoints
        sample_endpoints = [
            {
                "path": "/api/v1/partners",
                "method": "GET",
                "summary": "List partners",
                "description": "Retrieve a list of all partners",
                "parameters": [
                    {
                        "name": "limit",
                        "type": "integer",
                        "required": False,
                        "description": "Maximum number of results to return"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "status": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "tags": ["partners"]
            }
        ]

        for endpoint_data in sample_endpoints:
            await self.create_api_endpoint(endpoint_data)

    async def _load_code_examples(self):
        """Load code examples"""
        # Sample code examples
        sample_examples = [
            {
                "title": "Authentication Example",
                "description": "How to authenticate with the API",
                "languages": {
                    "python": """
import requests
headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}
response = requests.get('https://api.dashboard-ai.com/v1/partners', headers=headers)
print(response.json())
""",
                    "javascript": """
const headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
};
fetch('https://api.dashboard-ai.com/v1/partners', { headers })
    .then(response => response.json())
    .then(data => console.log(data));
""",
                    "curl": """
curl -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "Content-Type": 'application/json' \\
     https://api.dashboard-ai.com/v1/partners
"""
                },
                "category": "authentication",
                "difficulty": "beginner",
                "tags": ["auth", "api", "getting-started"]
            }
        ]

        for example_data in sample_examples:
            await self.create_code_example(example_data)

    async def _setup_templates(self):
        """Setup Jinja2 templates"""
        # Create basic templates
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)

        # Create homepage template
        homepage_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .section { margin-bottom: 30px; }
        .doc-tree { margin-left: 20px; }
        .popular-pages, .recent-updates { background: #f5f5f5; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Dashboard AI Developer Portal</h1>

    <div class="section">
        <h2>Documentation</h2>
        {% for type_name, pages in doc_tree.items() %}
        <div class="doc-tree">
            <h3>{{ type_name.replace('_', ' ').title() }}</h3>
            <ul>
            {% for page in pages %}
                <li><a href="/docs/{{ page.slug }}">{{ page.title }}</a></li>
                {% if page.children %}
                <ul>
                    {% for child in page.children %}
                    <li><a href="/docs/{{ child.slug }}">{{ child.title }}</a></li>
                    {% endfor %}
                </ul>
                {% endif %}
            {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <div class="popular-pages">
            <h2>Popular Pages</h2>
            <ul>
            {% for page in popular_pages %}
                <li><a href="/docs/{{ page.slug }}">{{ page.title }}</a> ({{ page.views }} views)</li>
            {% endfor %}
            </ul>
        </div>
    </div>

    <div class="section">
        <div class="recent-updates">
            <h2>Recent Updates</h2>
            <ul>
            {% for page in recent_updates %}
                <li><a href="/docs/{{ page.slug }}">{{ page.title }}</a> - {{ page.updated_at }}</li>
            {% endfor %}
            </ul>
        </div>
    </div>
</body>
</html>
"""
        (template_dir / "homepage.html").write_text(homepage_template)

        # Create documentation page template
        doc_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .nav { background: #f5f5f5; padding: 15px; margin-bottom: 20px; }
        .content { max-width: 800px; }
        .back-link { margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">← Back to Portal Home</a>
    </div>

    <div class="content">
        <h1>{{ page.title }}</h1>
        <div>{{ content|safe }}</div>
    </div>
</body>
</html>
"""
        (template_dir / "documentation_page.html").write_text(doc_template)

    async def _index_page_for_search(self, page: DocumentationPage):
        """Index page for search"""
        # In production, update search index
        pass

    async def _save_documentation_page(self, page: DocumentationPage):
        """Save documentation page"""
        # In production, save to database
        pass

    async def _save_api_endpoint(self, endpoint: APIEndpoint):
        """Save API endpoint"""
        # In production, save to database
        pass

    async def _save_code_example(self, example: CodeExample):
        """Save code example"""
        # In production, save to database
        pass

    async def _save_support_ticket(self, ticket: DeveloperTicket):
        """Save support ticket"""
        # In production, save to database
        pass

    async def _save_feedback(self, feedback: Dict[str, Any]):
        """Save user feedback"""
        # In production, save to database
        pass

    async def _save_analytics_report(self, report: Dict[str, Any]):
        """Save analytics report"""
        # In production, save to database
        pass

    async def _send_ticket_notification(self, ticket: DeveloperTicket):
        """Send support ticket notification"""
        self.logger.info(f"Support ticket notification sent: {ticket.id}")

    async def get_portal_dashboard_data(self) -> Dict[str, Any]:
        """Get developer portal dashboard data"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "documentation": {
                    "total_pages": len(self.documentation_pages),
                    "published_pages": len([
                        p for p in self.documentation_pages.values()
                        if p.status == ContentStatus.PUBLISHED
                    ]),
                    "draft_pages": len([
                        p for p in self.documentation_pages.values()
                        if p.status == ContentStatus.DRAFT
                    ])
                },
                "api_documentation": {
                    "total_endpoints": len(self.api_endpoints),
                    "deprecated_endpoints": len([
                        e for e in self.api_endpoints.values()
                        if e.deprecated
                    ])
                },
                "code_examples": {
                    "total_examples": len(self.code_examples),
                    "by_difficulty": {
                        "beginner": len([e for e in self.code_examples.values() if e.difficulty == "beginner"]),
                        "intermediate": len([e for e in self.code_examples.values() if e.difficulty == "intermediate"]),
                        "advanced": len([e for e in self.code_examples.values() if e.difficulty == "advanced"])
                    }
                },
                "analytics": {
                    "total_page_views": sum(self.page_views.values()),
                    "total_searches": len(self.search_queries),
                    "total_feedback": len(self.feedback_data)
                },
                "support": {
                    "open_tickets": len([
                        t for t in self.developer_tickets.values()
                        if t.status == "open"
                    ]),
                    "total_tickets": len(self.developer_tickets)
                }
            }

        except Exception as e:
            self.logger.error(f"Portal dashboard data generation failed: {e}")
            return {}

    async def shutdown(self):
        """Shutdown developer portal system"""
        self.logger.info("Developer Portal System shutdown complete")


# Example usage
async def main():
    """Example usage of developer portal system"""
    portal = DeveloperPortalSystem()
    await portal.initialize()

    # Search documentation
    results = await portal.search_documentation("authentication")
    print(f"Search results: {len(results)}")

    # Generate OpenAPI spec
    openapi_spec = await portal.generate_openapi_spec()
    print(f"OpenAPI spec generated with {len(openapi_spec.get('paths', {}))} endpoints")

    # Get analytics
    analytics = await portal.get_analytics_report(7)
    print(f"Analytics: {analytics}")

    # Get dashboard data
    dashboard = await portal.get_portal_dashboard_data()
    print(f"Dashboard: {dashboard}")


if __name__ == "__main__":
    asyncio.run(main())

