// Media Monitor Platform - JavaScript Utilities

// Global variables
let currentPage = 0;
let selectedContentIds = [];
let allContent = [];

// Utility functions
function showNotification(message, type = 'info') {
    // Simple notification system
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown Date';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function getSourceTypeLabel(sourceType) {
    const labels = {
        'blog': 'Blog',
        'podcast': 'Podcast',
        'twitter': 'Twitter',
        'reddit': 'Reddit',
        'unknown': 'Unknown'
    };
    return labels[sourceType] || 'Unknown';
}

function getSourceTypeIcon(sourceType) {
    const icons = {
        'blog': 'fa-newspaper',
        'podcast': 'fa-podcast', 
        'twitter': 'fa-twitter',
        'reddit': 'fa-reddit-alien',
        'unknown': 'fa-question-circle'
    };
    return icons[sourceType] || 'fa-question-circle';
}

function generatePlaceholderImage(content) {
    // This function can be expanded later to generate more sophisticated placeholders
    return `https://via.placeholder.com/300x200/${getSourceTypeColor(content.source_type)}/ffffff?text=${encodeURIComponent(content.source_type || 'Content')}`;
}

function getSourceTypeColor(sourceType) {
    const colors = {
        'blog': '667eea',
        'podcast': 'f093fb',
        'twitter': '1da1f2',
        'reddit': 'ff4500',
        'unknown': '6b7280'
    };
    return colors[sourceType] || '6b7280';
}

// Modal functions
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('show');
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        modal.classList.add('hidden');
    }
}

// Content selection functions
function toggleContentSelection(contentId) {
    const index = selectedContentIds.indexOf(contentId);
    if (index > -1) {
        selectedContentIds.splice(index, 1);
    } else {
        selectedContentIds.push(contentId);
    }
    updateSelectedContentList();
}

