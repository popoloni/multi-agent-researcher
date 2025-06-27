// API Configuration
const API_BASE_URL = window.location.origin;

// Global state
let repositories = [];
let filteredRepositories = [];

// DOM Elements
const repositoryList = document.getElementById('repository-list');
const repositorySearch = document.getElementById('repository-search');
const keywordSearch = document.getElementById('keyword-search');
const paginationText = document.getElementById('pagination-text');
const addRepositoryModal = document.getElementById('add-repository-modal');
const addRepositoryForm = document.getElementById('add-repository-form');
const loadingOverlay = document.getElementById('loading-overlay');
const notificationsContainer = document.getElementById('notifications');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// Initialize application
async function initializeApp() {
    try {
        await loadRepositories();
    } catch (error) {
        console.error('Failed to initialize app:', error);
        showNotification('Failed to load repositories', 'error');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    repositorySearch.addEventListener('input', filterRepositories);
    keywordSearch.addEventListener('input', filterRepositories);
    
    // Form submission
    addRepositoryForm.addEventListener('submit', handleAddRepository);
    
    // Auto-detect repository name from URL
    document.getElementById('repo-url').addEventListener('input', function(e) {
        const url = e.target.value;
        const nameField = document.getElementById('repo-name');
        
        if (url && !nameField.value) {
            const repoName = extractRepositoryName(url);
            if (repoName) {
                nameField.value = repoName;
            }
        }
    });
}

// API Functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API request failed: ${endpoint}`, error);
        throw error;
    }
}

// Repository Management
async function loadRepositories() {
    showLoading(true);
    try {
        const response = await apiRequest('/kenobi/repositories');
        repositories = response.repositories || [];
        filteredRepositories = [...repositories];
        renderRepositories();
        updatePagination();
    } catch (error) {
        console.error('Failed to load repositories:', error);
        showNotification('Failed to load repositories', 'error');
        repositories = [];
        filteredRepositories = [];
        renderRepositories();
    } finally {
        showLoading(false);
    }
}

async function addRepository(repositoryData) {
    showLoading(true);
    try {
        const response = await apiRequest('/kenobi/repositories/index', {
            method: 'POST',
            body: JSON.stringify(repositoryData)
        });
        
        showNotification('Repository added successfully!', 'success');
        await loadRepositories(); // Reload the list
        return response;
    } catch (error) {
        console.error('Failed to add repository:', error);
        showNotification(`Failed to add repository: ${error.message}`, 'error');
        throw error;
    } finally {
        showLoading(false);
    }
}

