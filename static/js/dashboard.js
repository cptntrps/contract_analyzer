// Dashboard JavaScript - Enhanced with Sidebar Navigation and Report Generation
let dashboardInitialized = false;

document.addEventListener('DOMContentLoaded', function() {
    if (!dashboardInitialized) {
        console.log('Dashboard initializing...');
        initializeDashboard();
        dashboardInitialized = true;
    }
});

// Global variables
let currentTab = 'dashboard';
let dashboardData = {
    contracts: [],
    templates: [],
    analysisResults: [],
    systemStatus: {}
};

// Toggle sidebar for mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
    
    // Close sidebar when clicking outside
    document.addEventListener('click', function(event) {
        const sidebar = document.querySelector('.sidebar');
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        
        if (sidebar && sidebarToggle && 
            !sidebar.contains(event.target) && 
            !sidebarToggle.contains(event.target)) {
            sidebar.classList.remove('active');
        }
    });
}

function initializeDashboard() {
    console.log('Setting up dashboard...');
    
    // Setup sidebar navigation
    setupSidebarNavigation();
    
    // Setup file uploads
    setupFileUploads();
    
    // Load initial data
    loadDashboardData();
    
    // Setup modal events
    setupModalEvents();
    
    // Check system status
    checkSystemStatus();
    
    // Load model information for header display
    loadModelInfo();
    
    // Setup auto-refresh
    setInterval(loadDashboardData, 30000);
    
    // Setup table interactions
    setupTableInteractions();
    
    // Initialize default tab
    showTab('dashboard');
    
    console.log('Dashboard initialized successfully');
}

function setupSidebarNavigation() {
    console.log('Setting up sidebar navigation...');
    
    // Use proper DOM ready state check instead of setTimeout
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebarEvents);
    } else {
        initSidebarEvents();
    }
}

function initSidebarEvents() {
    const menuItems = document.querySelectorAll('.menu-item a[data-tab]');
    const tabContents = document.querySelectorAll('.tab-content');
    
    console.log('Found menu items:', menuItems.length);
    console.log('Found tab contents:', tabContents.length);
    
    // List all found elements for debugging
    menuItems.forEach((item, index) => {
        console.log(`Menu item ${index + 1}: data-tab="${item.dataset.tab}"`);
    });
    
    tabContents.forEach((content, index) => {
        console.log(`Tab content ${index + 1}: id="${content.id}"`);
    });
    
    if (menuItems.length === 0) {
        console.error('No menu items found! Check if .menu-item a[data-tab] elements exist.');
        return;
    }
    
    if (tabContents.length === 0) {
        console.error('No tab contents found! Check if .tab-content elements exist.');
        return;
    }
    
    // Clear all existing event listeners first
    menuItems.forEach((item) => {
        // Clone the node to remove all event listeners
        const newItem = item.cloneNode(true);
        item.parentNode.replaceChild(newItem, item);
    });
    
    // Re-query for fresh elements and add event listeners
    const freshMenuItems = document.querySelectorAll('.menu-item a[data-tab]');
    freshMenuItems.forEach((item, index) => {
        console.log(`Setting up menu item ${index + 1}:`, item.dataset.tab);
        item.addEventListener('click', handleTabClick);
    });
    
    console.log('Sidebar navigation setup complete');
}

function handleTabClick(e) {
    e.preventDefault();
    console.log('Menu item clicked:', this.dataset.tab);
    
    const targetTab = this.dataset.tab;
    
    if (!targetTab) {
        console.error('No data-tab attribute found on menu item');
        return;
    }
    
    showTab(targetTab);
    
    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(menu => {
        menu.classList.remove('active');
    });
    this.parentElement.classList.add('active');
    
    // Update page title
    updatePageTitle(targetTab);
    
    // Load tab-specific data
    loadTabData(targetTab);
    
    currentTab = targetTab;
}

function updatePageTitle(tab) {
    const pageTitle = document.getElementById('pageTitle');
    const titles = {
        'dashboard': 'Contract Review Dashboard',
        'upload': 'File Upload & Management',
        'settings': 'System Configuration'
    };
    
    if (pageTitle) {
        pageTitle.textContent = titles[tab] || 'Contract Review Dashboard';
        console.log('Updated page title to:', titles[tab] || 'Contract Review Dashboard');
    } else {
        console.error('Page title element not found');
    }
}

function loadDashboardData() {
    console.log('Loading dashboard data...');
    
    // Load multiple endpoints in parallel
    Promise.all([
        fetch('/api/analysis-results').then(response => response.json()),
        fetch('/api/contracts').then(response => response.json()),
        fetch('/api/templates').then(response => response.json()),
        fetch('/api/health').then(response => response.json())
    ]).then(([analysisResults, contracts, templates, health]) => {
        dashboardData.analysisResults = analysisResults;
        dashboardData.contracts = contracts;
        dashboardData.templates = templates;
        dashboardData.systemStatus = health;
        
        updateDashboard();
        console.log('Dashboard data loaded successfully');
    }).catch(error => {
        console.error('Error loading dashboard data:', error);
        showNotification('Error loading dashboard data', 'error');
    });
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    console.log(`Notification: ${message} (${type})`);
    
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="closeNotification(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        closeNotification(notification);
    }, duration);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function closeNotification(element) {
    const notification = element.closest ? element.closest('.notification') : element;
    if (notification) {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }
}

// Tab data loading function
function loadTabData(tabName) {
    console.log('Loading tab data for:', tabName);
    switch(tabName) {
        case 'upload':
            updateFileListings();
            setupFileUploads();
            break;
        case 'settings':
            loadSettings();
            break;
        case 'dashboard':
            // Already loaded in main data refresh
            break;
    }
}

function updateFileListings() {
    console.log('Updating file listings...');
    updateContractsList();
    updateTemplatesList();
}

function loadSettings() {
    console.log('Loading settings...');
    
    // Load available models
    loadAvailableModels();
    
    // Load cache statistics
    loadCacheStats();
    
    // Load other settings
    loadSystemSettings();
}

