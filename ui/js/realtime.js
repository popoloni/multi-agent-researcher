/**
 * Real-time Status Updates Module
 * Handles WebSocket connections and periodic status polling
 */

class RealTimeStatusManager {
    constructor() {
        this.pollInterval = null;
        this.pollFrequency = 5000; // 5 seconds
        this.isPolling = false;
        this.statusCallbacks = new Map();
        this.lastStatus = {};
    }

    /**
     * Start real-time status monitoring
     */
    start() {
        if (this.isPolling) return;
        
        this.isPolling = true;
        this.pollStatus();
        this.pollInterval = setInterval(() => this.pollStatus(), this.pollFrequency);
        
        console.log('🔄 Real-time status monitoring started');
    }

    /**
     * Stop real-time status monitoring
     */
    stop() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
        this.isPolling = false;
        
        console.log('⏹️ Real-time status monitoring stopped');
    }

    /**
     * Register callback for status updates
     */
    onStatusUpdate(component, callback) {
        this.statusCallbacks.set(component, callback);
    }

    /**
     * Unregister callback for status updates
     */
    offStatusUpdate(component) {
        this.statusCallbacks.delete(component);
    }

    /**
     * Poll system status from API
     */
    async pollStatus() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            const status = await response.json();
            
            // Check if status has changed
            if (JSON.stringify(status) !== JSON.stringify(this.lastStatus)) {
                this.lastStatus = status;
                this.notifyStatusUpdate(status);
            }
            
        } catch (error) {
            console.warn('Status polling failed:', error);
            
            // Notify offline status
            const offlineStatus = {
                status: 'offline',
                timestamp: new Date().toISOString(),
                error: error.message
            };
            
            if (JSON.stringify(offlineStatus) !== JSON.stringify(this.lastStatus)) {
                this.lastStatus = offlineStatus;
                this.notifyStatusUpdate(offlineStatus);
            }
        }
    }

    /**
     * Notify all registered callbacks of status update
     */
    notifyStatusUpdate(status) {
        this.statusCallbacks.forEach((callback, component) => {
            try {
                callback(status);
            } catch (error) {
                console.error(`Error in status callback for ${component}:`, error);
            }
        });
    }

    /**
     * Get current status
     */
    getCurrentStatus() {
        return this.lastStatus;
    }

    /**
     * Set polling frequency
     */
    setPollFrequency(frequency) {
        this.pollFrequency = frequency;
        
        if (this.isPolling) {
            this.stop();
            this.start();
        }
    }
}

// Global instance
window.realTimeStatus = new RealTimeStatusManager();

/**
 * Progress Tracking for Long Operations
 */
class ProgressTracker {
    constructor() {
        this.activeOperations = new Map();
    }

    /**
     * Start tracking an operation
     */
    startOperation(operationId, title, estimatedDuration = null) {
        const operation = {
            id: operationId,
            title,
            startTime: Date.now(),
            estimatedDuration,
            progress: 0,
            status: 'running',
            steps: []
        };
        
        this.activeOperations.set(operationId, operation);
        this.notifyProgressUpdate(operation);
        
        return operation;
    }

    /**
     * Update operation progress
     */
    updateProgress(operationId, progress, currentStep = null) {
        const operation = this.activeOperations.get(operationId);
        if (!operation) return;
        
        operation.progress = Math.min(100, Math.max(0, progress));
        operation.lastUpdate = Date.now();
        
        if (currentStep) {
            operation.steps.push({
                step: currentStep,
                timestamp: Date.now(),
                progress: operation.progress
            });
        }
        
        this.notifyProgressUpdate(operation);
    }

    /**
     * Complete an operation
     */
    completeOperation(operationId, result = null) {
        const operation = this.activeOperations.get(operationId);
        if (!operation) return;
        
        operation.progress = 100;
        operation.status = 'completed';
        operation.endTime = Date.now();
        operation.duration = operation.endTime - operation.startTime;
        operation.result = result;
        
        this.notifyProgressUpdate(operation);
        
        // Remove after delay to allow UI to show completion
        setTimeout(() => {
            this.activeOperations.delete(operationId);
        }, 3000);
    }

