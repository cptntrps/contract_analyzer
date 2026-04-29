// ===== Dashboard JavaScript ===== 

class ContractAnalyzerDashboard {
    constructor() {
        this.currentTab = 'overview';
        this.analysisData = [];
        this.templatesData = [];
        this.contractsData = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadData();
        this.updateMetrics();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = e.currentTarget.getAttribute('href').substring(1);
                this.switchTab(tab);
            });
        });

        // Buttons
        document.getElementById('analyze-new-btn')?.addEventListener('click', () => {
            this.showAnalyzeModal();
        });

        document.getElementById('refresh-data')?.addEventListener('click', () => {
            this.loadData();
        });

        document.getElementById('clear-cache')?.addEventListener('click', () => {
            this.clearCache();
        });

        document.getElementById('run-analysis-btn')?.addEventListener('click', () => {
            this.runBatchAnalysis();
        });

        // File uploads
        document.getElementById('upload-contract')?.addEventListener('change', (e) => {
            this.handleFileUpload(e, 'contract');
        });

        document.getElementById('upload-template')?.addEventListener('change', (e) => {
            this.handleFileUpload(e, 'template');
        });

        // Settings
        document.getElementById('similarity-threshold')?.addEventListener('input', (e) => {
            this.updateThresholdDisplay(e);
        });

        // Modal close
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                this.closeModal();
            });
        });

        // Report filter
        document.getElementById('report-filter')?.addEventListener('change', (e) => {
            this.filterReports(e.target.value);
        });
    }

    switchTab(tabName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[href="#${tabName}"]`).parentElement.classList.add('active');

        // Update content
        document.querySelectorAll('.content-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific data
        this.loadTabData(tabName);
    }

    async loadData() {
        try {
            // Load analysis results
            const analysisResponse = await fetch('/api/analysis-results');
            if (analysisResponse.ok) {
                this.analysisData = await analysisResponse.json();
            }

            // Load templates
            const templatesResponse = await fetch('/api/templates');
            if (templatesResponse.ok) {
                this.templatesData = await templatesResponse.json();
            }

            // Load contracts
            const contractsResponse = await fetch('/api/contracts');
            if (contractsResponse.ok) {
                this.contractsData = await contractsResponse.json();
            }

            this.updateMetrics();
            this.loadTabData(this.currentTab);
        } catch (error) {
            console.error('Error loading data:', error);
            this.loadSampleData();
        }
    }

    loadSampleData() {
        // Sample data for demonstration
        this.analysisData = [
            {
                file: 'Contract_008_Capgemini_SOW_20240208.docx',
                category: 'VENDOR_CAPGEMINI',
                template: 'VENDOR_CAPGEMINI_SOW_v1.docx',
                similarity: 0.7498,
                changes: 76,
                report: 'reports/Contract_008_Capgemini_SOW_20240208_comparison_20250715_193432.docx',
                timestamp: '2025-07-15T19:34:32',
                status: this.getComplianceStatus(76)
            },
            {
                file: 'Contract_015_Generic_SOW_MODIFIED_20240301.docx',
                category: 'TYPE_SOW',
                template: 'TYPE_SOW_Standard_v1.docx',
                similarity: 0.7220,
                changes: 74,
                report: 'reports/Contract_015_Generic_SOW_MODIFIED_20240301_comparison_20250715_193440.docx',
                timestamp: '2025-07-15T19:34:40',
                status: this.getComplianceStatus(74)
            },
            {
                file: 'Contract_001_Generic_SOW_20240115.docx',
                category: 'TYPE_SOW',
                template: 'TYPE_SOW_Standard_v1.docx',
                similarity: 0.9325,
                changes: 3,
                report: 'reports/Contract_001_Generic_SOW_20240115_comparison_20250715_193312.docx',
                timestamp: '2025-07-15T19:33:12',
                status: this.getComplianceStatus(3)
            }
        ];

        this.templatesData = [
            { name: 'VENDOR_CAPGEMINI_SOW_v1.docx', type: 'Vendor Specific', lastModified: '2025-07-15' },
            { name: 'VENDOR_BLUEOPTIMA_SOW_v1.docx', type: 'Vendor Specific', lastModified: '2025-07-15' },
            { name: 'VENDOR_EPAM_SOW_v1.docx', type: 'Vendor Specific', lastModified: '2025-07-15' },
            { name: 'TYPE_SOW_Standard_v1.docx', type: 'Document Type', lastModified: '2025-07-15' },
            { name: 'TYPE_CHANGEORDER_Standard_v1.docx', type: 'Document Type', lastModified: '2025-07-15' }
        ];

        this.contractsData = [
            { name: 'Contract_008_Capgemini_SOW_20240208.docx', uploadDate: '2025-07-15', status: 'analyzed' },
            { name: 'Contract_015_Generic_SOW_MODIFIED_20240301.docx', uploadDate: '2025-07-15', status: 'analyzed' },
            { name: 'Contract_001_Generic_SOW_20240115.docx', uploadDate: '2025-07-15', status: 'analyzed' }
        ];

        this.updateMetrics();
        this.loadTabData(this.currentTab);
    }

    updateMetrics() {
        const compliantCount = this.analysisData.filter(item => item.status === 'compliant').length;
        const warningCount = this.analysisData.filter(item => item.status === 'warning').length;
        const criticalCount = this.analysisData.filter(item => item.status === 'critical').length;
        const totalAnalyzed = this.analysisData.length;
        const complianceRate = totalAnalyzed > 0 ? Math.round((compliantCount / totalAnalyzed) * 100) : 0;

        // Update header stats
        document.getElementById('total-analyzed').textContent = totalAnalyzed;
        document.getElementById('compliance-rate').textContent = `${complianceRate}%`;

        // Update metric cards
        document.getElementById('compliant-count').textContent = compliantCount;
        document.getElementById('warning-count').textContent = warningCount;
        document.getElementById('critical-count').textContent = criticalCount;
        document.getElementById('template-count').textContent = this.templatesData.length;
    }

    loadTabData(tabName) {
        switch (tabName) {
            case 'overview':
                this.loadOverviewData();
                break;
            case 'contracts':
                this.loadContractsData();
                break;
            case 'templates':
                this.loadTemplatesData();
                break;
            case 'reports':
                this.loadReportsData();
                break;
        }
    }

    loadOverviewData() {
        const tableBody = document.querySelector('#recent-analysis-table tbody');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        this.analysisData.slice(0, 10).forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${this.truncateFileName(item.file)}</td>
                <td>${item.template}</td>
                <td><span class="status-badge ${item.status}">${this.getStatusIcon(item.status)} ${this.capitalizeFirst(item.status)}</span></td>
                <td>${item.changes}</td>
                <td>${Math.round(item.similarity * 100)}%</td>
                <td>${this.formatDate(item.timestamp)}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="dashboard.viewReport('${item.report}')" title="View Report">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="dashboard.downloadReport('${item.report}')" title="Download Report">
                        <i class="fas fa-download"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }

    loadContractsData() {
        const grid = document.getElementById('contracts-grid');
        if (!grid) return;

        grid.innerHTML = '';

        this.contractsData.forEach(contract => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div class="card-header">
                    <h3>${this.truncateFileName(contract.name)}</h3>
                    <div class="card-actions">
                        <button class="btn btn-primary btn-sm" onclick="dashboard.analyzeContract('${contract.name}')" title="Analyze Contract">
                            <i class="fas fa-play"></i> Analyze
                        </button>
                    </div>
                </div>
                <div class="card-content">
                    <p><strong>Upload Date:</strong> ${contract.uploadDate}</p>
                    <p><strong>Status:</strong> <span class="status-badge ${contract.status}">${this.capitalizeFirst(contract.status)}</span></p>
                    <p><strong>File Size:</strong> ${contract.size || 'Unknown'}</p>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    loadTemplatesData() {
        const grid = document.getElementById('templates-grid');
        if (!grid) return;

        grid.innerHTML = '';

        this.templatesData.forEach(template => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div class="card-header">
                    <h3>${template.name}</h3>
                    <div class="card-actions">
                        <button class="btn btn-secondary btn-sm" onclick="dashboard.editTemplate('${template.name}')">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </div>
                <div class="card-content">
                    <p><strong>Type:</strong> ${template.type}</p>
                    <p><strong>Last Modified:</strong> ${template.lastModified}</p>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    loadReportsData() {
        const grid = document.getElementById('reports-grid');
        if (!grid) return;

        grid.innerHTML = '';

        this.analysisData.forEach(report => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div class="card-header">
                    <h3>${this.truncateFileName(report.file)}</h3>
                    <div class="card-actions">
                        <button class="btn btn-primary btn-sm" onclick="dashboard.viewReport('${report.report}')" title="View Report">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="dashboard.downloadReport('${report.report}')" title="Download Report">
                            <i class="fas fa-download"></i> Download
                        </button>
                    </div>
                </div>
                <div class="card-content">
                    <p><strong>Template:</strong> ${report.template}</p>
                    <p><strong>Status:</strong> <span class="status-badge ${report.status}">${this.getStatusIcon(report.status)} ${this.capitalizeFirst(report.status)}</span></p>
                    <p><strong>Changes:</strong> ${report.changes}</p>
                    <p><strong>Similarity:</strong> ${Math.round(report.similarity * 100)}%</p>
                    <p><strong>Generated:</strong> ${this.formatDate(report.timestamp)}</p>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    filterReports(filterValue) {
        const filteredData = filterValue === 'all' 
            ? this.analysisData 
            : this.analysisData.filter(item => {
                switch (filterValue) {
                    case 'compliant':
                        return item.status === 'compliant';
                    case 'warnings':
                        return item.status === 'warning';
                    case 'critical':
                        return item.status === 'critical';
                    default:
                        return true;
                }
            });

        // Update reports grid with filtered data
        const grid = document.getElementById('reports-grid');
        if (!grid) return;

        grid.innerHTML = '';
        filteredData.forEach(report => {
            const card = document.createElement('div');
            card.className = 'card fade-in';
            card.innerHTML = `
                <div class="card-header">
                    <h3>${this.truncateFileName(report.file)}</h3>
                    <div class="card-actions">
                        <button class="btn btn-primary btn-sm" onclick="dashboard.viewReport('${report.report}')" title="View Report">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="dashboard.downloadReport('${report.report}')" title="Download Report">
                            <i class="fas fa-download"></i> Download
                        </button>
                    </div>
                </div>
                <div class="card-content">
                    <p><strong>Template:</strong> ${report.template}</p>
                    <p><strong>Status:</strong> <span class="status-badge ${report.status}">${this.getStatusIcon(report.status)} ${this.capitalizeFirst(report.status)}</span></p>
                    <p><strong>Changes:</strong> ${report.changes}</p>
                    <p><strong>Similarity:</strong> ${Math.round(report.similarity * 100)}%</p>
                    <p><strong>Generated:</strong> ${this.formatDate(report.timestamp)}</p>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    handleFileUpload(event, type) {
        const files = event.target.files;
        if (files.length === 0) return;

        this.showModal();
        this.simulateUpload(files, type);
    }

    simulateUpload(files, type) {
        const progressBar = document.getElementById('upload-progress');
        const statusText = document.getElementById('upload-status');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                statusText.textContent = `${files.length} ${type}(s) uploaded successfully!`;
                setTimeout(() => {
                    this.closeModal();
                    this.loadData(); // Refresh data
                }, 1500);
            }
            
            progressBar.style.width = `${progress}%`;
            statusText.textContent = `Uploading ${files.length} ${type}(s)... ${Math.round(progress)}%`;
        }, 200);
    }

    showModal() {
        const modal = document.getElementById('upload-modal');
        modal.classList.add('active');
        
        // Reset progress
        document.getElementById('upload-progress').style.width = '0%';
        document.getElementById('upload-status').textContent = 'Preparing upload...';
    }

    closeModal() {
        const modal = document.getElementById('upload-modal');
        modal.classList.remove('active');
    }

    showAnalyzeModal() {
        // Create and show file picker for analysis
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.docx';
        input.multiple = true;
        input.onchange = (e) => {
            this.handleFileUpload(e, 'contract for analysis');
        };
        input.click();
    }

    updateThresholdDisplay(event) {
        const value = event.target.value;
        const display = event.target.parentElement.querySelector('.threshold-value');
        if (display) {
            display.textContent = `${value}%`;
        }
    }

    async clearCache() {
        // Show confirmation dialog
        if (!confirm('Are you sure you want to clear all analysis cache? This will remove all analysis results and reports.')) {
            return;
        }

        try {
            // Show loading state
            const clearBtn = document.getElementById('clear-cache');
            const originalText = clearBtn.innerHTML;
            clearBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Clearing...';
            clearBtn.disabled = true;

            // Call the clear cache API
            const response = await fetch('/api/clear-cache', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                
                // Reset data arrays
                this.analysisData = [];
                this.contractsData = [];
                
                // Update UI
                this.updateMetrics();
                this.loadTabData(this.currentTab);
                
                // Show success message
                const event = new CustomEvent('showToast', {
                    detail: { 
                        message: result.message || 'Cache cleared successfully', 
                        type: 'success' 
                    }
                });
                document.dispatchEvent(event);
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to clear cache');
            }

        } catch (error) {
            console.error('Error clearing cache:', error);
            const event = new CustomEvent('showToast', {
                detail: { 
                    message: `Error clearing cache: ${error.message}`, 
                    type: 'error' 
                }
            });
            document.dispatchEvent(event);
        } finally {
            // Restore button state
            const clearBtn = document.getElementById('clear-cache');
            clearBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Clear Cache';
            clearBtn.disabled = false;
        }
    }

    async runBatchAnalysis() {
        // Get all pending contracts
        const pendingContracts = this.contractsData.filter(contract => contract.status === 'pending');
        
        if (pendingContracts.length === 0) {
            const event = new CustomEvent('showToast', {
                detail: { message: 'No pending contracts found to analyze', type: 'info' }
            });
            document.dispatchEvent(event);
            return;
        }

        // Show confirmation
        if (!confirm(`Run analysis on ${pendingContracts.length} pending contracts?`)) {
            return;
        }

        try {
            // Show loading state
            const runBtn = document.getElementById('run-analysis-btn');
            const originalText = runBtn.innerHTML;
            runBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            runBtn.disabled = true;

            // Prepare contract list for batch analysis
            const contractNames = pendingContracts.map(contract => contract.name);

            // Call batch analysis API
            const response = await fetch('/api/batch-analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contracts: contractNames
                })
            });

            if (response.ok) {
                const result = await response.json();
                
                // Refresh data to show updated results
                await this.loadData();
                
                // Show success message
                const event = new CustomEvent('showToast', {
                    detail: { 
                        message: result.message || `Successfully analyzed ${result.results?.length || 0} contracts`, 
                        type: 'success' 
                    }
                });
                document.dispatchEvent(event);
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Batch analysis failed');
            }

        } catch (error) {
            console.error('Error running batch analysis:', error);
            const event = new CustomEvent('showToast', {
                detail: { 
                    message: `Error running analysis: ${error.message}`, 
                    type: 'error' 
                }
            });
            document.dispatchEvent(event);
        } finally {
            // Restore button state
            const runBtn = document.getElementById('run-analysis-btn');
            runBtn.innerHTML = '<i class="fas fa-play"></i> Run Analysis';
            runBtn.disabled = false;
        }
    }

    // Utility methods
    getComplianceStatus(changes) {
        if (changes === 0) return 'compliant';
        if (changes <= 10) return 'warning';
        return 'critical';
    }

    getStatusIcon(status) {
        switch (status) {
            case 'compliant':
                return '<i class="fas fa-check-circle"></i>';
            case 'warning':
                return '<i class="fas fa-exclamation-triangle"></i>';
            case 'critical':
                return '<i class="fas fa-times-circle"></i>';
            default:
                return '<i class="fas fa-question-circle"></i>';
        }
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    truncateFileName(fileName, maxLength = 30) {
        if (fileName.length <= maxLength) return fileName;
        const extension = fileName.split('.').pop();
        const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
        const truncatedName = nameWithoutExt.substring(0, maxLength - extension.length - 4) + '...';
        return `${truncatedName}.${extension}`;
    }

    formatDate(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // Action methods
    viewReport(reportPath) {
        console.log(`Viewing report: ${reportPath}`);
        
        // Open report in new window/tab for viewing
        const viewUrl = `/view-report?path=${encodeURIComponent(reportPath)}`;
        window.open(viewUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
        
        // Show notification
        const event = new CustomEvent('showToast', {
            detail: { message: `Opening report: ${reportPath.split('/').pop()}`, type: 'info' }
        });
        document.dispatchEvent(event);
    }

    downloadReport(reportPath) {
        console.log(`Downloading report: ${reportPath}`);
        
        // Trigger actual download
        const link = document.createElement('a');
        link.href = `/download-report?path=${encodeURIComponent(reportPath)}`;
        link.download = reportPath.split('/').pop();
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Show notification
        const event = new CustomEvent('showToast', {
            detail: { message: `Downloading: ${reportPath.split('/').pop()}`, type: 'success' }
        });
        document.dispatchEvent(event);
    }

    analyzeContract(contractName) {
        console.log(`Analyzing contract: ${contractName}`);
        
        // Show loading state
        const event = new CustomEvent('showToast', {
            detail: { message: `Starting analysis for ${contractName}...`, type: 'info' }
        });
        document.dispatchEvent(event);
        
        // In a real implementation, this would trigger the analysis
        setTimeout(() => {
            const event = new CustomEvent('showToast', {
                detail: { message: `Analysis completed for ${contractName}`, type: 'success' }
            });
            document.dispatchEvent(event);
            this.loadData();
        }, 2000);
    }

    editTemplate(templateName) {
        console.log(`Editing template: ${templateName}`);
        
        // In a real implementation, this would open a template editor
        const event = new CustomEvent('showToast', {
            detail: { message: `Template editor for ${templateName} would open here`, type: 'info' }
        });
        document.dispatchEvent(event);
    }
}

// Toast notification system
document.addEventListener('showToast', (event) => {
    const { message, type = 'info' } = event.detail;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : 'info'}-circle"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Show toast
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Hide and remove toast
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
});

// Add toast styles
const toastStyles = `
.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--bg-primary);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    padding: var(--spacing-md);
    z-index: 1100;
    transform: translateX(100%);
    transition: transform var(--transition-normal);
    min-width: 300px;
}

.toast.show {
    transform: translateX(0);
}

.toast-content {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.toast-success {
    border-left: 4px solid var(--success-color);
}

.toast-error {
    border-left: 4px solid var(--danger-color);
}

.toast-info {
    border-left: 4px solid var(--info-color);
}

.toast i {
    color: var(--text-secondary);
}

.toast-success i {
    color: var(--success-color);
}

.toast-error i {
    color: var(--danger-color);
}

.toast-info i {
    color: var(--info-color);
}
`;

// Inject toast styles
const styleSheet = document.createElement('style');
styleSheet.textContent = toastStyles;
document.head.appendChild(styleSheet);

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ContractAnalyzerDashboard();
});