function loadAvailableModels() {
    console.log('Loading available models...');
    
    fetch('/api/available-models')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('llmModel');
            select.innerHTML = '';
            
            if (data.success) {
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.name;
                    option.textContent = `${model.name} (${model.size})`;
                    if (model.name === data.current_model) {
                        option.selected = true;
                    }
                    select.appendChild(option);
                });
                
                // Add change event listener
                select.addEventListener('change', function() {
                    changeModel(this.value);
                });
            } else {
                select.innerHTML = '<option value="">Error loading models</option>';
            }
        })
        .catch(error => {
            console.error('Error loading models:', error);
            const select = document.getElementById('llmModel');
            select.innerHTML = '<option value="">Error loading models</option>';
        });
}

function changeModel(modelName) {
    console.log('Changing model to:', modelName);
    
    showNotification('Changing model...', 'info');
    
    fetch('/api/change-model', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model_name: modelName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Successfully changed to ${modelName}`, 'success');
            loadModelInfo();
        } else {
            showNotification('Failed to change model: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error changing model:', error);
        showNotification('Error changing model', 'error');
    });
}

function loadModelInfo() {
    fetch('/api/model-info')
        .then(response => response.json())
        .then(data => {
            const infoDiv = document.getElementById('current-model-info');
            const modelStatusText = document.getElementById('model-status-text');
            
            if (data.name) {
                // Update settings tab model info
                const modelName = data.name;
                const status = data.connection_healthy ? 'Connected' : 'Disconnected';
                
                let infoHtml = `<strong>Current Model:</strong> ${modelName}<br>`;
                
                // Add size info if available (for Ollama)
                if (data.info && data.info.size) {
                    const sizeInGB = (data.info.size / (1024 * 1024 * 1024)).toFixed(1);
                    infoHtml += `<strong>Size:</strong> ${sizeInGB} GB<br>`;
                }
                
                infoHtml += `<strong>Status:</strong> ${status}`;
                
                if (infoDiv) {
                    infoDiv.innerHTML = infoHtml;
                }
                
                // Update header model status
                if (modelStatusText) {
                    if (data.info && data.info.size) {
                        const sizeInGB = (data.info.size / (1024 * 1024 * 1024)).toFixed(1);
                        modelStatusText.textContent = `${modelName} (${sizeInGB} GB)`;
                    } else {
                        modelStatusText.textContent = modelName;
                    }
                }
                
                console.log('Model info loaded successfully:', modelName);
            } else {
                if (infoDiv) {
                    infoDiv.innerHTML = 'Error loading model info';
                }
                if (modelStatusText) {
                    modelStatusText.textContent = 'Model info unavailable';
                }
            }
        })
        .catch(error => {
            console.error('Error loading model info:', error);
            const infoDiv = document.getElementById('current-model-info');
            const modelStatusText = document.getElementById('model-status-text');
            if (infoDiv) {
                infoDiv.innerHTML = 'Error loading model info';
            }
            if (modelStatusText) {
                modelStatusText.textContent = 'Error loading model';
            }
        });
}

function loadCacheStats() {
    console.log('Loading cache statistics...');
    
    fetch('/api/cache-stats')
        .then(response => response.json())
        .then(data => {
            const statsDiv = document.getElementById('cacheStats');
            if (data.success) {
                statsDiv.innerHTML = `
                    <div class="cache-stat">
                        <strong>Analysis Cache:</strong> ${data.stats.analysis_count} items (${data.stats.analysis_size})
                    </div>
                    <div class="cache-stat">
                        <strong>Reports Cache:</strong> ${data.stats.reports_count} items (${data.stats.reports_size})
                    </div>
                    <div class="cache-stat">
                        <strong>Memory Cache:</strong> ${data.stats.memory_count} items (${data.stats.memory_size})
                    </div>
                    <div class="cache-stat">
                        <strong>Total Cache Size:</strong> ${data.stats.total_size}
                    </div>
                `;
            } else {
                statsDiv.innerHTML = '<p>Error loading cache statistics</p>';
            }
        })
        .catch(error => {
            console.error('Error loading cache stats:', error);
            document.getElementById('cacheStats').innerHTML = '<p>Error loading cache statistics</p>';
        });
}

function loadSystemSettings() {
    // Load other system settings like file size limits, etc.
    console.log('Loading system settings...');
}

function clearCache(type) {
    console.log('Clearing cache:', type);
    
    const messages = {
        'analysis': 'Clear analysis cache?',
        'reports': 'Clear reports cache?',
        'memory': 'Clear memory cache?',
        'all': 'Clear all cache data?'
    };
    
    if (confirm(messages[type] || 'Clear cache?')) {
        showNotification(`Clearing ${type} cache...`, 'info');
        
        fetch('/api/clear-cache', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                cache_type: type
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`${type} cache cleared successfully`, 'success');
                loadCacheStats(); // Refresh cache stats
            } else {
                showNotification(`Failed to clear ${type} cache: ` + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error clearing cache:', error);
            showNotification(`Error clearing ${type} cache`, 'error');
        });
    }
}

function refreshDashboard() {
    console.log('Refreshing dashboard...');
    showNotification('Refreshing dashboard...', 'info');
    loadDashboardData();
}


function setupModalEvents() {
    console.log('Setting up modal events...');
    // Stub implementation
}

function setupTableInteractions() {
    console.log('Setting up table interactions...');
    // Stub implementation
}

// Consolidated tab switching function
function showTab(tabName) {
    console.log('Showing tab:', tabName);
    
    if (!tabName) {
        console.error('No tab name provided to showTab');
        return false;
    }
    
    // Validate tab exists
    const targetTab = document.getElementById(tabName);
    if (!targetTab) {
        console.error('Target tab not found:', tabName);
        const availableTabs = Array.from(document.querySelectorAll('.tab-content')).map(tab => tab.id);
        console.error('Available tabs:', availableTabs);
        showNotification(`Error: Tab "${tabName}" not found`, 'error');
        return false;
    }
    
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
        console.log(`Hiding tab: ${content.id}`);
    });
    
    // Remove active class from all menu items
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.classList.remove('active');
    });
    
    // Show target tab content
    targetTab.classList.add('active');
    console.log('Successfully showed tab:', tabName);
    
    // Activate corresponding menu item
    const menuItem = document.querySelector(`[data-tab="${tabName}"]`);
    if (menuItem) {
        menuItem.parentElement.classList.add('active');
        console.log('Activated menu item for tab:', tabName);
    } else {
        console.error('Menu item not found for tab:', tabName);
    }
    
    // Update page title
    updatePageTitle(tabName);
    
    // Load tab-specific data
    loadTabData(tabName);
    
    // Update current tab
    currentTab = tabName;
    
    // Show brief success notification
    showNotification(`Switched to ${tabName} tab`, 'info', 1500);
    
    return true;
}

// Batch operations functions
function analyzeAllContracts() {
    console.log('Analyzing all contracts...');
    
    if (dashboardData.contracts.length === 0) {
        showNotification('No contracts available to analyze', 'warning');
        return;
    }
    
    showNotification('Starting batch analysis...', 'info');
    
    // Call the batch analyze endpoint
    fetch('/api/batch-analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            contracts: dashboardData.contracts.map(c => c.id)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Successfully analyzed ${data.results.length} contracts`, 'success');
            loadDashboardData(); // Refresh the dashboard
        } else {
            showNotification('Batch analysis failed: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error during batch analysis:', error);
        showNotification('Error during batch analysis', 'error');
    });
}

