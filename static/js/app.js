// Contract Analyzer JavaScript

class ContractAnalyzer {
    constructor() {
        this.fileInput = document.getElementById('fileInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.loading = document.getElementById('loading');
        this.results = document.getElementById('results');
        this.summaryMetrics = document.getElementById('summaryMetrics');
        this.summaryDetails = document.getElementById('summaryDetails');
        this.changesList = document.getElementById('changesList');
        this.uploadSection = document.getElementById('uploadSection');
        this.progressFill = document.getElementById('progressFill');
        this.downloadBtn = document.getElementById('downloadBtn');
        
        this.currentResults = null;
        this.totalAnalyzedCount = 0;
        this.significantChangesCount = 0;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File input change
        this.fileInput.addEventListener('change', () => {
            this.validateFile();
        });

        // Analyze button
        this.analyzeBtn.addEventListener('click', () => {
            this.analyzeContract();
        });

        // Drag and drop functionality
        this.setupDragAndDrop();

        // Filter controls
        this.setupFilterControls();
    }

    setupDragAndDrop() {
        this.uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadSection.classList.add('dragover');
        });

        this.uploadSection.addEventListener('dragleave', () => {
            this.uploadSection.classList.remove('dragover');
        });

        this.uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadSection.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.fileInput.files = files;
                this.validateFile();
            }
        });
    }

    setupFilterControls() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-checkbox')) {
                this.applyFilters();
            }
        });
    }

    validateFile() {
        const file = this.fileInput.files[0];
        if (!file) {
            this.analyzeBtn.disabled = true;
            return;
        }

        if (!file.name.endsWith('.docx')) {
            this.showAlert('Please select a .docx file', 'error');
            this.analyzeBtn.disabled = true;
            return;
        }

        this.analyzeBtn.disabled = false;
        this.showAlert(`File "${file.name}" selected successfully`, 'success');
    }

    async analyzeContract() {
        const file = this.fileInput.files[0];
        if (!file) {
            this.showAlert('Please select a file first', 'error');
            return;
        }

        if (!file.name.endsWith('.docx')) {
            this.showAlert('Please select a .docx file', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        this.showLoading(true);
        this.results.style.display = 'none';
        this.analyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.currentResults = data;
                this.displayResults(data);
                this.updateHeaderStats();
                this.showAlert('Analysis completed successfully!', 'success');
            } else {
                this.showAlert('Error: ' + data.error, 'error');
            }
        } catch (error) {
            this.showAlert('Error analyzing contract: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
            this.analyzeBtn.disabled = false;
        }
    }

    displayResults(data) {
        this.displaySummaryMetrics(data);
        this.displaySummaryDetails(data);
        this.displayChanges(data.analysis_results);
        this.addFilterControls(data.analysis_results);
        this.results.style.display = 'block';
        this.results.classList.add('fade-in');
    }

    displaySummaryMetrics(data) {
        const riskClass = this.getRiskClass(data.risk_level);
        
        this.summaryMetrics.innerHTML = `
            <div class="metric-card info">
                <div class="metric-icon">📊</div>
                <div class="metric-content">
                    <h3>${data.total_changes}</h3>
                    <p>Total Changes</p>
                </div>
            </div>
            <div class="metric-card ${data.significant_changes_count > 0 ? 'critical' : 'compliant'}">
                <div class="metric-icon">${data.significant_changes_count > 0 ? '⚠️' : '✅'}</div>
                <div class="metric-content">
                    <h3>${data.significant_changes_count}</h3>
                    <p>Significant Changes</p>
                </div>
            </div>
            <div class="metric-card ${data.inconsequential_changes_count > 0 ? 'warning' : 'compliant'}">
                <div class="metric-icon">📝</div>
                <div class="metric-content">
                    <h3>${data.inconsequential_changes_count}</h3>
                    <p>Minor Changes</p>
                </div>
            </div>
            <div class="metric-card ${riskClass}">
                <div class="metric-icon">${this.getRiskIcon(data.risk_level)}</div>
                <div class="metric-content">
                    <h3>${data.risk_level}</h3>
                    <p>Risk Level</p>
                </div>
            </div>
        `;
    }

    displaySummaryDetails(data) {
        this.summaryDetails.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--spacing-lg); margin-top: var(--spacing-lg);">
                <div>
                    <h4 style="margin-bottom: var(--spacing-sm); color: var(--text-primary);">📄 Contract Details</h4>
                    <p><strong>File:</strong> ${data.uploaded_filename}</p>
                    <p><strong>Template:</strong> ${data.selected_template}</p>
                    <p><strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}</p>
                </div>
                <div>
                    <h4 style="margin-bottom: var(--spacing-sm); color: var(--text-primary);">🎯 Analysis Results</h4>
                    <p><strong>Risk Assessment:</strong> <span class="status-badge ${data.risk_level.toLowerCase()}">${data.risk_level}</span></p>
                    <p><strong>Compliance Score:</strong> ${this.calculateComplianceScore(data)}%</p>
                    <p><strong>Review Priority:</strong> ${data.significant_changes_count > 0 ? 'High' : 'Low'}</p>
                </div>
            </div>
        `;
    }

    displayChanges(changes) {
        this.changesList.innerHTML = '';
        
        if (changes.length === 0) {
            this.changesList.innerHTML = '<div class="text-center" style="padding: var(--spacing-2xl); color: var(--text-muted);">No changes detected</div>';
            return;
        }

        changes.forEach((change, index) => {
            const changeDiv = document.createElement('div');
            changeDiv.className = `change-item ${change.classification.toLowerCase()}`;
            changeDiv.style.animationDelay = `${index * 0.1}s`;
            
            changeDiv.innerHTML = `
                <div class="change-header">
                    ${this.getChangeIcon(change.classification)} Change ${index + 1}
                    <span class="status-badge ${change.classification.toLowerCase()}">${change.classification}</span>
                </div>
                <div class="change-explanation">
                    <strong>Analysis:</strong> ${change.explanation}
                </div>
                ${change.deleted_text ? `
                    <div class="change-text deleted-text">
                        <strong>🗑️ Deleted:</strong> ${this.truncateText(change.deleted_text, 200)}
                    </div>
                ` : ''}
                ${change.inserted_text ? `
                    <div class="change-text added-text">
                        <strong>➕ Added:</strong> ${this.truncateText(change.inserted_text, 200)}
                    </div>
                ` : ''}
            `;
            
            this.changesList.appendChild(changeDiv);
        });
    }

    addFilterControls(changes) {
        const significantCount = changes.filter(c => c.classification === 'SIGNIFICANT').length;
        const inconsequentialCount = changes.filter(c => c.classification === 'INCONSEQUENTIAL').length;
        
        const filterControls = document.createElement('div');
        filterControls.className = 'filter-controls';
        filterControls.innerHTML = `
            <h4>🔍 Filter Changes</h4>
            <div style="display: flex; gap: var(--spacing-lg); flex-wrap: wrap;">
                <label>
                    <input type="checkbox" class="filter-checkbox" data-filter="significant" checked>
                    Show Significant Changes (${significantCount})
                </label>
                <label>
                    <input type="checkbox" class="filter-checkbox" data-filter="inconsequential" checked>
                    Show Inconsequential Changes (${inconsequentialCount})
                </label>
            </div>
        `;
        
        this.changesList.insertBefore(filterControls, this.changesList.firstChild);
    }

    applyFilters() {
        const showSignificant = document.querySelector('[data-filter="significant"]')?.checked;
        const showInconsequential = document.querySelector('[data-filter="inconsequential"]')?.checked;
        
        const changeItems = document.querySelectorAll('.change-item');
        changeItems.forEach(item => {
            const isSignificant = item.classList.contains('significant');
            const isInconsequential = item.classList.contains('inconsequential');
            
            if ((isSignificant && showSignificant) || (isInconsequential && showInconsequential)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    async downloadReport(customFilename = null) {
        if (!this.currentResults) {
            this.showAlert('No analysis results available to download', 'error');
            return;
        }

        const filename = customFilename || this.currentResults.uploaded_filename.replace('.docx', '_analyzed.docx');
        
        try {
            this.showAlert('Preparing download...', 'info');
            
            const response = await fetch(`/api/download/${filename}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showAlert('Download completed successfully!', 'success');
            } else {
                this.showAlert('Error downloading file', 'error');
            }
        } catch (error) {
            this.showAlert('Error downloading file: ' + error.message, 'error');
        }
    }

    clearResults() {
        this.results.style.display = 'none';
        this.fileInput.value = '';
        this.analyzeBtn.disabled = true;
        this.currentResults = null;
        this.showAlert('Results cleared', 'info');
    }

    shareResults() {
        if (!this.currentResults) {
            this.showAlert('No results to share', 'error');
            return;
        }

        const shareData = {
            title: 'Contract Analysis Results',
            text: `Contract: ${this.currentResults.uploaded_filename}\nChanges: ${this.currentResults.total_changes}\nRisk Level: ${this.currentResults.risk_level}`,
            url: window.location.href
        };

        if (navigator.share) {
            navigator.share(shareData);
        } else {
            // Fallback - copy to clipboard
            navigator.clipboard.writeText(shareData.text).then(() => {
                this.showAlert('Results copied to clipboard', 'success');
            });
        }
    }

    exportChanges() {
        if (!this.currentResults) {
            this.showAlert('No changes to export', 'error');
            return;
        }

        const csvContent = this.convertChangesToCSV(this.currentResults.analysis_results);
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.currentResults.uploaded_filename}_changes.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        this.showAlert('Changes exported successfully', 'success');
    }

    convertChangesToCSV(changes) {
        const headers = ['Change #', 'Classification', 'Explanation', 'Deleted Text', 'Added Text'];
        const rows = changes.map((change, index) => [
            index + 1,
            change.classification,
            change.explanation,
            change.deleted_text || '',
            change.inserted_text || ''
        ]);
        
        return [headers, ...rows].map(row => 
            row.map(cell => `"${cell.toString().replace(/"/g, '""')}"`).join(',')
        ).join('\n');
    }

    updateHeaderStats() {
        this.totalAnalyzedCount++;
        if (this.currentResults) {
            this.significantChangesCount += this.currentResults.significant_changes_count;
        }
        
        document.getElementById('totalAnalyzed').textContent = this.totalAnalyzedCount;
        document.getElementById('significantChanges').textContent = this.significantChangesCount;
    }

    showLoading(show) {
        if (show) {
            this.loading.style.display = 'block';
            this.loading.classList.add('active');
            this.updateProgress(0);
            this.simulateProgress();
        } else {
            this.loading.style.display = 'none';
            this.loading.classList.remove('active');
            if (this.progressInterval) {
                clearInterval(this.progressInterval);
            }
        }
    }

    simulateProgress() {
        let progress = 0;
        this.progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) {
                progress = 90;
            }
            this.updateProgress(progress);
        }, 500);
    }

    updateProgress(percentage) {
        if (this.progressFill) {
            this.progressFill.style.width = `${percentage}%`;
        }
    }

    showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;

        // Insert after the upload section
        this.uploadSection.parentNode.insertBefore(alert, this.uploadSection.nextSibling);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }

    getRiskClass(riskLevel) {
        switch (riskLevel) {
            case 'HIGH': return 'critical';
            case 'MEDIUM': return 'warning';
            case 'LOW': return 'compliant';
            default: return 'compliant';
        }
    }

    getRiskIcon(riskLevel) {
        switch (riskLevel) {
            case 'HIGH': return '🚨';
            case 'MEDIUM': return '⚠️';
            case 'LOW': return '✅';
            default: return '📊';
        }
    }

    getChangeIcon(classification) {
        return classification === 'SIGNIFICANT' ? '🚨' : '📝';
    }

    calculateComplianceScore(data) {
        const total = data.total_changes;
        const significant = data.significant_changes_count;
        if (total === 0) return 100;
        return Math.round(((total - significant) / total) * 100);
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + '...';
    }
}

