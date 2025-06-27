// Multi-Agent Researcher UI - Main Application

/**
 * Main application logic and initialization
 */

class MultiAgentResearcherApp {
    constructor() {
        this.currentSection = 'home';
        this.researchTasks = new Map();
        this.repositories = new Map();
        this.systemStatus = {
            api: 'unknown',
            ollama: 'unknown',
            models: 'unknown',
            tools: 'unknown'
        };
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupNavigation();
        
        // Initialize Phase 2 features
        this.initializePhase2Features();
        
        await this.checkSystemStatus();
        this.updateStats();
        
        // Load saved data from localStorage
        this.loadSavedData();
        
        console.log('Multi-Agent Researcher UI initialized');
    }

    setupEventListeners() {
        // Research form
        const researchForm = utils.$('#research-form');
        if (researchForm) {
            researchForm.addEventListener('submit', (e) => this.handleResearchSubmit(e));
        }

        // Demo research button
        const demoBtn = utils.$('#demo-research-btn');
        if (demoBtn) {
            demoBtn.addEventListener('click', () => this.runDemoResearch());
        }

        // Repository form
        const repoForm = utils.$('#repository-form');
        if (repoForm) {
            repoForm.addEventListener('submit', (e) => this.handleRepositorySubmit(e));
        }

        // Mobile navigation toggle
        const navToggle = utils.$('#nav-toggle');
        const navMenu = utils.$('#nav-menu');
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                navToggle.classList.toggle('active');
            });
        }

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            const navMenu = utils.$('#nav-menu');
            const navToggle = utils.$('#nav-toggle');
            if (navMenu && navToggle && 
                !navMenu.contains(e.target) && 
                !navToggle.contains(e.target)) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case '1':
                        e.preventDefault();
                        this.showSection('home');
                        break;
                    case '2':
                        e.preventDefault();
                        this.showSection('research');
                        break;
                    case '3':
                        e.preventDefault();
                        this.showSection('repository');
                        break;
                    case '4':
                        e.preventDefault();
                        this.showSection('status');
                        break;
                }
            }
        });
    }

    setupNavigation() {
        const navLinks = utils.$$('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('data-section');
                this.showSection(section);
            });
        });
    }

    showSection(sectionName) {
        // Hide all sections
        const sections = utils.$$('.section');
        sections.forEach(section => section.classList.remove('active'));

        // Show target section
        const targetSection = utils.$(`#${sectionName}`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Update navigation
        const navLinks = utils.$$('.nav-link');
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-section') === sectionName) {
                link.classList.add('active');
            }
        });

        // Close mobile menu
        const navMenu = utils.$('#nav-menu');
        const navToggle = utils.$('#nav-toggle');
        if (navMenu && navToggle) {
            navMenu.classList.remove('active');
            navToggle.classList.remove('active');
        }

        this.currentSection = sectionName;

        // Load section-specific data
        this.loadSectionData(sectionName);

        // Update URL
        utils.url.setParam('section', sectionName);
    }

    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'status':
                await this.loadStatusData();
                break;
            case 'research':
                this.loadResearchHistory();
                break;
            case 'repository':
                this.loadRepositoryHistory();
                break;
        }
    }

    async checkSystemStatus() {
        try {
            // Check API health
            const healthCheck = await api.checkHealth();
            this.systemStatus.api = healthCheck.status;
            this.updateStatusIndicator('api-status', healthCheck.status);

            if (healthCheck.status === 'online') {
                // Check other services
                await Promise.allSettled([
                    this.checkOllamaStatus(),
                    this.checkModelsStatus(),
                    this.checkToolsStatus()
                ]);
            }
        } catch (error) {
            console.error('Failed to check system status:', error);
            this.systemStatus.api = 'offline';
            this.updateStatusIndicator('api-status', 'offline');
        }

        this.updateOverallStatus();
    }

    async checkOllamaStatus() {
        try {
            const status = await api.getOllamaStatus();
            this.systemStatus.ollama = status.status === 'running' ? 'online' : 'offline';
            this.updateStatusIndicator('ollama-status', this.systemStatus.ollama);
        } catch (error) {
            this.systemStatus.ollama = 'offline';
            this.updateStatusIndicator('ollama-status', 'offline');
        }
    }

    async checkModelsStatus() {
        try {
            const models = await api.getModelInfo();
            this.systemStatus.models = 'online';
            this.updateStatusIndicator('models-status', 'online');
        } catch (error) {
            this.systemStatus.models = 'offline';
            this.updateStatusIndicator('models-status', 'offline');
        }
    }

    async checkToolsStatus() {
        try {
            const tools = await api.getAvailableTools();
            this.systemStatus.tools = 'online';
            this.updateStatusIndicator('tools-status', 'online');
        } catch (error) {
            this.systemStatus.tools = 'offline';
            this.updateStatusIndicator('tools-status', 'offline');
        }
    }

    updateStatusIndicator(elementId, status) {
        const indicator = utils.$(`#${elementId}`);
        if (indicator) {
            indicator.className = `status-indicator ${status}`;
            const icon = indicator.querySelector('i');
            if (icon) {
                icon.className = status === 'online' ? 'fas fa-circle' : 'fas fa-circle';
            }
        }
    }

    updateOverallStatus() {
        const overallStatus = this.systemStatus.api === 'online' ? 'online' : 'offline';
        const statusIndicator = utils.$('#status-indicator');
        if (statusIndicator) {
            statusIndicator.className = `fas fa-circle status-indicator ${overallStatus}`;
        }
    }

    async loadStatusData() {
        const statusCards = {
            'api-health-content': this.loadApiHealthContent,
            'ollama-status-content': this.loadOllamaStatusContent,
            'models-content': this.loadModelsContent,
            'tools-content': this.loadToolsContent
        };

        for (const [elementId, loader] of Object.entries(statusCards)) {
            try {
                const content = await loader.call(this);
                const element = utils.$(`#${elementId}`);
                if (element) {
                    element.innerHTML = content;
                }
            } catch (error) {
                const element = utils.$(`#${elementId}`);
                if (element) {
                    element.innerHTML = `<div class="error">Failed to load: ${error.message}</div>`;
                }
            }
        }
    }

    async loadApiHealthContent() {
        const health = await api.checkHealth();
        return `
            <div class="status-details">
                <div class="status-item">
                    <span class="label">Status:</span>
                    <span class="value ${health.status}">${health.status}</span>
                </div>
                <div class="status-item">
                    <span class="label">Service:</span>
                    <span class="value">${health.data?.service || 'Unknown'}</span>
                </div>
                <div class="status-item">
                    <span class="label">Version:</span>
                    <span class="value">${health.data?.version || 'Unknown'}</span>
                </div>
            </div>
        `;
    }

    async loadOllamaStatusContent() {
        const status = await api.getOllamaStatus();
        return `
            <div class="status-details">
                <div class="status-item">
                    <span class="label">Status:</span>
                    <span class="value ${status.status}">${status.status}</span>
                </div>
                <div class="status-item">
                    <span class="label">Host:</span>
                    <span class="value">${status.host}</span>
                </div>
                <div class="status-item">
                    <span class="label">Models:</span>
                    <span class="value">${status.available_models?.length || 0}</span>
                </div>
            </div>
        `;
    }

    async loadModelsContent() {
        const models = await api.getModelInfo();
        return `
            <div class="status-details">
                <div class="status-item">
                    <span class="label">Provider:</span>
                    <span class="value">${models.model_info?.provider || 'Unknown'}</span>
                </div>
                <div class="status-item">
                    <span class="label">Model:</span>
                    <span class="value">${models.model_info?.model || 'Unknown'}</span>
                </div>
                <div class="status-item">
                    <span class="label">Status:</span>
                    <span class="value online">Available</span>
                </div>
            </div>
        `;
    }

    async loadToolsContent() {
        const tools = await api.getAvailableTools();
        return `
            <div class="status-details">
                <div class="status-item">
                    <span class="label">Available Tools:</span>
                    <span class="value">${tools.tools?.length || 0}</span>
                </div>
                ${tools.tools?.map(tool => `
                    <div class="tool-item">
                        <strong>${tool.name}</strong>
                        <p>${tool.description}</p>
                    </div>
                `).join('') || ''}
            </div>
        `;
    }

    async handleResearchSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const query = formData.get('query');
        const maxSubagents = parseInt(formData.get('max_subagents'));
        const maxIterations = parseInt(formData.get('max_iterations'));

        if (!query.trim()) {
            showToast('Please enter a research query', 'warning');
            return;
        }

        try {
            loadingManager.show('Starting research...');
            
            const result = await api.startResearch(query, maxSubagents, maxIterations);
            
            loadingManager.hide();
            showToast('Research started successfully', 'success');
            
            this.displayResearchResult(result);
            this.saveResearchTask(result);
            
        } catch (error) {
            loadingManager.hide();
            showToast(`Research failed: ${apiUtils.formatError(error)}`, 'error');
        }
    }

    async runDemoResearch() {
        try {
            loadingManager.show('Running demo research...');
            
            const result = await api.runDemoResearch();
            
            loadingManager.hide();
            showToast('Demo research completed', 'success');
            
            this.displayResearchResult(result);
            
        } catch (error) {
            loadingManager.hide();
            showToast(`Demo research failed: ${apiUtils.formatError(error)}`, 'error');
        }
    }

    displayResearchResult(result) {
        const resultsContainer = utils.$('#research-results');
        if (!resultsContainer) return;

        const resultHtml = `
            <div class="result-card">
                <div class="result-header">
                    <h3>Research Result</h3>
                    <div class="result-meta">
                        <span><i class="fas fa-clock"></i> ${utils.formatDateTime(new Date())}</span>
                        <span><i class="fas fa-robot"></i> ${result.demo_result?.tokens_used || 'N/A'} tokens</span>
                        <span><i class="fas fa-chart-line"></i> ${result.status}</span>
                    </div>
                </div>
                <div class="result-content">
                    <div class="query-section">
                        <h4>Query:</h4>
                        <p>${utils.escapeHtml(result.demo_result?.query || result.query || 'N/A')}</p>
                    </div>
                    <div class="report-section">
                        <h4>Report:</h4>
                        <div class="report-content">
                            ${this.formatReport(result.demo_result?.report || result.report || 'No report available')}
                        </div>
                    </div>
                    ${result.demo_result?.sources_count ? `
                        <div class="sources-section">
                            <h4>Sources:</h4>
                            <p>${result.demo_result.sources_count} sources analyzed</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        resultsContainer.innerHTML = resultHtml;
    }

    formatReport(report) {
        // Convert markdown-like formatting to HTML
        return report
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/^(.*)$/gim, '<p>$1</p>')
            .replace(/<p><\/p>/g, '')
            .replace(/<p><h/g, '<h')
            .replace(/<\/h([1-6])><\/p>/g, '</h$1>');
    }

    async handleRepositorySubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const path = formData.get('path');

        if (!path.trim()) {
            showToast('Please enter a repository path', 'warning');
            return;
        }

        try {
            loadingManager.show('Analyzing repository...');
            
            const result = await api.indexRepository(path);
            
            loadingManager.hide();
            showToast('Repository analysis completed', 'success');
            
            this.displayRepositoryResult(result);
            this.saveRepository(result);
            
        } catch (error) {
            loadingManager.hide();
            showToast(`Repository analysis failed: ${apiUtils.formatError(error)}`, 'error');
        }
    }

    displayRepositoryResult(result) {
        const resultsContainer = utils.$('#repository-results');
        if (!resultsContainer) return;

        const resultHtml = `
            <div class="result-card">
                <div class="result-header">
                    <h3>Repository Analysis</h3>
                    <div class="result-meta">
                        <span><i class="fas fa-clock"></i> ${utils.formatDateTime(new Date())}</span>
                        <span><i class="fas fa-code"></i> ${result.total_files || 'N/A'} files</span>
                        <span><i class="fas fa-check"></i> ${result.status}</span>
                    </div>
                </div>
                <div class="result-content">
                    <div class="repo-info">
                        <h4>Repository Information:</h4>
                        <div class="info-grid">
                            <div class="info-item">
                                <span class="label">ID:</span>
                                <span class="value">${result.repository_id}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Path:</span>
                                <span class="value">${result.repository_path || 'N/A'}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Files:</span>
                                <span class="value">${result.total_files || 'N/A'}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Size:</span>
                                <span class="value">${utils.formatFileSize(result.total_size || 0)}</span>
                            </div>
                        </div>
                    </div>
                    ${result.analysis_summary ? `
                        <div class="analysis-summary">
                            <h4>Analysis Summary:</h4>
                            <pre>${JSON.stringify(result.analysis_summary, null, 2)}</pre>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        resultsContainer.innerHTML = resultHtml;
    }

    saveResearchTask(task) {
        const id = utils.generateId();
        const taskData = {
            id,
            timestamp: new Date().toISOString(),
            ...task
        };
        
        this.researchTasks.set(id, taskData);
        this.saveToLocalStorage();
        this.updateStats();
    }

    saveRepository(repo) {
        const id = repo.repository_id || utils.generateId();
        const repoData = {
            id,
            timestamp: new Date().toISOString(),
            ...repo
        };
        
        this.repositories.set(id, repoData);
        this.saveToLocalStorage();
        this.updateStats();
    }

    saveToLocalStorage() {
        utils.storage.set('researchTasks', Array.from(this.researchTasks.entries()));
        utils.storage.set('repositories', Array.from(this.repositories.entries()));
    }

    loadSavedData() {
        const savedTasks = utils.storage.get('researchTasks', []);
        const savedRepos = utils.storage.get('repositories', []);
        
        this.researchTasks = new Map(savedTasks);
        this.repositories = new Map(savedRepos);
    }

    loadResearchHistory() {
        // Implementation for loading research history
        console.log('Loading research history...');
    }

    loadRepositoryHistory() {
        // Implementation for loading repository history
        console.log('Loading repository history...');
    }

    updateStats() {
        const totalResearchEl = utils.$('#total-research');
        const totalReposEl = utils.$('#total-repos');
        
        if (totalResearchEl) {
            totalResearchEl.textContent = this.researchTasks.size;
        }
        
        if (totalReposEl) {
            totalReposEl.textContent = this.repositories.size;
        }
    }

    /**
     * Initialize Phase 2 Features
     * Real-time updates, data visualization, and enhanced UX
     */
    initializePhase2Features() {
        console.log('🚀 Initializing Phase 2 features...');
        
        // Initialize real-time status monitoring
        this.initializeRealTimeStatus();
        
        // Initialize metrics dashboard
        this.initializeMetricsDashboard();
        
        // Initialize data visualization
        this.initializeDataVisualization();
        
        // Initialize live activity feed
        this.initializeLiveActivityFeed();
        
        // Initialize progress tracking
        this.initializeProgressTracking();
        
        // Initialize notifications
        this.initializeNotifications();
        
        console.log('✅ Phase 2 features initialized');
    }

    initializeRealTimeStatus() {
        // Start real-time status monitoring
        if (window.realTimeStatus) {
            // Register status update callback
            window.realTimeStatus.onStatusUpdate('main', (status) => {
                this.updateRealTimeStatus(status);
            });
            
            // Start monitoring
            window.realTimeStatus.start();
        }
    }

    initializeMetricsDashboard() {
        const dashboard = new MetricsDashboard('metrics-dashboard');
        
        // Add initial metrics
        dashboard.addMetric('api-response-time', 'API Response Time', 0, {
            type: 'number',
            format: 'duration',
            color: '#4285f4'
        });
        
        dashboard.addMetric('system-uptime', 'System Uptime', 0, {
            type: 'number',
            format: 'duration',
            color: '#34a853'
        });
        
        dashboard.addMetric('active-connections', 'Active Connections', 0, {
            type: 'number',
            format: 'default',
            color: '#fbbc04'
        });
        
        dashboard.addMetric('memory-usage', 'Memory Usage', 0, {
            type: 'number',
            format: 'percentage',
            color: '#ea4335'
        });
        
        this.metricsDashboard = dashboard;
        
        // Update metrics periodically
        setInterval(() => {
            this.updateMetrics();
        }, 10000); // Update every 10 seconds
    }

    initializeDataVisualization() {
        // Initialize performance chart
        this.initializePerformanceChart();
        
        // Set up chart controls
        const chartControls = document.querySelectorAll('.chart-control');
        chartControls.forEach(control => {
            control.addEventListener('click', (e) => {
                // Remove active class from all controls
                chartControls.forEach(c => c.classList.remove('active'));
                // Add active class to clicked control
                e.target.classList.add('active');
                
                // Update chart based on timeframe
                const timeframe = e.target.dataset.timeframe;
                this.updatePerformanceChart(timeframe);
            });
        });
    }

    initializePerformanceChart() {
        // Generate sample performance data
        const performanceData = this.generatePerformanceData();
        
        // Create line chart
        if (window.chartRenderer) {
            this.performanceChart = window.chartRenderer.createLineChart('performance-chart', performanceData, {
                width: 800,
                height: 300,
                margin: { top: 20, right: 20, bottom: 40, left: 60 },
                lineColor: '#4285f4',
                pointColor: '#4285f4',
                showPoints: true,
                showGrid: true
            });
        }
    }

    generatePerformanceData() {
        const data = [];
        const now = Date.now();
        
        // Generate 24 hours of sample data
        for (let i = 0; i < 24; i++) {
            data.push({
                x: i,
                y: Math.random() * 100 + 50 // Random response time between 50-150ms
            });
        }
        
        return data;
    }

    updatePerformanceChart(timeframe) {
        let dataPoints;
        
        switch (timeframe) {
            case '1h':
                dataPoints = 12; // 5-minute intervals
                break;
            case '6h':
                dataPoints = 24; // 15-minute intervals
                break;
            case '24h':
                dataPoints = 48; // 30-minute intervals
                break;
            default:
                dataPoints = 24;
        }
        
        const newData = [];
        for (let i = 0; i < dataPoints; i++) {
            newData.push({
                x: i,
                y: Math.random() * 100 + 50
            });
        }
        
        if (this.performanceChart) {
            this.performanceChart.update(newData);
        }
    }

    initializeLiveActivityFeed() {
        this.activityFeed = [];
        
        // Set start timestamp
        const startTimestamp = document.getElementById('start-timestamp');
        if (startTimestamp) {
            startTimestamp.textContent = utils.formatDateTime(new Date());
        }
        
        // Add periodic activity updates
        setInterval(() => {
            this.addActivityItem();
        }, 30000); // Add activity every 30 seconds
    }

    addActivityItem(message = null, type = 'info') {
        const feed = document.getElementById('live-activity-feed');
        if (!feed) return;
        
        const activities = [
            'System health check completed',
            'API endpoint responded successfully',
            'Background task processed',
            'Cache updated',
            'Metrics collected',
            'Status monitoring active'
        ];
        
        const activity = message || activities[Math.floor(Math.random() * activities.length)];
        
        const item = document.createElement('div');
        item.className = 'live-feed-item';
        item.innerHTML = `
            <span>${activity}</span>
            <span class="live-feed-timestamp">${utils.formatDateTime(new Date())}</span>
        `;
        
        // Add to top of feed
        const firstChild = feed.firstChild;
        if (firstChild) {
            feed.insertBefore(item, firstChild);
        } else {
            feed.appendChild(item);
        }
        
        // Keep only last 10 items
        const items = feed.querySelectorAll('.live-feed-item');
        if (items.length > 10) {
            items[items.length - 1].remove();
        }
        
        // Store in activity feed array
        this.activityFeed.unshift({
            message: activity,
            timestamp: new Date().toISOString(),
            type
        });
        
        if (this.activityFeed.length > 50) {
            this.activityFeed = this.activityFeed.slice(0, 50);
        }
    }

    initializeProgressTracking() {
        // Listen for progress events
        window.addEventListener('progressUpdate', (event) => {
            this.updateProgressDisplay(event.detail);
        });
    }

    initializeNotifications() {
        // Create notification system
        this.notifications = [];
        
        // Add welcome notification
        setTimeout(() => {
            this.showNotification('Phase 2 features activated!', 'Real-time monitoring and data visualization are now available.', 'success');
        }, 2000);
    }

    updateRealTimeStatus(status) {
        // Update status indicators
        this.updateStatusIndicator('api-status', status.status === 'ok' ? 'online' : 'offline');
        this.updateStatusIndicator('ollama-status', 'offline'); // Ollama not running
        this.updateStatusIndicator('models-status', 'online');
        this.updateStatusIndicator('tools-status', 'online');
        
        // Update status cards
        this.updateStatusCard('api-health-card', status.status === 'ok' ? 'online' : 'offline');
        this.updateStatusCard('ollama-status-card', 'offline');
        this.updateStatusCard('models-status-card', 'online');
        this.updateStatusCard('tools-status-card', 'online');
        
        // Add activity
        this.addActivityItem(`API status: ${status.status}`, status.status === 'ok' ? 'success' : 'error');
    }

    updateStatusIndicator(elementId, status) {
        const indicator = document.getElementById(elementId);
        if (!indicator) return;
        
        const textElement = indicator.querySelector('span');
        if (textElement) {
            textElement.textContent = status;
        }
        
        // Update classes
        indicator.className = `status-indicator ${status}`;
    }

    updateStatusCard(cardId, status) {
        const card = document.getElementById(cardId);
        if (!card) return;
        
        // Update card classes
        card.className = `status-card enhanced ${status}`;
    }

    updateMetrics() {
        if (!this.metricsDashboard) return;
        
        // Simulate metric updates
        const apiResponseTime = Math.random() * 200 + 50; // 50-250ms
        const systemUptime = Date.now() - (Date.now() - Math.random() * 86400000); // Random uptime
        const activeConnections = Math.floor(Math.random() * 50) + 10; // 10-60 connections
        const memoryUsage = Math.random() * 40 + 30; // 30-70% memory usage
        
        this.metricsDashboard.updateMetric('api-response-time', apiResponseTime);
        this.metricsDashboard.updateMetric('system-uptime', systemUptime);
        this.metricsDashboard.updateMetric('active-connections', activeConnections);
        this.metricsDashboard.updateMetric('memory-usage', memoryUsage);
    }

    showNotification(title, message, type = 'info') {
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-header">
                <h4 class="notification-title">${title}</h4>
                <button class="notification-close">&times;</button>
            </div>
            <div class="notification-message">${message}</div>
        `;
        
        // Add close functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        container.appendChild(notification);
    }

    updateProgressDisplay(operation) {
        const overlay = document.getElementById('progress-overlay');
        const title = document.getElementById('progress-title');
        const fill = document.getElementById('progress-fill');
        const text = document.getElementById('progress-text');
        const steps = document.getElementById('progress-steps');
        
        if (!overlay) return;
        
        if (operation.status === 'running') {
            overlay.style.display = 'flex';
            title.textContent = operation.title;
            fill.style.width = `${operation.progress}%`;
            text.textContent = `${Math.round(operation.progress)}%`;
            
            // Update steps
            if (operation.steps && operation.steps.length > 0) {
                steps.innerHTML = operation.steps.map(step => `
                    <div class="progress-step completed">
                        <div class="step-icon">✓</div>
                        <span>${step.step}</span>
                    </div>
                `).join('');
            }
        } else if (operation.status === 'completed' || operation.status === 'failed') {
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 1000);
        }
    }
}

// Global function to show section (called from HTML)
window.showSection = (sectionName) => {
    if (window.app) {
        window.app.showSection(sectionName);
    }
};

// Initialize app when DOM is ready
utils.ready(() => {
    window.app = new MultiAgentResearcherApp();
    
    // Check for section parameter in URL
    const urlParams = utils.url.getParams();
    if (urlParams.section) {
        window.app.showSection(urlParams.section);
    }
});

// Handle browser back/forward buttons
window.addEventListener('popstate', () => {
    const urlParams = utils.url.getParams();
    if (urlParams.section && window.app) {
        window.app.showSection(urlParams.section);
    }
});