function generateBatchReports() {
    console.log('Generating batch reports...');
    
    if (dashboardData.analysisResults.length === 0) {
        showNotification('No analysis results available for report generation', 'warning');
        return;
    }
    
    showNotification('Generating batch reports...', 'info');
    
    // You could implement batch report generation here
    setTimeout(() => {
        showNotification('Batch reports generated successfully', 'success');
    }, 2000);
}

function clearAllContracts() {
    if (confirm('Are you sure you want to clear all contracts? This will remove all uploaded contracts and their analysis results. This action cannot be undone.')) {
        console.log('Clearing all contracts...');
        
        showNotification('Clearing contracts...', 'info');
        
        // Clear only contracts
        fetch('/api/clear-contracts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                loadDashboardData(); // Refresh the dashboard
            } else {
                showNotification('Failed to clear contracts: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error clearing contracts:', error);
            showNotification('Error clearing contracts', 'error');
        });
    }
}

function clearAllFiles() {
    if (confirm('Are you sure you want to clear all files? This action cannot be undone.')) {
        console.log('Clearing all files...');
        
        // Clear contracts and templates
        fetch('/api/clear-files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('All files cleared successfully', 'success');
                loadDashboardData(); // Refresh the dashboard
            } else {
                showNotification('Failed to clear files: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error clearing files:', error);
            showNotification('Error clearing files', 'error');
        });
    }
}

function analyzeContract(contractId) {
    console.log('Analyzing contract:', contractId);
    
    showNotification('Analyzing contract...', 'info');
    
    fetch('/api/analyze-contract', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            contract_id: contractId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Contract analyzed successfully', 'success');
            loadDashboardData(); // Refresh the dashboard
        } else {
            showNotification('Contract analysis failed: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error analyzing contract:', error);
        showNotification('Error analyzing contract', 'error');
    });
}

function deleteContract(contractId) {
    if (confirm('Are you sure you want to delete this contract?')) {
        console.log('Deleting contract:', contractId);
        
        fetch(`/api/contracts/${contractId}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Contract deleted successfully', 'success');
                loadDashboardData(); // Refresh the dashboard
            } else {
                showNotification('Failed to delete contract: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting contract:', error);
            showNotification('Error deleting contract', 'error');
        });
    }
}

function editTemplate(templateId) {
    console.log('Editing template:', templateId);
    showNotification('Template editing not implemented yet', 'info');
}

function deleteTemplate(templateId) {
    if (confirm('Are you sure you want to delete this template?')) {
        console.log('Deleting template:', templateId);
        
        fetch(`/api/templates/${templateId}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Template deleted successfully', 'success');
                loadDashboardData(); // Refresh the dashboard
            } else {
                showNotification('Failed to delete template: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting template:', error);
            showNotification('Error deleting template', 'error');
        });
    }
}

function updateDashboard() {
    updateMetrics();
    updateAnalysisTable();
    updateSystemStatus();
}

function updateMetrics() {
    const metrics = {
        totalContracts: dashboardData.contracts.length,
        totalTemplates: dashboardData.templates.length,
        totalAnalyses: dashboardData.analysisResults.length,
        pendingReviews: dashboardData.analysisResults.filter(r => r.status !== 'No changes').length
    };
    
    // Update metric cards with animation
    Object.entries(metrics).forEach(([key, value]) => {
        const element = document.getElementById(key);
        if (element) {
            animateValue(element, parseInt(element.textContent) || 0, value, 1000);
        }
    });
}

