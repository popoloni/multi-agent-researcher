// Multi-Agent Researcher UI - API Communication

/**
 * API communication module for the Multi-Agent Researcher UI
 */

class APIClient {
    constructor(baseURL = 'http://localhost:12000') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // GET request
    async get(endpoint, params = {}) {
        const url = new URL(`${this.baseURL}${endpoint}`);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });

        return this.request(url.pathname + url.search, {
            method: 'GET'
        });
    }

    // POST request
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }

    // Health check
    async checkHealth() {
        try {
            const response = await this.get('/health');
            return {
                status: 'online',
                data: response
            };
        } catch (error) {
            return {
                status: 'offline',
                error: error.message
            };
        }
    }

    // Research API methods
    async startResearch(query, maxSubagents = 3, maxIterations = 2) {
        return this.post('/research/start', {
            query,
            max_subagents: maxSubagents,
            max_iterations: maxIterations
        });
    }

    async getResearchStatus(researchId) {
        return this.get(`/research/${researchId}/status`);
    }

    async getResearchResult(researchId) {
        return this.get(`/research/${researchId}/result`);
    }

    async runDemoResearch() {
        return this.post('/research/demo');
    }

    async testCitations() {
        return this.post('/research/test-citations');
    }

    // Repository API methods
    async indexRepository(path) {
        return this.post('/kenobi/repositories/index', { path });
    }

    async getRepositoryAnalysis(repositoryId) {
        return this.get(`/kenobi/repositories/${repositoryId}/analysis`);
    }

    async searchCode(query, repositoryId, filters = {}) {
        return this.post('/kenobi/search/code', {
            query,
            repository_id: repositoryId,
            filters
        });
    }

    async analyzeFile(filePath, repositoryId) {
        return this.post('/kenobi/analyze/file', {
            file_path: filePath,
            repository_id: repositoryId
        });
    }

    async getRepositoryInsights(repositoryId) {
        return this.get(`/kenobi/repositories/${repositoryId}/insights`);
    }

    async compareRepositories(repositoryIds) {
        return this.post('/kenobi/analysis/compare-repositories', {
            repository_ids: repositoryIds
        });
    }

    async batchAnalyzeRepositories(repositoryPaths) {
        return this.post('/kenobi/repositories/batch-analysis', {
            repository_paths: repositoryPaths
        });
    }

    // Dashboard API methods
    async getDashboardOverview() {
        return this.get('/kenobi/dashboard/overview');
    }

    async getRepositoryDashboard(repositoryId) {
        return this.get(`/kenobi/dashboard/repository/${repositoryId}`);
    }

    async getQualityDashboard() {
        return this.get('/kenobi/dashboard/quality');
    }

    async getRealTimeDashboard() {
        return this.get('/kenobi/dashboard/real-time');
    }

    // Analytics API methods
    async getAnalyticsMetrics() {
        return this.get('/kenobi/analytics/metrics');
    }

    async getRealTimeAnalytics() {
        return this.get('/kenobi/analytics/real-time');
    }

    async getRepositoryTrends(repositoryId) {
        return this.get(`/kenobi/analytics/repository-trends/${repositoryId}`);
    }

    async getSystemPerformance() {
        return this.get('/kenobi/analytics/system-performance');
    }

    // Cache API methods
    async getCacheStats() {
        return this.get('/kenobi/cache/stats');
    }

    async clearCache() {
        return this.post('/kenobi/cache/clear');
    }

    // Monitoring API methods
    async startMonitoring(repositoryIds) {
        return this.post('/kenobi/monitoring/start', {
            repository_ids: repositoryIds
        });
    }

    async stopMonitoring() {
        return this.post('/kenobi/monitoring/stop');
    }

    async getMonitoringStatus() {
        return this.get('/kenobi/monitoring/status');
    }

    // System API methods
    async getAvailableTools() {
        return this.get('/tools/available');
    }

    async getModelInfo() {
        return this.get('/models/info');
    }

    async getOllamaStatus() {
        return this.get('/ollama/status');
    }

    async getKenobiStatus() {
        return this.get('/kenobi/status');
    }

    // Quality API methods
    async getRepositoryQuality(repositoryId) {
        return this.get(`/kenobi/quality/repository/${repositoryId}`);
    }

    async getFileQuality(filePath, repositoryId) {
        return this.post('/kenobi/quality/file', {
            file_path: filePath,
            repository_id: repositoryId
        });
    }

    async getQualityTrends(repositoryId) {
        return this.get(`/kenobi/quality/trends/${repositoryId}`);
    }

    async getQualityReport(repositoryId) {
        return this.get(`/kenobi/quality/report/${repositoryId}`);
    }

    // Search API methods
    async semanticSearch(query, repositoryId, limit = 10) {
        return this.post('/kenobi/search/semantic', {
            query,
            repository_id: repositoryId,
            limit
        });
    }

    async searchPatterns(pattern, repositoryId) {
        return this.post('/kenobi/search/patterns', {
            pattern,
            repository_id: repositoryId
        });
    }

    async findSimilarCode(codeSnippet, repositoryId) {
        return this.post('/kenobi/search/similar', {
            code_snippet: codeSnippet,
            repository_id: repositoryId
        });
    }

    async crossRepositorySearch(query, repositoryIds) {
        return this.post('/kenobi/search/cross-repository', {
            query,
            repository_ids: repositoryIds
        });
    }

    // Dependency API methods
    async getRepositoryDependencies(repositoryId) {
        return this.get(`/kenobi/repositories/${repositoryId}/dependencies`);
    }

    async analyzeDependencyHealth(repositoryId) {
        return this.get(`/kenobi/analysis/dependency-health/${repositoryId}`);
    }

    async getCrossDependencies(repositoryIds) {
        return this.post('/kenobi/analysis/cross-repository-dependencies', {
            repository_ids: repositoryIds
        });
    }

    async getDependencyGraph(repositoryId) {
        return this.get(`/kenobi/dependencies/graph/${repositoryId}`);
    }
}

// Create global API client instance
const api = new APIClient();

// Export for use in other modules
window.api = api;

// Utility functions for common API patterns
window.apiUtils = {
    // Retry mechanism for failed requests
    async retry(apiCall, maxRetries = 3, delay = 1000) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await apiCall();
            } catch (error) {
                if (i === maxRetries - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
            }
        }
    },

    // Batch requests with concurrency limit
    async batchRequests(requests, concurrency = 5) {
        const results = [];
        for (let i = 0; i < requests.length; i += concurrency) {
            const batch = requests.slice(i, i + concurrency);
            const batchResults = await Promise.allSettled(batch);
            results.push(...batchResults);
        }
        return results;
    },

    // Poll for status updates
    async pollStatus(statusCheck, interval = 2000, maxAttempts = 30) {
        for (let i = 0; i < maxAttempts; i++) {
            try {
                const status = await statusCheck();
                if (status.completed || status.error) {
                    return status;
                }
                await new Promise(resolve => setTimeout(resolve, interval));
            } catch (error) {
                if (i === maxAttempts - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, interval));
            }
        }
        throw new Error('Polling timeout exceeded');
    },

    // Format API errors for display
    formatError(error) {
        if (typeof error === 'string') {
            return error;
        }
        
        if (error.message) {
            return error.message;
        }
        
        if (error.detail) {
            return error.detail;
        }
        
        return 'An unexpected error occurred';
    }
};