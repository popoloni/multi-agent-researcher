/**
 * Data Visualization Components
 * Lightweight charting and visualization without external dependencies
 */

class ChartRenderer {
    constructor() {
        this.charts = new Map();
    }

    /**
     * Create a line chart
     */
    createLineChart(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const config = {
            width: options.width || container.clientWidth || 400,
            height: options.height || 300,
            margin: options.margin || { top: 20, right: 20, bottom: 40, left: 50 },
            lineColor: options.lineColor || '#4285f4',
            pointColor: options.pointColor || '#4285f4',
            gridColor: options.gridColor || '#e0e0e0',
            textColor: options.textColor || '#666',
            showPoints: options.showPoints !== false,
            showGrid: options.showGrid !== false,
            ...options
        };

        const chart = new LineChart(container, data, config);
        this.charts.set(containerId, chart);
        return chart;
    }

    /**
     * Create a bar chart
     */
    createBarChart(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const config = {
            width: options.width || container.clientWidth || 400,
            height: options.height || 300,
            margin: options.margin || { top: 20, right: 20, bottom: 40, left: 50 },
            barColor: options.barColor || '#4285f4',
            gridColor: options.gridColor || '#e0e0e0',
            textColor: options.textColor || '#666',
            showGrid: options.showGrid !== false,
            ...options
        };

        const chart = new BarChart(container, data, config);
        this.charts.set(containerId, chart);
        return chart;
    }

    /**
     * Create a pie chart
     */
    createPieChart(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const config = {
            width: options.width || container.clientWidth || 300,
            height: options.height || 300,
            colors: options.colors || ['#4285f4', '#34a853', '#fbbc04', '#ea4335', '#9c27b0'],
            showLabels: options.showLabels !== false,
            showLegend: options.showLegend !== false,
            ...options
        };

        const chart = new PieChart(container, data, config);
        this.charts.set(containerId, chart);
        return chart;
    }

    /**
     * Create a progress ring
     */
    createProgressRing(containerId, value, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const config = {
            size: options.size || 120,
            strokeWidth: options.strokeWidth || 8,
            color: options.color || '#4285f4',
            backgroundColor: options.backgroundColor || '#e0e0e0',
            showText: options.showText !== false,
            ...options
        };

        const chart = new ProgressRing(container, value, config);
        this.charts.set(containerId, chart);
        return chart;
    }

    /**
     * Update chart data
     */
    updateChart(containerId, data) {
        const chart = this.charts.get(containerId);
        if (chart && chart.update) {
            chart.update(data);
        }
    }

    /**
     * Remove chart
     */
    removeChart(containerId) {
        const chart = this.charts.get(containerId);
        if (chart && chart.destroy) {
            chart.destroy();
        }
        this.charts.delete(containerId);
    }
}

/**
 * Line Chart Implementation
 */
class LineChart {
    constructor(container, data, config) {
        this.container = container;
        this.data = data;
        this.config = config;
        this.svg = null;
        this.render();
    }

    render() {
        this.container.innerHTML = '';
        
        const { width, height, margin } = this.config;
        const chartWidth = width - margin.left - margin.right;
        const chartHeight = height - margin.top - margin.bottom;

        // Create SVG
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('width', width);
        this.svg.setAttribute('height', height);
        this.svg.style.display = 'block';
        this.container.appendChild(this.svg);

        // Create chart group
        const chartGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        chartGroup.setAttribute('transform', `translate(${margin.left}, ${margin.top})`);
        this.svg.appendChild(chartGroup);

        if (!this.data || this.data.length === 0) {
            this.renderNoData(chartGroup, chartWidth, chartHeight);
            return;
        }

        // Calculate scales
        const xValues = this.data.map(d => d.x);
        const yValues = this.data.map(d => d.y);
        const xMin = Math.min(...xValues);
        const xMax = Math.max(...xValues);
        const yMin = Math.min(0, Math.min(...yValues));
        const yMax = Math.max(...yValues);

        const xScale = (x) => ((x - xMin) / (xMax - xMin)) * chartWidth;
        const yScale = (y) => chartHeight - ((y - yMin) / (yMax - yMin)) * chartHeight;

        // Render grid
        if (this.config.showGrid) {
            this.renderGrid(chartGroup, chartWidth, chartHeight, xScale, yScale, xMin, xMax, yMin, yMax);
        }

        // Render line
        this.renderLine(chartGroup, xScale, yScale);

        // Render points
        if (this.config.showPoints) {
            this.renderPoints(chartGroup, xScale, yScale);
        }

        // Render axes
        this.renderAxes(chartGroup, chartWidth, chartHeight, xMin, xMax, yMin, yMax);
    }