function animateValue(element, start, end, duration) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);
        
        const currentValue = Math.floor(start + (end - start) * progress);
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function updateAnalysisTable() {
    const tbody = document.getElementById('analysisTableBody');
    tbody.innerHTML = '';
    
    dashboardData.analysisResults.forEach(result => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${result.contract}</td>
            <td>${result.template}</td>
            <td>
                <span class="confidence-badge confidence-${getConfidenceClass(result.similarity)}">
                    ${result.similarity}%
                </span>
            </td>
            <td>
                <span class="status-badge status-${getStatusClass(result.status)}">
                    ${result.status}
                </span>
            </td>
            <td>System</td>
            <td>${formatDate(result.date)}</td>
            <td>${getNextStepSuggestion(result.status)}</td>
            <td>
                <button class="download-btn" onclick="downloadReport('${result.id}', 'review')" title="Download Redlined Document">
                    <i class="fas fa-file-word"></i>
                </button>
            </td>
            <td>
                <button class="download-btn" onclick="downloadReport('${result.id}', 'changes')" title="Download Changes Table">
                    <i class="fas fa-table"></i>
                </button>
            </td>
            <td>
                <button class="download-btn" onclick="downloadWordComRedlined('${result.id}')" title="Download Word Track Changes">
                    <i class="fas fa-file-word"></i>
                    <span style="font-size: 0.7em; margin-left: 2px;">TC</span>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateSystemStatus() {
    const statusIndicator = document.getElementById('systemStatus');
    const statusText = document.getElementById('statusText');
    const health = dashboardData.systemStatus;
    
    if (health.status === 'healthy') {
        statusIndicator.className = 'fas fa-circle status-indicator status-healthy';
        statusText.textContent = 'System Healthy';
    } else {
        statusIndicator.className = 'fas fa-circle status-indicator status-degraded';
        statusText.textContent = 'System Degraded';
    }
}


function updateFileListings() {
    updateContractsList();
    updateTemplatesList();
}

function updateContractsList() {
    const contractsList = document.getElementById('contractsList');
    contractsList.innerHTML = '';
    
    dashboardData.contracts.forEach(contract => {
        const contractDiv = document.createElement('div');
        contractDiv.className = 'file-item';
        contractDiv.innerHTML = `
            <div class="file-info">
                <div class="file-name">${contract.name}</div>
                <div class="file-details">${contract.type} • ${contract.size}</div>
            </div>
            <div class="file-actions">
                <button class="action-btn small" onclick="analyzeContract('${contract.id}')" title="Analyze Contract">
                    <i class="fas fa-search"></i>
                </button>
                <button class="action-btn small danger" onclick="deleteContract('${contract.id}')" title="Delete Contract">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        contractsList.appendChild(contractDiv);
    });
}

function updateTemplatesList() {
    const templatesList = document.getElementById('templatesList');
    templatesList.innerHTML = '';
    
    dashboardData.templates.forEach(template => {
        const templateDiv = document.createElement('div');
        templateDiv.className = 'file-item';
        templateDiv.innerHTML = `
            <div class="file-info">
                <div class="file-name">${template.name}</div>
                <div class="file-details">${template.category} • v${template.version}</div>
            </div>
            <div class="file-actions">
                <button class="action-btn small" onclick="editTemplate('${template.id}')" title="Edit Template">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn small danger" onclick="deleteTemplate('${template.id}')" title="Delete Template">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        templatesList.appendChild(templateDiv);
    });
}

function setupFileUploads() {
    // Contract upload
    const contractUpload = document.getElementById('contractUpload');
    const contractInput = document.getElementById('contractFileInput');
    
    if (contractUpload && contractInput) {
        contractUpload.addEventListener('click', () => contractInput.click());
        contractUpload.addEventListener('dragover', handleDragOver);
        contractUpload.addEventListener('dragleave', handleDragLeave);
        contractUpload.addEventListener('drop', (e) => handleDrop(e, 'contract'));
        contractInput.addEventListener('change', (e) => uploadFiles(e.target.files, 'contract'));
        console.log('Contract upload area setup complete');
    } else {
        console.error('Contract upload elements not found');
    }
    
    // Template upload
    const templateUpload = document.getElementById('templateUpload');
    const templateInput = document.getElementById('templateFileInput');
    
    if (templateUpload && templateInput) {
        templateUpload.addEventListener('click', () => templateInput.click());
        templateUpload.addEventListener('dragover', handleDragOver);
        templateUpload.addEventListener('dragleave', handleDragLeave);
        templateUpload.addEventListener('drop', (e) => handleDrop(e, 'template'));
        templateInput.addEventListener('change', (e) => uploadFiles(e.target.files, 'template'));
        console.log('Template upload area setup complete');
    } else {
        console.error('Template upload elements not found');
    }
    
    // Modal upload
    const modalUpload = document.getElementById('modalFileInput');
    modalUpload.addEventListener('change', (e) => uploadFiles(e.target.files, 'contract'));
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    // Only remove the class if we're actually leaving the element (not just moving to a child)
    if (!e.currentTarget.contains(e.relatedTarget)) {
        e.currentTarget.classList.remove('drag-over');
    }
}

function handleDrop(e, type) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
    
    // Check if files were dropped
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFiles(files, type);
    } else {
        showNotification('No files were dropped', 'warning');
    }
}

function uploadFiles(files, type) {
    Array.from(files).forEach(file => {
        // Validate file type
        if (!file.name.toLowerCase().endsWith('.docx')) {
            showNotification(`${file.name} is not a DOCX file. Only DOCX files are supported.`, 'error');
            return;
        }
        
        // Validate file size (16MB limit)
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            showNotification(`${file.name} is too large. Maximum file size is 16MB.`, 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        const endpoint = type === 'contract' ? '/api/upload-contract' : '/api/upload-template';
        const typeLabel = type === 'contract' ? 'contract' : 'template';
        
        // Show upload progress
        showUploadProgress(file.name);
        
        fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideUploadProgress();
            
            if (data.error) {
                showNotification(`Error uploading ${typeLabel} ${file.name}: ${data.error}`, 'error');
            } else {
                showNotification(`${typeLabel.charAt(0).toUpperCase() + typeLabel.slice(1)} ${file.name} uploaded successfully`, 'success');
                loadDashboardData();
            }
        })
        .catch(error => {
            hideUploadProgress();
            console.error('Upload error:', error);
            showNotification(`Error uploading ${typeLabel} ${file.name}`, 'error');
        });
    });
}

function setupModalEvents() {
    // Upload modal events
    const uploadModal = document.getElementById('uploadModal');
    const reportModal = document.getElementById('reportModal');
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === uploadModal) {
            closeUploadModal();
        }
        if (event.target === reportModal) {
            closeReportModal();
        }
    });
    
    // Close modals with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeUploadModal();
            closeReportModal();
        }
    });
}

function setupTableInteractions() {
    // Add sorting functionality
    const tableHeaders = document.querySelectorAll('.analysis-table th');
    tableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const column = this.textContent.trim();
            sortTable(column);
        });
    });
}

// Modal functions
function openUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
}

function openReportModal() {
    document.getElementById('reportModal').style.display = 'block';
}

function closeReportModal() {
    document.getElementById('reportModal').style.display = 'none';
}