// Health check functionality
class HealthChecker {
    constructor() {
        this.checkInterval = null;
        this.startHealthCheck();
    }

    async startHealthCheck() {
        await this.checkHealth();
        
        // Check every 30 seconds
        this.checkInterval = setInterval(() => {
            this.checkHealth();
        }, 30000);
    }

    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            this.updateHealthStatus(data);
            this.updateSystemStatus(data);
        } catch (error) {
            this.updateHealthStatus({
                status: 'unhealthy',
                error: 'Could not connect to server'
            });
            this.updateSystemStatus({
                status: 'unhealthy',
                ollama_connected: false
            });
        }
    }

    updateHealthStatus(data) {
        let statusIndicator = document.getElementById('healthStatus');
        
        if (!statusIndicator) {
            statusIndicator = document.createElement('div');
            statusIndicator.id = 'healthStatus';
            statusIndicator.className = 'health-status';
            statusIndicator.style.cssText = `
                position: fixed;
                top: var(--spacing-md);
                right: var(--spacing-md);
                padding: var(--spacing-sm) var(--spacing-md);
                border-radius: var(--radius-md);
                font-size: var(--text-sm);
                font-weight: 500;
                z-index: 1000;
                box-shadow: var(--shadow-md);
                transition: all var(--transition-fast);
            `;
            document.body.appendChild(statusIndicator);
        }

        if (data.status === 'healthy') {
            statusIndicator.style.backgroundColor = 'var(--success-color)';
            statusIndicator.style.color = 'var(--text-white)';
            statusIndicator.textContent = '🟢 System Healthy';
            statusIndicator.title = `Ollama: ${data.ollama_connected ? 'Connected' : 'Disconnected'}`;
        } else {
            statusIndicator.style.backgroundColor = 'var(--danger-color)';
            statusIndicator.style.color = 'var(--text-white)';
            statusIndicator.textContent = '🔴 System Issues';
            statusIndicator.title = data.error || 'Unknown error';
        }
    }

    updateSystemStatus(data) {
        const systemStatusElement = document.getElementById('systemStatus');
        if (systemStatusElement) {
            systemStatusElement.textContent = data.status === 'healthy' ? '🟢' : '🔴';
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.contractAnalyzer = new ContractAnalyzer();
    window.healthChecker = new HealthChecker();
});

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString();
}

// Export for use in other modules
window.ContractAnalyzer = ContractAnalyzer;
window.HealthChecker = HealthChecker; 