async function deleteRepository(repositoryId) {
    if (!confirm('Are you sure you want to delete this repository?')) {
        return;
    }
    
    showLoading(true);
    try {
        await apiRequest(`/kenobi/repositories/${repositoryId}`, {
            method: 'DELETE'
        });
        
        showNotification('Repository deleted successfully!', 'success');
        await loadRepositories(); // Reload the list
    } catch (error) {
        console.error('Failed to delete repository:', error);
        showNotification(`Failed to delete repository: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function getRepositoryDetails(repositoryId) {
    showLoading(true);
    try {
        const response = await apiRequest(`/kenobi/repositories/${repositoryId}`);
        return response;
    } catch (error) {
        console.error('Failed to get repository details:', error);
        showNotification(`Failed to load repository details: ${error.message}`, 'error');
        throw error;
    } finally {
        showLoading(false);
    }
}

async function generateDocumentation(repositoryId) {
    showLoading(true);
    try {
        const response = await apiRequest(`/kenobi/repositories/${repositoryId}/index`, {
            method: 'POST'
        });
        
        showNotification('Documentation generation started!', 'success');
        return response;
    } catch (error) {
        console.error('Failed to generate documentation:', error);
        showNotification(`Failed to generate documentation: ${error.message}`, 'error');
        throw error;
    } finally {
        showLoading(false);
    }
}

// UI Functions
function renderRepositories() {
    if (filteredRepositories.length === 0) {
        repositoryList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-folder-open"></i>
                <p>No repositories found. Add your first repository to get started.</p>
            </div>
        `;
        return;
    }
    
    const repositoriesHTML = filteredRepositories.map(repo => `
        <div class="repository-row">
            <div class="table-row">
                <div class="repository-name">${escapeHtml(repo.name || 'Unnamed Repository')}</div>
                <div class="repository-url">${escapeHtml(repo.url || 'No URL')}</div>
                <div class="repository-actions">
                    <a href="#" class="action-link" onclick="viewFunctionalities('${repo.id}')">
                        <i class="fas fa-file-text"></i>
                        Functionalities registry
                    </a>
                    <button class="action-btn" onclick="viewRepositoryDetails('${repo.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn" onclick="generateDocumentation('${repo.id}')" title="Generate Documentation">
                        <i class="fas fa-file-alt"></i>
                    </button>
                    <button class="action-btn danger" onclick="deleteRepository('${repo.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                    <a href="${escapeHtml(repo.url || '#')}" target="_blank" class="action-btn" title="Open in GitHub">
                        <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            </div>
        </div>
    `).join('');
    
    repositoryList.innerHTML = repositoriesHTML;
}

function filterRepositories() {
    const searchTerm = repositorySearch.value.toLowerCase();
    const keywordTerm = keywordSearch.value.toLowerCase();
    
    filteredRepositories = repositories.filter(repo => {
        const nameMatch = (repo.name || '').toLowerCase().includes(searchTerm);
        const keywordMatch = keywordTerm === '' || 
            (repo.keywords && repo.keywords.some(keyword => 
                keyword.toLowerCase().includes(keywordTerm)
            ));
        
        return nameMatch && keywordMatch;
    });
    
    renderRepositories();
    updatePagination();
}

function updatePagination() {
    const total = repositories.length;
    const filtered = filteredRepositories.length;
    paginationText.textContent = `1 - ${filtered} of ${total}`;
}

// Modal Functions
function showAddRepositoryModal() {
    addRepositoryModal.classList.remove('hidden');
    document.getElementById('repo-url').focus();
}

function hideAddRepositoryModal() {
    addRepositoryModal.classList.add('hidden');
    addRepositoryForm.reset();
}

function showRepositoryDetailsModal(repository) {
    const modal = document.getElementById('repository-details-modal');
    const title = document.getElementById('repo-details-title');
    const content = document.getElementById('repository-details-content');
    
    title.textContent = repository.name || 'Repository Details';
    content.innerHTML = `
        <div class="space-y-4">
            <div>
                <h3 class="font-semibold mb-2">Repository Information</h3>
                <p><strong>Name:</strong> ${escapeHtml(repository.name || 'N/A')}</p>
                <p><strong>URL:</strong> <a href="${escapeHtml(repository.url || '#')}" target="_blank" class="text-blue-600">${escapeHtml(repository.url || 'N/A')}</a></p>
                <p><strong>Branch:</strong> ${escapeHtml(repository.branch || 'main')}</p>
                <p><strong>Status:</strong> ${escapeHtml(repository.status || 'Unknown')}</p>
            </div>
            ${repository.description ? `
                <div>
                    <h3 class="font-semibold mb-2">Description</h3>
                    <p>${escapeHtml(repository.description)}</p>
                </div>
            ` : ''}
            ${repository.analysis ? `
                <div>
                    <h3 class="font-semibold mb-2">Analysis</h3>
                    <pre class="bg-gray-100 p-4 rounded text-sm overflow-auto">${escapeHtml(JSON.stringify(repository.analysis, null, 2))}</pre>
                </div>
            ` : ''}
        </div>
    `;
    
    modal.classList.remove('hidden');
}

function hideRepositoryDetailsModal() {
    document.getElementById('repository-details-modal').classList.add('hidden');
}

// Event Handlers
async function handleAddRepository(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const repositoryData = {
        url: document.getElementById('repo-url').value,
        name: document.getElementById('repo-name').value,
        branch: document.getElementById('repo-branch').value || 'main',
        description: document.getElementById('repo-description').value
    };
    
    // Auto-detect name if not provided
    if (!repositoryData.name) {
        repositoryData.name = extractRepositoryName(repositoryData.url);
    }
    
    try {
        await addRepository(repositoryData);
        hideAddRepositoryModal();
    } catch (error) {
        // Error is already handled in addRepository function
    }
}

async function viewRepositoryDetails(repositoryId) {
    try {
        const repository = await getRepositoryDetails(repositoryId);
        showRepositoryDetailsModal(repository);
    } catch (error) {
        // Error is already handled in getRepositoryDetails function
    }
}

function viewFunctionalities(repositoryId) {
    // This would navigate to a functionalities page
    // For now, we'll show a placeholder
    showNotification('Functionalities registry feature coming soon!', 'info');
}

function clearKeyword() {
    keywordSearch.value = '';
    filterRepositories();
}

// Utility Functions
function extractRepositoryName(url) {
    try {
        const urlObj = new URL(url);
        const pathParts = urlObj.pathname.split('/').filter(part => part);
        
        if (pathParts.length >= 2) {
            return pathParts[pathParts.length - 1].replace('.git', '');
        }
    } catch (error) {
        console.error('Failed to extract repository name:', error);
    }
    
    return '';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="flex justify-between items-start">
            <div>
                <p class="font-medium">${escapeHtml(message)}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    notificationsContainer.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Global functions for onclick handlers
window.showAddRepositoryModal = showAddRepositoryModal;
window.hideAddRepositoryModal = hideAddRepositoryModal;
window.hideRepositoryDetailsModal = hideRepositoryDetailsModal;
window.viewRepositoryDetails = viewRepositoryDetails;
window.viewFunctionalities = viewFunctionalities;
window.deleteRepository = deleteRepository;
window.generateDocumentation = generateDocumentation;
window.clearKeyword = clearKeyword;