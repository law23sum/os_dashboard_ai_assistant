"""OneNote Viewer - Handles OneNote content display and integration with dashboard."""

from typing import Dict, List, Any, Optional
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime


class OneNoteViewer:
    """Handles OneNote content viewing and integration with the dashboard."""

    def __init__(self):
        self.session = requests.Session()
        self.shared_links = {}

    def add_shared_link(self, name: str, url: str) -> bool:
        """Add a shared OneNote link for monitoring."""
        try:
            # Parse the OneDrive sharing link
            parsed = urlparse(url)
            if '1drv.ms' in parsed.netloc:
                # Extract the sharing token and other parameters
                query_params = parse_qs(parsed.query)
                sharing_token = query_params.get('e', [None])[0]

                if sharing_token:
                    self.shared_links[name] = {
                        'url': url,
                        'sharing_token': sharing_token,
                        'added_at': datetime.now(),
                        'last_accessed': None,
                        'content_cache': None
                    }
                    return True
            return False
        except Exception as e:
            print(f"Error adding OneNote link: {e}")
            return False

    def get_shared_links(self) -> Dict[str, Dict]:
        """Get all configured shared links."""
        return self.shared_links

    def get_link_content(self, name: str) -> Optional[Dict[str, Any]]:
        """Get content from a shared OneNote link."""
        if name not in self.shared_links:
            return None

        link_data = self.shared_links[name]

        try:
            # For OneDrive shared links, we can try to access the content
            # Note: This is limited by OneDrive sharing permissions
            response = self.session.get(link_data['url'], allow_redirects=True)
            response.raise_for_status()

            # Update access time
            link_data['last_accessed'] = datetime.now()

            return {
                'name': name,
                'url': link_data['url'],
                'status': 'accessible',
                'last_accessed': link_data['last_accessed'].isoformat(),
                'content_type': response.headers.get('content-type', 'unknown'),
                'size': len(response.content) if response.content else 0
            }

        except requests.exceptions.RequestException as e:
            return {
                'name': name,
                'url': link_data['url'],
                'status': 'error',
                'error': str(e),
                'last_accessed': link_data.get('last_accessed').isoformat() if link_data.get('last_accessed') else None
            }

    def get_all_link_statuses(self) -> List[Dict[str, Any]]:
        """Get status of all shared links."""
        statuses = []
        for name in self.shared_links.keys():
            status = self.get_link_content(name)
            if status:
                statuses.append(status)
        return statuses

    def refresh_link_cache(self, name: str) -> bool:
        """Refresh cached content for a link."""
        if name not in self.shared_links:
            return False

        content = self.get_link_content(name)
        if content and content.get('status') == 'accessible':
            self.shared_links[name]['content_cache'] = content
            return True
        return False


# Integration with dashboard engine
def integrate_onenote_with_dashboard(dashboard_engine, onenote_viewer: OneNoteViewer):
    """Integrate OneNote viewer with the dashboard engine."""

    # Add OneNote data to dashboard
    onenote_data = onenote_viewer.get_all_link_statuses()

    # Update dashboard display model to include OneNote
    current_model = dashboard_engine.get_dashboard_state().get('display_model', {})

    current_model.update({
        'onenote_links': onenote_data,
        'onenote_summary': {
            'total_links': len(onenote_data),
            'accessible_links': len([l for l in onenote_data if l.get('status') == 'accessible']),
            'error_links': len([l for l in onenote_data if l.get('status') == 'error'])
        }
    })

    dashboard_engine.dashboard_state['display_model'] = current_model
    return current_model