function updateSelectedContentList() {
    const list = document.getElementById('selectedContentList');
    if (!list) return;
    
    if (selectedContentIds.length === 0) {
        list.innerHTML = '<p class="text-gray-500 text-center">No content items selected. Check the boxes above content items to select them.</p>';
        return;
    }

    const selectedContent = allContent.filter(item => selectedContentIds.includes(item.id));
    list.innerHTML = selectedContent.map(item => `
        <div class="flex items-center justify-between p-2 bg-white rounded border mb-2">
            <span class="text-sm font-medium">${item.title}</span>
            <button onclick="removeContentSelection(${item.id})" class="text-red-500 hover:text-red-700">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

function removeContentSelection(contentId) {
    const index = selectedContentIds.indexOf(contentId);
    if (index > -1) {
        selectedContentIds.splice(index, 1);
        // Uncheck the checkbox
        const checkbox = document.querySelector(`input[data-content-id="${contentId}"]`);
        if (checkbox) checkbox.checked = false;
        updateSelectedContentList();
    }
}

// API functions
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification(`API Error: ${error.message}`, 'error');
        throw error;
    }
}

// Content loading functions
async function loadContent() {
    console.log('🚀 Loading content and sources...');
    try {
        // Load both content and sources to enable proper filtering
        const [content, sources] = await Promise.all([
            fetchAPI('/api/content?limit=20'),
            fetchAPI('/api/sources')
        ]);
        console.log('📊 Content items:', content.length);
        console.log('📚 Sources:', sources.length);
        
        // Enhance content with source information
        allContent = content.map(item => {
            const source = sources.find(s => s.id === item.source_id);
            return {
                ...item,
                source_type: source ? source.source_type : 'unknown',
                source_name: source ? source.name : 'Unknown Source'
            };
        });
        
        populateSourceFilter(sources);
        filterContent(); // Apply any existing filters
        currentPage = 0;
    } catch (error) {
        console.error('Error loading content:', error);
        showNotification('Error loading content', 'error');
    }
}

async function loadMoreContent() {
    try {
        currentPage++;
        const offset = currentPage * 20;
        const [moreContent, sources] = await Promise.all([
            fetchAPI(`/api/content?limit=20&offset=${offset}`),
            fetchAPI('/api/sources')
        ]);
        
        if (moreContent.length > 0) {
            // Enhance the additional content with source information
            const enhancedMoreContent = moreContent.map(item => {
                const source = sources.find(s => s.id === item.source_id);
                return {
                    ...item,
                    source_type: source ? source.source_type : 'unknown',
                    source_name: source ? source.name : 'Unknown Source'
                };
            });
            
            allContent = [...allContent, ...enhancedMoreContent];
            // Apply current filters to the updated content
            filterContent();
        } else {
            const loadMoreBtn = document.getElementById('loadMoreBtn');
            if (loadMoreBtn) loadMoreBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading more content:', error);
        showNotification('Error loading more content', 'error');
    }
}

// Content rendering functions
function renderContentGrid(content) {
    console.log('🎨 Rendering content grid:', content.length, 'items');
    const grid = document.getElementById('contentGrid');
    if (!grid) {
        console.error('❌ Content grid element not found!');
        return;
    }
    
    grid.innerHTML = '';

    content.forEach(item => {
        const card = createContentCard(item);
        grid.appendChild(card);
    });
}

function createContentCard(content) {
    const card = document.createElement('div');
    card.className = 'content-card bg-white rounded-lg shadow-md overflow-hidden';
    
    // Get the source type with fallback
    const sourceType = content.source_type || 'unknown';
    const sourceIcon = getSourceTypeIcon(sourceType);
    const sourceLabel = getSourceTypeLabel(sourceType);
    const sourceColor = getSourceTypeColor(sourceType);
    
    card.innerHTML = `
        <div class="relative">
            <div class="w-full h-48 flex items-center justify-center" style="background: linear-gradient(135deg, #${sourceColor}15 0%, #${sourceColor}35 100%);">
                <div class="text-center p-6">
                    <i class="fas ${sourceIcon} text-5xl mb-3" style="color: #${sourceColor};"></i>
                    <p class="text-sm font-bold uppercase tracking-wide" style="color: #${sourceColor};">${sourceLabel}</p>
                    <p class="text-xs text-gray-500 mt-1">${content.source_name || 'Unknown Source'}</p>
                </div>
            </div>
            <div class="absolute top-2 right-2">
                <input type="checkbox" class="content-checkbox" data-content-id="${content.id}" onchange="toggleContentSelection(${content.id})">
            </div>
        </div>
        <div class="p-4">
            <div class="flex items-center mb-2">
                <span class="text-white text-xs px-2 py-1 rounded-full font-medium" style="background-color: #${sourceColor};">${sourceLabel}</span>
                <span class="text-gray-500 text-xs ml-auto">${formatDate(content.published_at)}</span>
            </div>
            <h3 class="font-semibold text-lg mb-2 line-clamp-2">${content.title}</h3>
            <p class="text-gray-600 text-sm mb-3 line-clamp-2">${content.description || 'No description available'}</p>
            <div class="flex items-center justify-between">
                <span class="text-gray-500 text-sm">${content.author || 'Unknown Author'}</span>
                <a href="${content.content_url || '#'}" target="_blank" class="text-purple-600 hover:text-purple-800 text-sm font-medium">
                    Read More <i class="fas fa-external-link-alt ml-1"></i>
                </a>
            </div>
        </div>
    `;
    
    return card;
}

// Filter and sort functions
function populateSourceFilter(sources) {
    const sourceFilter = document.getElementById('sourceFilter');
    if (!sourceFilter) return;
    
    // Clear existing options
    sourceFilter.innerHTML = '<option value="">All Sources</option>';
    
    // Group sources by type
    const sourcesByType = {};
    sources.forEach(source => {
        if (!sourcesByType[source.source_type]) {
            sourcesByType[source.source_type] = [];
        }
        sourcesByType[source.source_type].push(source);
    });
    
    // Add source type headers and individual sources
    Object.entries(sourcesByType).forEach(([type, typeSources]) => {
        // Add type header with appropriate emoji
        const typeIcons = {
            'blog': '📰',
            'podcast': '🎧',
            'twitter': '🐦', 
            'reddit': '📱'
        };
        const typeOption = document.createElement('option');
        typeOption.value = `type:${type}`;
        typeOption.textContent = `${typeIcons[type] || '📰'} ${type.charAt(0).toUpperCase() + type.slice(1)}s`;
        typeOption.disabled = true;
        typeOption.style.fontWeight = 'bold';
        sourceFilter.appendChild(typeOption);
        
        // Add individual sources
        typeSources.forEach(source => {
            const sourceOption = document.createElement('option');
            sourceOption.value = source.id;
            sourceOption.textContent = `  ${source.name}`;
            sourceFilter.appendChild(sourceOption);
        });
    });
}

function getFilteredContent() {
    const sourceTypeFilter = document.getElementById('sourceTypeFilter');
    const sourceFilter = document.getElementById('sourceFilter');
    
    if (!sourceTypeFilter || !sourceFilter) return allContent;
    
    const sourceType = sourceTypeFilter.value;
    const sourceId = sourceFilter.value;
    
    console.log('🔍 Filtering:', { sourceType, sourceId, totalContent: allContent.length });
    
    let filteredContent = [...allContent];
    
    // Filter by source type
    if (sourceType) {
        filteredContent = filteredContent.filter(item => item.source_type === sourceType);
    }
    
    // Filter by specific source
    if (sourceId && !sourceId.startsWith('type:')) {
        filteredContent = filteredContent.filter(item => item.source_id === parseInt(sourceId));
    }
    
    return filteredContent;
}

function filterContent() {
    const filteredContent = getFilteredContent();
    const sortedContent = applySorting(filteredContent);
    renderContentGrid(sortedContent);
}

function sortContent() {
    const filteredContent = getFilteredContent();
    const sortedContent = applySorting(filteredContent);
    renderContentGrid(sortedContent);
}

function applySorting(content) {
    const sortFilter = document.getElementById('sortFilter');
    if (!sortFilter) return content;
    
    const sortBy = sortFilter.value;
    let sortedContent = [...content];

    switch (sortBy) {
        case 'date':
            sortedContent.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
            break;
        case 'engagement':
            sortedContent.sort((a, b) => {
                const aEngagement = getEngagementScore(a);
                const bEngagement = getEngagementScore(b);
                return bEngagement - aEngagement;
            });
            break;
        case 'relevance':
            sortedContent.sort((a, b) => {
                const aScore = (a.title?.length || 0) + (a.description?.length || 0);
                const bScore = (b.title?.length || 0) + (b.description?.length || 0);
                return bScore - aScore;
            });
            break;
    }

    return sortedContent;
}

function getEngagementScore(content) {
    if (!content.engagement_metrics) return 0;
    
    let score = 0;
    const metrics = content.engagement_metrics;
    
    if (metrics.likes) score += metrics.likes;
    if (metrics.retweets) score += metrics.retweets * 2;
    if (metrics.comments) score += metrics.comments * 3;
    if (metrics.upvotes) score += metrics.upvotes;
    
    return score;
}

// Form handling functions
async function handleAddSource(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('sourceName')?.value || '',
        url: document.getElementById('sourceUrl')?.value || '',
        source_type: document.getElementById('sourceType')?.value || '',
        description: document.getElementById('sourceDescription')?.value || ''
    };

    try {
        await fetchAPI('/api/sources', {
            method: 'POST',
            body: JSON.stringify(formData)
        });

        showNotification('Source added successfully!', 'success');
        hideModal('addSourceModal');
        
        const form = document.getElementById('addSourceForm');
        if (form) form.reset();
        
        loadContent(); // Refresh content
    } catch (error) {
        console.error('Error adding source:', error);
        showNotification('Error adding source', 'error');
    }
}

async function handleGenerateSummary() {
    if (selectedContentIds.length === 0) {
        showNotification('Please select at least one content item', 'warning');
        return;
    }

    const analysisType = document.getElementById('analysisType')?.value || 'custom';
    let prompt = '';

    if (analysisType === 'custom') {
        prompt = document.getElementById('customPrompt')?.value || '';
        if (!prompt.trim()) {
            showNotification('Please enter a custom prompt', 'warning');
            return;
        }
    }

    try {
        let endpoint = '/api/summarize';
        let requestBody = {
            content_ids: selectedContentIds,
            prompt: prompt || 'Analyze the selected content and provide insights.'
        };

        if (analysisType !== 'custom') {
            endpoint = `/api/summarize/${analysisType}`;
            requestBody = selectedContentIds;
        }

        const summary = await fetchAPI(endpoint, {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });

        showSummaryResults(summary);
        hideModal('summarizeModal');
    } catch (error) {
        console.error('Error generating summary:', error);
        showNotification('Error generating summary', 'error');
    }
}

function showSummaryResults(summary) {
    const content = document.getElementById('summaryContent');
    if (!content) return;
    
    content.innerHTML = `
        <div class="mb-4">
            <h4 class="text-lg font-semibold mb-2">Analysis Results</h4>
            <div class="bg-gray-50 p-4 rounded-lg">
                <p class="text-sm text-gray-600 mb-2"><strong>Model Used:</strong> ${summary.ai_model || 'Unknown'}</p>
                <p class="text-sm text-gray-600 mb-2"><strong>Tokens Used:</strong> ${summary.tokens_used || 'Unknown'}</p>
                <p class="text-sm text-gray-600"><strong>Generated:</strong> ${formatDate(summary.created_at)}</p>
            </div>
        </div>
        <div class="prose">
            <h5 class="text-lg font-semibold mb-3">Summary</h5>
            <div class="whitespace-pre-wrap text-gray-700">${summary.summary_text}</div>
        </div>
    `;
    
    showModal('summaryResultsModal');
}

// Initialize the application
function initApp() {
    // Load initial content
    loadContent();
    
    // Set up event listeners
    setupEventListeners();
}

// Set up event listeners
function setupEventListeners() {
    // Modal controls
    const addSourceBtn = document.getElementById('addSourceBtn');
    if (addSourceBtn) addSourceBtn.addEventListener('click', () => showModal('addSourceModal'));
    
    const closeModalBtns = document.querySelectorAll('[id$="ModalBtn"]');
    closeModalBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.id.replace('close', '').replace('Btn', '');
            hideModal(modalId);
        });
    });
    
    // Form submissions
    const addSourceForm = document.getElementById('addSourceForm');
    if (addSourceForm) addSourceForm.addEventListener('submit', handleAddSource);
    
    const generateSummaryBtn = document.getElementById('generateSummaryBtn');
    if (generateSummaryBtn) generateSummaryBtn.addEventListener('click', handleGenerateSummary);
    
    const summarizeBtn = document.getElementById('summarizeBtn');
    if (summarizeBtn) summarizeBtn.addEventListener('click', () => showModal('summarizeModal'));
    
    // Filters
    const sourceTypeFilter = document.getElementById('sourceTypeFilter');
    if (sourceTypeFilter) sourceTypeFilter.addEventListener('change', filterContent);
    
    const sourceFilter = document.getElementById('sourceFilter');
    if (sourceFilter) sourceFilter.addEventListener('change', filterContent);
    
    const sortFilter = document.getElementById('sortFilter');
    if (sortFilter) sortFilter.addEventListener('change', sortContent);
    
    // Other controls
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) refreshBtn.addEventListener('click', loadContent);
    
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) loadMoreBtn.addEventListener('click', loadMoreContent);
}

// Start the app when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);
