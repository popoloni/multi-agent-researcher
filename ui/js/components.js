// Multi-Agent Researcher UI - UI Components

/**
 * UI Components and interactive elements
 */

// Toast notification system
class ToastManager {
    constructor() {
        this.container = utils.$('#toast-container');
        this.toasts = new Map();
    }

    show(message, type = 'info', duration = 5000) {
        const id = utils.generateId();
        const toast = this.createToast(id, message, type);
        
        this.container.appendChild(toast);
        this.toasts.set(id, toast);

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => this.remove(id), duration);
        }

        return id;
    }

    createToast(id, message, type) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.setAttribute('data-toast-id', id);

        const icon = this.getIcon(type);
        const title = this.getTitle(type);

        toast.innerHTML = `
            <div class="toast-header">
                <span class="toast-title">
                    <i class="${icon}"></i> ${title}
                </span>
                <button class="toast-close" onclick="toastManager.remove('${id}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="toast-message">${utils.escapeHtml(message)}</div>
        `;

        return toast;
    }

    getIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    getTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };
        return titles[type] || titles.info;
    }

    remove(id) {
        const toast = this.toasts.get(id);
        if (toast) {
            utils.animate.fadeOut(toast, 300);
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
                this.toasts.delete(id);
            }, 300);
        }
    }

    clear() {
        this.toasts.forEach((toast, id) => this.remove(id));
    }
}

// Loading overlay manager
class LoadingManager {
    constructor() {
        this.overlay = utils.$('#loading-overlay');
        this.text = utils.$('#loading-text');
        this.isVisible = false;
    }

    show(message = 'Processing...') {
        this.text.textContent = message;
        this.overlay.classList.add('active');
        this.isVisible = true;
        document.body.style.overflow = 'hidden';
    }

    hide() {
        this.overlay.classList.remove('active');
        this.isVisible = false;
        document.body.style.overflow = '';
    }

    updateText(message) {
        this.text.textContent = message;
    }
}

// Modal dialog manager
class ModalManager {
    constructor() {
        this.modals = new Map();
    }

    create(id, title, content, options = {}) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.setAttribute('data-modal-id', id);

        const size = options.size || 'medium';
        const showClose = options.showClose !== false;

        modal.innerHTML = `
            <div class="modal modal-${size}">
                <div class="modal-header">
                    <h3 class="modal-title">${utils.escapeHtml(title)}</h3>
                    ${showClose ? '<button class="modal-close" onclick="modalManager.close(\'' + id + '\')"><i class="fas fa-times"></i></button>' : ''}
                </div>
                <div class="modal-content">
                    ${content}
                </div>
                ${options.actions ? `<div class="modal-actions">${options.actions}</div>` : ''}
            </div>
        `;

        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.close(id);
            }
        });

        // Close on escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                this.close(id);
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);

        document.body.appendChild(modal);
        this.modals.set(id, { element: modal, escapeHandler });

        // Show with animation
        requestAnimationFrame(() => {
            modal.classList.add('active');
        });

        return id;
    }

    close(id) {
        const modal = this.modals.get(id);
        if (modal) {
            modal.element.classList.remove('active');
            setTimeout(() => {
                if (modal.element.parentNode) {
                    modal.element.parentNode.removeChild(modal.element);
                }
                this.modals.delete(id);
            }, 300);
        }
    }

    closeAll() {
        this.modals.forEach((modal, id) => this.close(id));
    }
}

// Progress bar component
class ProgressBar {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? utils.$(container) : container;
        this.options = {
            showPercentage: true,
            showLabel: true,
            animated: true,
            ...options
        };
        this.value = 0;
        this.max = 100;
        this.render();
    }

    render() {
        this.container.innerHTML = `
            <div class="progress-wrapper">
                ${this.options.showLabel ? '<div class="progress-label"></div>' : ''}
                <div class="progress">
                    <div class="progress-bar" style="width: 0%"></div>
                </div>
                ${this.options.showPercentage ? '<div class="progress-percentage">0%</div>' : ''}
            </div>
        `;

        this.bar = this.container.querySelector('.progress-bar');
        this.label = this.container.querySelector('.progress-label');
        this.percentage = this.container.querySelector('.progress-percentage');
    }

    setValue(value, label = '') {
        this.value = Math.max(0, Math.min(value, this.max));
        const percent = (this.value / this.max) * 100;

        this.bar.style.width = `${percent}%`;
        
        if (this.percentage) {
            this.percentage.textContent = `${Math.round(percent)}%`;
        }
        
        if (this.label && label) {
            this.label.textContent = label;
        }
    }

    setMax(max) {
        this.max = max;
        this.setValue(this.value);
    }

    increment(amount = 1, label = '') {
        this.setValue(this.value + amount, label);
    }

    reset() {
        this.setValue(0);
    }
}