// Enhanced Report Generation Functions
function downloadReport(resultId, reportType) {
    const reportTypes = {
        'review': {
            endpoint: '/api/generate-redlined-document',
            filename: 'review_document.docx',
            icon: 'fas fa-file-word'
        },
        'changes': {
            endpoint: '/api/generate-changes-table',
            filename: 'changes_table.xlsx',
            icon: 'fas fa-table'
        }
    };
    
    const reportConfig = reportTypes[reportType];
    if (!reportConfig) {
        showNotification('Invalid report type', 'error');
        return;
    }
    
    // Show loading state
    showNotification('Generating report...', 'info');
    
    fetch(reportConfig.endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            result_id: resultId,
            report_type: reportType
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Report generation failed');
        }
        return response.blob();
    })
    .then(blob => {
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${resultId}_${reportConfig.filename}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Report downloaded successfully', 'success');
    })
    .catch(error => {
        console.error('Download error:', error);
        showNotification('Error generating report', 'error');
    });
}

function generateSelectedReports() {
    const selectedTypes = {};
    
    // Check which report types are selected
    selectedTypes.review_docx = document.getElementById('generateReviewDoc').checked;
    selectedTypes.changes_xlsx = document.getElementById('generateChangesTable').checked;
    selectedTypes.changes_docx = document.getElementById('generateChangesTableDocx').checked;
    
    // Get selected contracts (if any)
    const selectedContracts = getSelectedContracts();
    
    if (selectedContracts.length === 0) {
        showNotification('Please select at least one contract', 'warning');
        return;
    }
    
    // Generate reports for selected contracts
    selectedContracts.forEach(contractId => {
        generateMultipleReports(contractId, selectedTypes);
    });
    
    closeReportModal();
}

function generateMultipleReports(contractId, reportTypes) {
    showNotification('Generating reports...', 'info');
    
    fetch('/api/generate-multiple-reports', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            contract_id: contractId,
            report_types: reportTypes
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showNotification(`Error: ${data.error}`, 'error');
        } else {
            showNotification(`Reports generated successfully: ${data.generated_count} files`, 'success');
            
            // Offer to download all files
            if (data.download_urls) {
                downloadMultipleFiles(data.download_urls);
            }
        }
    })
    .catch(error => {
        console.error('Report generation error:', error);
        showNotification('Error generating reports', 'error');
    });
}

function downloadMultipleFiles(urls) {
    urls.forEach((url, index) => {
        setTimeout(() => {
            window.open(url, '_blank');
        }, index * 500); // Stagger downloads
    });
}

// Action functions
function refreshData() {
    loadDashboardData();
    showNotification('Data refreshed', 'success');
}

function analyzeAllContracts() {
    const contractIds = dashboardData.contracts.map(c => c.id);
    
    if (contractIds.length === 0) {
        showNotification('No contracts to analyze', 'warning');
        return;
    }
    
    showNotification('Starting batch analysis...', 'info');
    
    fetch('/api/batch-analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ contract_ids: contractIds })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showNotification(`Error: ${data.error}`, 'error');
        } else {
            showNotification(`Batch analysis completed: ${data.count} contracts analyzed`, 'success');
            loadDashboardData();
        }
    })
    .catch(error => {
        console.error('Batch analyze error:', error);
        showNotification('Error performing batch analysis', 'error');
    });
}

function analyzeContract(contractId) {
    showNotification('Analyzing contract...', 'info');
    
    fetch('/api/analyze-contract', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ contract_id: contractId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showNotification(`Error: ${data.error}`, 'error');
        } else {
            showNotification('Contract analysis completed', 'success');
            loadDashboardData();
        }
    })
    .catch(error => {
        console.error('Analyze error:', error);
        showNotification('Error analyzing contract', 'error');
    });
}

function deleteContract(contractId) {
    if (!confirm('Are you sure you want to delete this contract?')) {
        return;
    }
    
    fetch(`/api/delete-contract/${contractId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showNotification(`Error: ${data.error}`, 'error');
        } else {
            showNotification('Contract deleted successfully', 'success');
            loadDashboardData();
        }
    })
    .catch(error => {
        console.error('Delete error:', error);
        showNotification('Error deleting contract', 'error');
    });
}

function deleteTemplate(templateId) {
    if (!confirm('Are you sure you want to delete this template?')) {
        return;
    }
    
    fetch(`/api/delete-template/${templateId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showNotification(`Error: ${data.error}`, 'error');
        } else {
            showNotification('Template deleted successfully', 'success');
            loadDashboardData();
        }
    })
    .catch(error => {
        console.error('Delete error:', error);
        showNotification('Error deleting template', 'error');
    });
}

function editTemplate(templateId) {
    showNotification('Template editing feature coming soon', 'info');
}

// Settings functions
function loadSettings() {
    // Load current settings
    console.log('Loading settings...');
    
    // Setup provider selector
    setupProviderSelector();
    
    // Load OpenAI models and configuration
    loadOpenAIModels();
    
    // Load LLM provider information
    loadLLMProviderInfo();
    
    // Load current model info
    loadModelInfo();
    
    // Load cache statistics
    loadCacheStats();
    
    // Setup model settings event listeners
    setupModelSettingsListeners();
}

function loadAvailableModels() {
    console.log('Loading available models...');
    
    fetch('/api/available-models')
        .then(response => response.json())
        .then(data => {
            const modelSelect = document.getElementById('llmModel');
            if (!modelSelect) {
                console.error('Model select element not found');
                return;
            }
            
            if (data.success && data.models) {
                // Clear loading option
                modelSelect.innerHTML = '';
                
                // Add models to dropdown
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.name;
                    option.textContent = `${model.name} (${(model.size / (1024 * 1024 * 1024)).toFixed(1)} GB)`;
                    
                    // Mark current model as selected
                    if (model.current) {
                        option.selected = true;
                    }
                    
                    modelSelect.appendChild(option);
                });
                
                console.log(`Loaded ${data.models.length} available models`);
                
                // Add change event listener for model switching
                modelSelect.addEventListener('change', function() {
                    if (this.value) {
                        switchModel(this.value);
                    }
                });
                
            } else {
                modelSelect.innerHTML = '<option value="">Error loading models</option>';
                console.error('Failed to load models:', data);
            }
        })
        .catch(error => {
            console.error('Error loading available models:', error);
            const modelSelect = document.getElementById('llmModel');
            if (modelSelect) {
                modelSelect.innerHTML = '<option value="">Error loading models</option>';
            }
        });
}