    renderLine(group, xScale, yScale) {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        
        let d = '';
        this.data.forEach((point, i) => {
            const x = xScale(point.x);
            const y = yScale(point.y);
            d += i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`;
        });

        path.setAttribute('d', d);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', this.config.lineColor);
        path.setAttribute('stroke-width', '2');
        group.appendChild(path);
    }

    renderPoints(group, xScale, yScale) {
        this.data.forEach(point => {
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', xScale(point.x));
            circle.setAttribute('cy', yScale(point.y));
            circle.setAttribute('r', '4');
            circle.setAttribute('fill', this.config.pointColor);
            group.appendChild(circle);
        });
    }

    renderGrid(group, width, height, xScale, yScale, xMin, xMax, yMin, yMax) {
        const gridGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        gridGroup.setAttribute('stroke', this.config.gridColor);
        gridGroup.setAttribute('stroke-width', '1');

        // Vertical grid lines
        for (let i = 0; i <= 5; i++) {
            const x = (width / 5) * i;
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x);
            line.setAttribute('y1', 0);
            line.setAttribute('x2', x);
            line.setAttribute('y2', height);
            gridGroup.appendChild(line);
        }

        // Horizontal grid lines
        for (let i = 0; i <= 5; i++) {
            const y = (height / 5) * i;
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', 0);
            line.setAttribute('y1', y);
            line.setAttribute('x2', width);
            line.setAttribute('y2', y);
            gridGroup.appendChild(line);
        }

        group.appendChild(gridGroup);
    }

    renderAxes(group, width, height, xMin, xMax, yMin, yMax) {
        // X-axis
        const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        xAxis.setAttribute('x1', 0);
        xAxis.setAttribute('y1', height);
        xAxis.setAttribute('x2', width);
        xAxis.setAttribute('y2', height);
        xAxis.setAttribute('stroke', this.config.textColor);
        group.appendChild(xAxis);

        // Y-axis
        const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        yAxis.setAttribute('x1', 0);
        yAxis.setAttribute('y1', 0);
        yAxis.setAttribute('x2', 0);
        yAxis.setAttribute('y2', height);
        yAxis.setAttribute('stroke', this.config.textColor);
        group.appendChild(yAxis);

        // Labels
        this.renderAxisLabels(group, width, height, xMin, xMax, yMin, yMax);
    }

    renderAxisLabels(group, width, height, xMin, xMax, yMin, yMax) {
        // X-axis labels
        for (let i = 0; i <= 5; i++) {
            const x = (width / 5) * i;
            const value = xMin + ((xMax - xMin) / 5) * i;
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x);
            text.setAttribute('y', height + 20);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '12');
            text.setAttribute('fill', this.config.textColor);
            text.textContent = value.toFixed(1);
            group.appendChild(text);
        }

        // Y-axis labels
        for (let i = 0; i <= 5; i++) {
            const y = height - (height / 5) * i;
            const value = yMin + ((yMax - yMin) / 5) * i;
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', -10);
            text.setAttribute('y', y + 4);
            text.setAttribute('text-anchor', 'end');
            text.setAttribute('font-size', '12');
            text.setAttribute('fill', this.config.textColor);
            text.textContent = value.toFixed(1);
            group.appendChild(text);
        }
    }

    renderNoData(group, width, height) {
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', width / 2);
        text.setAttribute('y', height / 2);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '16');
        text.setAttribute('fill', this.config.textColor);
        text.textContent = 'No data available';
        group.appendChild(text);
    }

    update(newData) {
        this.data = newData;
        this.render();
    }

    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

/**
 * Progress Ring Implementation
 */
class ProgressRing {
    constructor(container, value, config) {
        this.container = container;
        this.value = Math.max(0, Math.min(100, value));
        this.config = config;
        this.svg = null;
        this.render();
    }

    render() {
        this.container.innerHTML = '';
        
        const { size, strokeWidth } = this.config;
        const radius = (size - strokeWidth) / 2;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (this.value / 100) * circumference;

        // Create SVG
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('width', size);
        this.svg.setAttribute('height', size);
        this.svg.style.display = 'block';
        this.container.appendChild(this.svg);

        // Background circle
        const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        bgCircle.setAttribute('cx', size / 2);
        bgCircle.setAttribute('cy', size / 2);
        bgCircle.setAttribute('r', radius);
        bgCircle.setAttribute('fill', 'none');
        bgCircle.setAttribute('stroke', this.config.backgroundColor);
        bgCircle.setAttribute('stroke-width', strokeWidth);
        this.svg.appendChild(bgCircle);

        // Progress circle
        const progressCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        progressCircle.setAttribute('cx', size / 2);
        progressCircle.setAttribute('cy', size / 2);
        progressCircle.setAttribute('r', radius);
        progressCircle.setAttribute('fill', 'none');
        progressCircle.setAttribute('stroke', this.config.color);
        progressCircle.setAttribute('stroke-width', strokeWidth);
        progressCircle.setAttribute('stroke-linecap', 'round');
        progressCircle.setAttribute('stroke-dasharray', circumference);
        progressCircle.setAttribute('stroke-dashoffset', offset);
        progressCircle.setAttribute('transform', `rotate(-90 ${size / 2} ${size / 2})`);
        this.svg.appendChild(progressCircle);

        // Text
        if (this.config.showText) {
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', size / 2);
            text.setAttribute('y', size / 2 + 6);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', size / 6);
            text.setAttribute('font-weight', 'bold');
            text.setAttribute('fill', this.config.color);
            text.textContent = `${Math.round(this.value)}%`;
            this.svg.appendChild(text);
        }
    }

    update(newValue) {
        this.value = Math.max(0, Math.min(100, newValue));
        this.render();
    }

    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

/**
 * Metrics Dashboard Component
 */
class MetricsDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.metrics = new Map();
        this.charts = new Map();
    }

    addMetric(id, title, value, options = {}) {
        const metric = {
            id,
            title,
            value,
            type: options.type || 'number',
            format: options.format || 'default',
            color: options.color || '#4285f4',
            trend: options.trend || null,
            history: options.history || []
        };

        this.metrics.set(id, metric);
        this.render();
    }

    updateMetric(id, value, trend = null) {
        const metric = this.metrics.get(id);
        if (!metric) return;

        // Add to history
        metric.history.push({
            value: metric.value,
            timestamp: Date.now()
        });

        // Keep only last 20 values
        if (metric.history.length > 20) {
            metric.history = metric.history.slice(-20);
        }

        metric.value = value;
        if (trend !== null) {
            metric.trend = trend;
        }

        this.render();
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = '';
        this.container.className = 'metrics-dashboard';

        this.metrics.forEach(metric => {
            const metricElement = this.createMetricElement(metric);
            this.container.appendChild(metricElement);
        });
    }

    createMetricElement(metric) {
        const element = document.createElement('div');
        element.className = 'metric-card';
        element.innerHTML = `
            <div class="metric-header">
                <h3>${metric.title}</h3>
                ${metric.trend ? `<span class="metric-trend ${metric.trend > 0 ? 'positive' : 'negative'}">
                    ${metric.trend > 0 ? '↗' : '↘'} ${Math.abs(metric.trend).toFixed(1)}%
                </span>` : ''}
            </div>
            <div class="metric-value" style="color: ${metric.color}">
                ${this.formatValue(metric.value, metric.format)}
            </div>
            <div class="metric-chart" id="chart-${metric.id}"></div>
        `;

        // Add mini chart if history exists
        if (metric.history.length > 1) {
            setTimeout(() => {
                const chartData = metric.history.map((item, index) => ({
                    x: index,
                    y: item.value
                }));

                const chartRenderer = new ChartRenderer();
                chartRenderer.createLineChart(`chart-${metric.id}`, chartData, {
                    width: 200,
                    height: 60,
                    margin: { top: 5, right: 5, bottom: 5, left: 5 },
                    lineColor: metric.color,
                    showPoints: false,
                    showGrid: false
                });
            }, 0);
        }

        return element;
    }

    formatValue(value, format) {
        switch (format) {
            case 'percentage':
                return `${value.toFixed(1)}%`;
            case 'currency':
                return `$${value.toLocaleString()}`;
            case 'bytes':
                return this.formatBytes(value);
            case 'duration':
                return this.formatDuration(value);
            default:
                return typeof value === 'number' ? value.toLocaleString() : value;
        }
    }

    formatBytes(bytes) {
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
    }

    formatDuration(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }
}

// Global chart renderer instance
window.chartRenderer = new ChartRenderer();