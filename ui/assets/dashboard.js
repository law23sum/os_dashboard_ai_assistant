// OS Dashboard AI Assistant JavaScript

class DashboardApp {
    constructor() {
        this.lastUpdated = document.getElementById('last-updated');
        this.refreshBtn = document.getElementById('refresh-btn');
        this.eventsCount = document.getElementById('events-count');
        this.emailsCount = document.getElementById('emails-count');
        this.docsCount = document.getElementById('docs-count');
        this.onenoteCount = document.getElementById('onenote-count');
        this.eventsList = document.getElementById('events-list');
        this.emailsList = document.getElementById('emails-list');
        this.documentsList = document.getElementById('documents-list');
        this.onenoteList = document.getElementById('onenote-list');

        this.init();
    }

    init() {
        this.refreshBtn.addEventListener('click', () => this.refreshData());
        this.loadDashboardData();

        // Auto-refresh every 5 minutes
        setInterval(() => this.refreshData(), 5 * 60 * 1000);
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/dashboard-data');
            const data = await response.json();
            this.updateUI(data);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async refreshData() {
        try {
            this.refreshBtn.disabled = true;
            this.refreshBtn.textContent = 'Refreshing...';

            const response = await fetch('/api/refresh');
            const result = await response.json();

            if (result.success) {
                this.updateUI(result.data);
            } else {
                this.showError('Failed to refresh data');
            }
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showError('Failed to refresh data');
        } finally {
            this.refreshBtn.disabled = false;
            this.refreshBtn.textContent = 'Refresh Data';
        }
    }

    updateUI(data) {
        if (!data) return;

        const summary = data.summary || {};

        // Update counts
        this.eventsCount.textContent = summary.todays_events_count || 0;
        this.emailsCount.textContent = summary.recent_emails_count || 0;
        this.docsCount.textContent = summary.recent_docs_count || 0;
        this.onenoteCount.textContent = summary.onenote_accessible_count || 0;

        // Update last updated time
        if (data.last_updated) {
            const date = new Date(data.last_updated);
            this.lastUpdated.textContent = `Last updated: ${date.toLocaleString()}`;
        }

        // Update events list
        this.updateEventsList(data.todays_events || []);

        // Update emails list
        this.updateEmailsList(data.recent_emails || []);

        // Update documents list
        this.updateDocumentsList(data.recent_documents || []);

        // Update OneNote list
        this.updateOneNoteList(data.onenote_links || []);
    }

    updateEventsList(events) {
        if (events.length === 0) {
            this.eventsList.innerHTML = '<p class="empty-state">No events today</p>';
            return;
        }

        const html = events.map(event => `
            <div class="item">
                <div class="item-title">${this.escapeHtml(event.title || 'Untitled Event')}</div>
                <div class="item-meta">${this.formatTime(event.start_time)} - ${this.formatTime(event.end_time)}</div>
                ${event.location ? `<div class="item-meta">${this.escapeHtml(event.location)}</div>` : ''}
            </div>
        `).join('');

        this.eventsList.innerHTML = html;
    }

    updateEmailsList(emails) {
        if (emails.length === 0) {
            this.emailsList.innerHTML = '<p class="empty-state">No recent emails</p>';
            return;
        }

        const html = emails.map(email => `
            <div class="item">
                <div class="item-title">${this.escapeHtml(email.subject || 'No subject')}</div>
                <div class="item-meta">From: ${this.escapeHtml(email.sender || 'Unknown')}</div>
            </div>
        `).join('');

        this.emailsList.innerHTML = html;
    }

    updateDocumentsList(documents) {
        if (documents.length === 0) {
            this.documentsList.innerHTML = '<p class="empty-state">No recent documents</p>';
            return;
        }

        const html = documents.map(doc => `
            <div class="item">
                <div class="item-title">${this.escapeHtml(doc.name || 'Unnamed document')}</div>
                <div class="item-meta">${this.formatFileSize(doc.size || 0)} • ${this.formatDate(doc.modified_time)}</div>
            </div>
        `).join('');

        this.documentsList.innerHTML = html;
    }

    updateOneNoteList(onenoteLinks) {
        if (onenoteLinks.length === 0) {
            this.onenoteList.innerHTML = '<p class="empty-state">No OneNote links configured</p>';
            return;
        }

        const html = onenoteLinks.map(link => {
            const statusClass = link.status === 'accessible' ? 'status-accessible' : 'status-error';
            const statusIcon = link.status === 'accessible' ? '✓' : '✗';
            const lastAccessed = link.last_accessed ? this.formatDate(link.last_accessed) : 'Never';

            return `
                <div class="item">
                    <div class="item-title">
                        <a href="${this.escapeHtml(link.url)}" target="_blank" class="onenote-link">
                            ${this.escapeHtml(link.name)}
                        </a>
                        <span class="status-indicator ${statusClass}" title="${link.status}">${statusIcon}</span>
                    </div>
                    <div class="item-meta">Last accessed: ${lastAccessed}</div>
                    ${link.error ? `<div class="item-meta error">Error: ${this.escapeHtml(link.error)}</div>` : ''}
                </div>
            `;
        }).join('');

        this.onenoteList.innerHTML = html;
    }

    formatTime(datetimeStr) {
        if (!datetimeStr) return '';
        try {
            const date = new Date(datetimeStr);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch {
            return datetimeStr;
        }
    }

    formatDate(datetimeStr) {
        if (!datetimeStr) return '';
        try {
            const date = new Date(datetimeStr);
            return date.toLocaleDateString();
        } catch {
            return datetimeStr;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        // Simple error display - could be enhanced with a toast notification
        console.error(message);
        alert(message);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DashboardApp();
});