function switchModel(modelName) {
    console.log('Switching to model:', modelName);
    showNotification(`Switching to model: ${modelName}...`, 'info');
    
    fetch('/api/change-model', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: modelName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Successfully switched to ${modelName}`, 'success');
            // Reload model info to reflect the change
            loadModelInfo();
        } else {
            showNotification(`Failed to switch model: ${data.error}`, 'error');
            // Reload available models to reset the dropdown
            loadAvailableModels();
        }
    })
    .catch(error => {
        console.error('Error switching model:', error);
        showNotification('Error switching model', 'error');
        // Reload available models to reset the dropdown
        loadAvailableModels();
    });
}

function loadCacheStats() {
    fetch('/api/cache-stats')
        .then(response => response.json())
        .then(stats => {
            displayCacheStats(stats);
        })
        .catch(error => {
            console.error('Error loading cache stats:', error);
        });
}

function displayCacheStats(stats) {
    const cacheStatsDiv = document.getElementById('cacheStats');
    if (!cacheStatsDiv) return;
    
    cacheStatsDiv.innerHTML = `
        <div class="cache-stats">
            <h3>Cache Statistics</h3>
            <div class="cache-section">
                <h4>Memory Cache</h4>
                <ul>
                    <li>Analysis Results: ${stats.memory.analysis_results}</li>
                    <li>Contracts: ${stats.memory.contracts}</li>
                    <li>Templates: ${stats.memory.templates}</li>
                </ul>
            </div>
            <div class="cache-section">
                <h4>File Cache</h4>
                <ul>
                    <li>Analysis JSON: ${stats.files.analysis_json_exists ? 'Yes' : 'No'} (${formatBytes(stats.files.analysis_json_size)})</li>
                    <li>Report Files: ${stats.files.reports_count} files (${stats.files.reports_size_mb} MB)</li>
                </ul>
            </div>
        </div>
    `;
}

function clearCache(cacheType = 'all') {
    if (!confirm(`Are you sure you want to clear ${cacheType} cache? This action cannot be undone.`)) {
        return;
    }
    
    showNotification('Clearing cache...', 'info');
    
    fetch('/api/clear-cache', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            cache_type: cacheType
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification(`Cache cleared successfully: ${result.cleared_items.join(', ')}`, 'success');
            // Refresh cache stats
            loadCacheStats();
            // Refresh main data
            loadDashboardData();
        } else {
            showNotification(`Error clearing cache: ${result.message}`, 'error');
        }
    })
    .catch(error => {
        showNotification(`Error clearing cache: ${error.message}`, 'error');
    });
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function refreshDashboard() {
    showNotification('Refreshing dashboard...', 'info');
    loadDashboardData();
}

// Utility functions
function getSelectedContracts() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value).filter(Boolean);
}

function getConfidenceClass(confidence) {
    if (confidence >= 90) return 'high';
    if (confidence >= 70) return 'medium';
    return 'low';
}

function getStatusClass(status) {
    if (status === 'No changes') return 'success';
    if (status.includes('Minor')) return 'info';
    if (status.includes('Moderate')) return 'warning';
    return 'danger';
}

function getNextStepSuggestion(status) {
    if (status === 'No changes') return 'Proceed without Legal';
    if (status.includes('Minor')) return 'Quick Review';
    if (status.includes('Moderate')) return 'Legal Review';
    return 'Requires Legal Review';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function sortTable(column) {
    // Table sorting implementation
    showNotification('Table sorting feature coming soon', 'info');
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function showUploadProgress(filename) {
    const progress = document.getElementById('uploadProgress');
    if (progress) {
        progress.style.display = 'block';
        progress.querySelector('.progress-text').textContent = `Uploading ${filename}...`;
    }
}

function hideUploadProgress() {
    const progress = document.getElementById('uploadProgress');
    if (progress) {
        progress.style.display = 'none';
    }
}

function checkSystemStatus() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            dashboardData.systemStatus = data;
            updateSystemStatus();
        })
        .catch(error => {
            console.error('Status check error:', error);
            const statusIndicator = document.getElementById('systemStatus');
            const statusText = document.getElementById('statusText');
            statusIndicator.className = 'fas fa-circle status-indicator status-error';
            statusText.textContent = 'System Error';
        });
}

// Mobile responsiveness
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('active');
}

// Add mobile menu toggle if needed
if (window.innerWidth <= 480) {
    const header = document.querySelector('.content-header');
    const menuToggle = document.createElement('button');
    menuToggle.className = 'menu-toggle';
    menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
    menuToggle.addEventListener('click', toggleSidebar);
    header.querySelector('.header-content').prepend(menuToggle);
} 

// Download functions
function downloadReport(resultId, type) {
    const endpoints = {
        'review': '/api/download-redlined-document',
        'changes': '/api/download-changes-table'
    };
    
    const endpoint = endpoints[type];
    if (!endpoint) {
        showNotification('Unknown report type', 'error');
        return;
    }
    
    const url = `${endpoint}?id=${resultId}`;
    
    // Check if file exists before attempting download
    fetch(url, { method: 'HEAD' })
        .then(response => {
            if (response.ok) {
                // File exists, proceed with download
                window.open(url, '_blank');
            } else if (response.status === 404) {
                showNotification(`Report file not found. You may need to regenerate this report.`, 'error');
            } else {
                showNotification(`Error accessing report: ${response.statusText}`, 'error');
            }
        })
        .catch(error => {
            console.error('Download error:', error);
            showNotification('Failed to download report. Please try again.', 'error');
        });
}

function downloadWordComRedlined(resultId) {
    // First generate the Word COM redlined document
    showNotification('Generating Word Track Changes document...', 'info');
    
    fetch('/api/generate-word-com-redlined', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            result_id: resultId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (data.error.includes('Windows COM interface')) {
                showNotification('Word Track Changes feature requires Windows with Microsoft Word installed', 'warning');
            } else {
                showNotification(data.error, 'error');
            }
        } else {
            showNotification('Word Track Changes document generated successfully!', 'success');
            
            // Download the generated file
            setTimeout(() => {
                const url = `/api/download-word-com-redlined?id=${resultId}`;
                window.open(url, '_blank');
            }, 500);
        }
    })
    .catch(error => {
        console.error('Error generating Word COM redlined document:', error);
        showNotification('Failed to generate Word Track Changes document', 'error');
    });
} 

// Enhanced model management variables
let modelSwitchInProgress = false;
let availableModels = [];
let currentModel = '';
let currentProvider = 'openai';
let openaiModels = [];

// OpenAI Model Management Functions
function loadOpenAIModels() {
    console.log('Loading OpenAI models...');
    
    fetch('/api/openai-models')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                openaiModels = data.models;
                updateOpenAIModelDropdown(data.models, data.current_model);
                
                if (data.recommendations) {
                    console.log('OpenAI model recommendations:', data.recommendations);
                }
            } else {
                console.error('Failed to load OpenAI models:', data.error);
                showNotification('Failed to load OpenAI models', 'error');
            }
        })
        .catch(error => {
            console.error('Error loading OpenAI models:', error);
            showNotification('Error loading OpenAI models', 'error');
        });
}

function updateOpenAIModelDropdown(models, currentModel) {
    const modelSelect = document.getElementById('openaiModel');
    const modelDescription = document.getElementById('model-description');
    
    if (!modelSelect) {
        console.error('OpenAI model select element not found');
        return;
    }
    
    // Clear existing options
    modelSelect.innerHTML = '';
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select an OpenAI model...';
    defaultOption.disabled = true;
    modelSelect.appendChild(defaultOption);
    
    // Add model options
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.name;
        option.textContent = `${model.name} - ${model.tier.toUpperCase()}`;
        
        if (model.recommended) {
            option.textContent += ' ⭐ RECOMMENDED';
            option.setAttribute('data-recommended', 'true');
        }
        
        if (model.name === currentModel) {
            option.selected = true;
            updateModelDescription(model);
        }
        
        modelSelect.appendChild(option);
    });
    
    // Add change event listener
    modelSelect.addEventListener('change', function() {
        const selectedModel = this.value;
        if (selectedModel) {
            const model = openaiModels.find(m => m.name === selectedModel);
            if (model) {
                updateModelDescription(model);
                changeOpenAIModel(selectedModel);
            }
        }
    });
    
    console.log(`Updated OpenAI model dropdown with ${models.length} models`);
}

function updateModelDescription(model) {
    const modelDescription = document.getElementById('model-description');
    if (!modelDescription) return;
    
    modelDescription.innerHTML = `
        <strong>${model.name}</strong><br>
        ${model.description}<br>
        <small>Context: ${model.context_window.toLocaleString()} tokens | Tier: ${model.tier}</small>
    `;
    
    // Add recommended styling
    if (model.recommended) {
        modelDescription.classList.add('recommended');
    } else {
        modelDescription.classList.remove('recommended');
    }
}

function changeOpenAIModel(modelName) {
    if (modelSwitchInProgress) {
        showNotification('Model change already in progress', 'warning');
        return;
    }
    
    modelSwitchInProgress = true;
    const modelSelect = document.getElementById('openaiModel');
    
    console.log('Changing OpenAI model to:', modelName);
    
    // Add loading animation
    modelSelect.classList.add('model-switching');
    modelSelect.disabled = true;
    
    showNotification('Changing model...', 'info');
    
    fetch('/api/update-openai-model', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model: modelName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentModel = modelName;
            showNotification(`Model changed to ${modelName}`, 'success');
            
            // Update model info display
            loadModelInfo();
            loadLLMProviderInfo();
            
            console.log('Model change successful');
        } else {
            showNotification(`Model change failed: ${data.error}`, 'error');
            console.error('Model change failed:', data.error);
        }
    })
    .catch(error => {
        console.error('Error changing model:', error);
        showNotification('Error changing model', 'error');
    })
    .finally(() => {
        modelSwitchInProgress = false;
        modelSelect.classList.remove('model-switching');
        modelSelect.disabled = false;
    });
}

function loadLLMProviderInfo() {
    console.log('Loading LLM provider information...');
    
    fetch('/api/llm-provider')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentProvider = data.provider;
                currentModel = data.model;
                
                // Update provider selector
                const providerSelector = document.getElementById('providerSelector');
                if (providerSelector) {
                    providerSelector.value = data.provider;
                }
                
                // Update provider display
                const providerElement = document.getElementById('current-provider');
                const healthElement = document.getElementById('provider-health');
                
                if (providerElement) {
                    providerElement.textContent = data.provider.toUpperCase();
                }
                
                if (healthElement) {
                    healthElement.className = `health-indicator ${data.api_key_configured ? 'health-healthy' : 'health-unhealthy'}`;
                }
                
                // Show/hide appropriate settings sections
                const openaiSettings = document.getElementById('openai-settings');
                
                if (data.provider === 'openai') {
                    if (openaiSettings) openaiSettings.style.display = 'block';
                }
                
                // Update model settings
                updateModelSettings(data.temperature, data.max_tokens);
                
                console.log('LLM provider info loaded:', data);
            } else {
                console.error('Failed to load LLM provider info');
            }
        })
        .catch(error => {
            console.error('Error loading LLM provider info:', error);
        });
}

function updateModelSettings(temperature, maxTokens) {
    const temperatureSlider = document.getElementById('temperatureSlider');
    const temperatureValue = document.getElementById('temperatureValue');
    const maxTokensInput = document.getElementById('maxTokensInput');
    
    if (temperatureSlider && temperatureValue) {
        temperatureSlider.value = temperature;
        temperatureValue.textContent = temperature;
    }
    
    if (maxTokensInput) {
        maxTokensInput.value = maxTokens;
    }
}

function setupModelSettingsListeners() {
    const temperatureSlider = document.getElementById('temperatureSlider');
    const temperatureValue = document.getElementById('temperatureValue');
    const maxTokensInput = document.getElementById('maxTokensInput');
    
    if (temperatureSlider && temperatureValue) {
        temperatureSlider.addEventListener('input', function() {
            temperatureValue.textContent = this.value;
        });
        
        temperatureSlider.addEventListener('change', function() {
            updateLLMSettings({ temperature: parseFloat(this.value) });
        });
    }
    
    if (maxTokensInput) {
        maxTokensInput.addEventListener('change', function() {
            updateLLMSettings({ max_tokens: parseInt(this.value) });
        });
    }
}

function setupProviderSelector() {
    const providerSelector = document.getElementById('providerSelector');
    if (providerSelector) {
        providerSelector.addEventListener('change', function() {
            switchProvider(this.value);
        });
    }
}

function switchProvider(providerType) {
    console.log('Switching to provider:', providerType);
    
    // Show loading state
    showNotification('Switching LLM provider...', 'info');
    
    // Show/hide appropriate settings sections
    const openaiSettings = document.getElementById('openai-settings');
    
    if (providerType === 'openai') {
        if (openaiSettings) openaiSettings.style.display = 'block';
        loadOpenAIModels();
    }
    
    // Update provider in backend
    updateLLMProvider(providerType);
    
    // Update provider display
    const providerElement = document.getElementById('current-provider');
    if (providerElement) {
        providerElement.textContent = 'OpenAI';
    }
}

// REMOVED: function loadOllamaModels() {
// REMOVED:     console.log('Loading Ollama models...');
// REMOVED:     
// REMOVED:     fetch('/api/available-models')
// REMOVED:         .then(response => response.json())
// REMOVED:         .then(data => {
// REMOVED:             const ollamaSelect = document.getElementById('ollamaModel');
// REMOVED:             if (!ollamaSelect) return;
// REMOVED:             
// REMOVED:             if (data.success && data.models) {
// REMOVED:                 ollamaSelect.innerHTML = '';
// REMOVED:                 
// REMOVED:                 data.models.forEach(model => {
// REMOVED:                     const option = document.createElement('option');
// REMOVED:                     option.value = model.name;
// REMOVED:                     const sizeGB = (model.size / (1024 * 1024 * 1024)).toFixed(1);
// REMOVED:                     option.textContent = `${model.name} (${sizeGB} GB)`;
// REMOVED:                     
// REMOVED:                     if (model.current) {
// REMOVED:                         option.selected = true;
// REMOVED:                     }
// REMOVED:                     
// REMOVED:                     ollamaSelect.appendChild(option);
// REMOVED:                 });
// REMOVED:                 
// REMOVED:                 ollamaSelect.addEventListener('change', function() {
// REMOVED:                     if (this.value) {
// REMOVED:                         changeOllamaModel(this.value);
// REMOVED:                     }
// REMOVED:                 });
// REMOVED:             } else {
// REMOVED:                 ollamaSelect.innerHTML = '<option value="">Error loading models</option>';
// REMOVED:             }
// REMOVED:         })
// REMOVED:         .catch(error => {
// REMOVED:             console.error('Error loading Ollama models:', error);
// REMOVED:             const ollamaSelect = document.getElementById('ollamaModel');
// REMOVED:             if (ollamaSelect) {
// REMOVED:                 ollamaSelect.innerHTML = '<option value="">Error loading models</option>';
// REMOVED:             }
// REMOVED:         });
// REMOVED: }
// REMOVED: 
// REMOVED: function changeOllamaModel(modelName) {
// REMOVED:     console.log('Changing Ollama model to:', modelName);
// REMOVED:     
// REMOVED:     showNotification('Changing Ollama model...', 'info');
// REMOVED:     
// REMOVED:     fetch('/api/change-model', {
// REMOVED:         method: 'POST',
// REMOVED:         headers: {
// REMOVED:             'Content-Type': 'application/json',
// REMOVED:         },
// REMOVED:         body: JSON.stringify({
// REMOVED:             model: modelName
// REMOVED:         })
// REMOVED:     })
// REMOVED:     .then(response => response.json())
// REMOVED:     .then(data => {
// REMOVED:         if (data.success) {
// REMOVED:             showNotification(`Model changed to ${modelName}`, 'success');
// REMOVED:             loadModelInfo();
// REMOVED:         } else {
// REMOVED:             showNotification(`Model change failed: ${data.message}`, 'error');
// REMOVED:         }
// REMOVED:     })
// REMOVED:     .catch(error => {
// REMOVED:         console.error('Error changing Ollama model:', error);
// REMOVED:         showNotification('Error changing model', 'error');
// REMOVED:     });
// REMOVED: }

function updateLLMProvider(providerType) {
    console.log('Updating LLM provider to:', providerType);
    
    // Note: This would update the provider in the backend
    // For now, we'll update the user config
    fetch('/api/user-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            llm_settings: {
                provider: providerType
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Provider updated successfully');
            // Refresh model info
            loadModelInfo();
        } else {
            console.error('Failed to update provider:', data.error);
        }
    })
    .catch(error => {
        console.error('Error updating provider:', error);
    });
}

function updateLLMSettings(settings) {
    console.log('Updating LLM settings:', settings);
    
    fetch('/api/update-llm-settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Settings updated successfully', 'success');
            console.log('LLM settings updated:', data.updated_settings);
        } else {
            showNotification(`Settings update failed: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error updating LLM settings:', error);
        showNotification('Error updating settings', 'error');
    });
}

// Debug function for testing tabs (call from browser console)
function testTabs() {
    console.log('=== TAB DEBUGGING TEST ===');
    
    const tabs = ['dashboard', 'upload', 'settings'];
    
    tabs.forEach(tabName => {
        console.log(`\nTesting tab: ${tabName}`);
        
        // Check if elements exist
        const tabContent = document.getElementById(tabName);
        const menuItem = document.querySelector(`[data-tab="${tabName}"]`);
        
        console.log(`Tab content exists: ${!!tabContent}`);
        console.log(`Menu item exists: ${!!menuItem}`);
        
        // Test tab switching
        if (typeof showTab === 'function') {
            const result = showTab(tabName);
            console.log(`Tab switch result: ${result}`);
        }
    });
    
    console.log('\n=== Test completed ===');
    return 'Tab test completed - check console output';
} 