    /**
     * Fail an operation
     */
    failOperation(operationId, error) {
        const operation = this.activeOperations.get(operationId);
        if (!operation) return;
        
        operation.status = 'failed';
        operation.endTime = Date.now();
        operation.duration = operation.endTime - operation.startTime;
        operation.error = error;
        
        this.notifyProgressUpdate(operation);
        
        // Remove after delay to allow UI to show error
        setTimeout(() => {
            this.activeOperations.delete(operationId);
        }, 5000);
    }

    /**
     * Get all active operations
     */
    getActiveOperations() {
        return Array.from(this.activeOperations.values());
    }

    /**
     * Get specific operation
     */
    getOperation(operationId) {
        return this.activeOperations.get(operationId);
    }

    /**
     * Notify progress update (override in implementation)
     */
    notifyProgressUpdate(operation) {
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('progressUpdate', {
            detail: operation
        }));
    }
}

// Global instance
window.progressTracker = new ProgressTracker();

/**
 * Live Data Feed Manager
 */
class LiveDataFeed {
    constructor() {
        this.feeds = new Map();
        this.updateCallbacks = new Map();
    }

    /**
     * Register a data feed
     */
    registerFeed(feedId, endpoint, updateInterval = 10000) {
        const feed = {
            id: feedId,
            endpoint,
            updateInterval,
            lastUpdate: null,
            data: null,
            isActive: false,
            intervalId: null
        };
        
        this.feeds.set(feedId, feed);
        return feed;
    }

    /**
     * Start a data feed
     */
    startFeed(feedId) {
        const feed = this.feeds.get(feedId);
        if (!feed || feed.isActive) return;
        
        feed.isActive = true;
        
        // Initial fetch
        this.fetchFeedData(feedId);
        
        // Set up interval
        feed.intervalId = setInterval(() => {
            this.fetchFeedData(feedId);
        }, feed.updateInterval);
        
        console.log(`📡 Started data feed: ${feedId}`);
    }

    /**
     * Stop a data feed
     */
    stopFeed(feedId) {
        const feed = this.feeds.get(feedId);
        if (!feed || !feed.isActive) return;
        
        feed.isActive = false;
        
        if (feed.intervalId) {
            clearInterval(feed.intervalId);
            feed.intervalId = null;
        }
        
        console.log(`📡 Stopped data feed: ${feedId}`);
    }

    /**
     * Fetch data for a feed
     */
    async fetchFeedData(feedId) {
        const feed = this.feeds.get(feedId);
        if (!feed) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}${feed.endpoint}`);
            const data = await response.json();
            
            feed.data = data;
            feed.lastUpdate = Date.now();
            
            this.notifyFeedUpdate(feedId, data);
            
        } catch (error) {
            console.warn(`Feed ${feedId} update failed:`, error);
        }
    }

    /**
     * Subscribe to feed updates
     */
    onFeedUpdate(feedId, callback) {
        if (!this.updateCallbacks.has(feedId)) {
            this.updateCallbacks.set(feedId, new Set());
        }
        this.updateCallbacks.get(feedId).add(callback);
    }

    /**
     * Unsubscribe from feed updates
     */
    offFeedUpdate(feedId, callback) {
        const callbacks = this.updateCallbacks.get(feedId);
        if (callbacks) {
            callbacks.delete(callback);
        }
    }

    /**
     * Notify feed update
     */
    notifyFeedUpdate(feedId, data) {
        const callbacks = this.updateCallbacks.get(feedId);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in feed callback for ${feedId}:`, error);
                }
            });
        }
    }

    /**
     * Get current feed data
     */
    getFeedData(feedId) {
        const feed = this.feeds.get(feedId);
        return feed ? feed.data : null;
    }
}

// Global instance
window.liveDataFeed = new LiveDataFeed();