// Data table component
class DataTable {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? utils.$(container) : container;
        this.options = {
            sortable: true,
            searchable: true,
            pagination: true,
            pageSize: 10,
            ...options
        };
        this.data = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
    }

    setData(data, columns) {
        this.data = data;
        this.columns = columns;
        this.filteredData = [...data];
        this.render();
    }

    render() {
        const searchHtml = this.options.searchable ? `
            <div class="table-search">
                <input type="text" placeholder="Search..." onkeyup="this.table.search(this.value)">
            </div>
        ` : '';

        this.container.innerHTML = `
            <div class="data-table">
                ${searchHtml}
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                ${this.columns.map(col => `
                                    <th ${this.options.sortable ? `onclick="this.table.sort('${col.key}')"` : ''} 
                                        class="${this.options.sortable ? 'sortable' : ''}">
                                        ${col.title}
                                        ${this.options.sortable ? '<i class="fas fa-sort"></i>' : ''}
                                    </th>
                                `).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${this.renderRows()}
                        </tbody>
                    </table>
                </div>
                ${this.options.pagination ? this.renderPagination() : ''}
            </div>
        `;

        // Store reference for event handlers
        this.container.querySelector('.data-table').table = this;
    }

    renderRows() {
        const start = (this.currentPage - 1) * this.options.pageSize;
        const end = start + this.options.pageSize;
        const pageData = this.filteredData.slice(start, end);

        return pageData.map(row => `
            <tr>
                ${this.columns.map(col => `
                    <td>${this.formatCell(row[col.key], col)}</td>
                `).join('')}
            </tr>
        `).join('');
    }

    formatCell(value, column) {
        if (column.formatter) {
            return column.formatter(value);
        }
        return utils.escapeHtml(String(value || ''));
    }

    renderPagination() {
        const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
        if (totalPages <= 1) return '';

        return `
            <div class="table-pagination">
                <button onclick="this.table.goToPage(${this.currentPage - 1})" 
                        ${this.currentPage === 1 ? 'disabled' : ''}>
                    Previous
                </button>
                <span>Page ${this.currentPage} of ${totalPages}</span>
                <button onclick="this.table.goToPage(${this.currentPage + 1})" 
                        ${this.currentPage === totalPages ? 'disabled' : ''}>
                    Next
                </button>
            </div>
        `;
    }

    search(query) {
        if (!query) {
            this.filteredData = [...this.data];
        } else {
            this.filteredData = this.data.filter(row =>
                this.columns.some(col =>
                    String(row[col.key] || '').toLowerCase().includes(query.toLowerCase())
                )
            );
        }
        this.currentPage = 1;
        this.render();
    }

    sort(columnKey) {
        if (this.sortColumn === columnKey) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = columnKey;
            this.sortDirection = 'asc';
        }

        this.filteredData.sort((a, b) => {
            const aVal = a[columnKey];
            const bVal = b[columnKey];
            
            if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        this.render();
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
        this.currentPage = Math.max(1, Math.min(page, totalPages));
        this.render();
    }
}

// Chart component (simple implementation)
class SimpleChart {
    constructor(container, type = 'line') {
        this.container = typeof container === 'string' ? utils.$(container) : container;
        this.type = type;
        this.data = [];
        this.options = {};
    }

    setData(data, options = {}) {
        this.data = data;
        this.options = options;
        this.render();
    }

    render() {
        // Simple SVG-based chart implementation
        const width = this.container.offsetWidth || 400;
        const height = this.container.offsetHeight || 300;
        const margin = { top: 20, right: 20, bottom: 40, left: 40 };
        const chartWidth = width - margin.left - margin.right;
        const chartHeight = height - margin.top - margin.bottom;

        if (this.type === 'bar') {
            this.renderBarChart(chartWidth, chartHeight, margin);
        } else {
            this.renderLineChart(chartWidth, chartHeight, margin);
        }
    }

    renderBarChart(width, height, margin) {
        const maxValue = Math.max(...this.data.map(d => d.value));
        const barWidth = width / this.data.length;

        const svg = `
            <svg width="${width + margin.left + margin.right}" height="${height + margin.top + margin.bottom}">
                <g transform="translate(${margin.left},${margin.top})">
                    ${this.data.map((d, i) => {
                        const barHeight = (d.value / maxValue) * height;
                        const x = i * barWidth;
                        const y = height - barHeight;
                        return `
                            <rect x="${x}" y="${y}" width="${barWidth * 0.8}" height="${barHeight}" 
                                  fill="var(--primary-color)" opacity="0.8"/>
                            <text x="${x + barWidth * 0.4}" y="${height + 15}" 
                                  text-anchor="middle" font-size="12">${d.label}</text>
                        `;
                    }).join('')}
                </g>
            </svg>
        `;

        this.container.innerHTML = svg;
    }

    renderLineChart(width, height, margin) {
        // Simple line chart implementation
        const maxValue = Math.max(...this.data.map(d => d.value));
        const stepX = width / (this.data.length - 1);

        const points = this.data.map((d, i) => {
            const x = i * stepX;
            const y = height - (d.value / maxValue) * height;
            return `${x},${y}`;
        }).join(' ');

        const svg = `
            <svg width="${width + margin.left + margin.right}" height="${height + margin.top + margin.bottom}">
                <g transform="translate(${margin.left},${margin.top})">
                    <polyline points="${points}" fill="none" stroke="var(--primary-color)" stroke-width="2"/>
                    ${this.data.map((d, i) => {
                        const x = i * stepX;
                        const y = height - (d.value / maxValue) * height;
                        return `
                            <circle cx="${x}" cy="${y}" r="4" fill="var(--primary-color)"/>
                            <text x="${x}" y="${height + 15}" text-anchor="middle" font-size="12">${d.label}</text>
                        `;
                    }).join('')}
                </g>
            </svg>
        `;

        this.container.innerHTML = svg;
    }
}

// Initialize global component managers
const toastManager = new ToastManager();
const loadingManager = new LoadingManager();
const modalManager = new ModalManager();

// Export components
window.components = {
    ToastManager,
    LoadingManager,
    ModalManager,
    ProgressBar,
    DataTable,
    SimpleChart
};

// Export global instances
window.toastManager = toastManager;
window.loadingManager = loadingManager;
window.modalManager = modalManager;

// Global toast function for convenience
window.showToast = (message, type = 'info', duration = 5000) => {
    return toastManager.show(message, type, duration);
};