class ErrorHandler {
    constructor() {
        this.errorContainer = document.querySelector('.error-container');
        this.errorMessages = document.querySelector('.error-messages');
    }

    showErrors(errors) {
        // Clear existing errors
        this.clearErrors();

        // Create and show new error messages
        Object.entries(errors).forEach(([field, messages]) => {
            const errorMessage = this.createErrorMessage(field, messages);
            this.errorMessages.appendChild(errorMessage);
            
            // Highlight related input field
            this.highlightField(field);
        });

        // Show error container with animation
        this.errorContainer.style.display = 'block';
        this.errorMessages.classList.add('animate__fadeIn');

        // Auto-hide errors after 5 seconds
        setTimeout(() => this.clearErrors(), 5000);
    }

    createErrorMessage(field, messages) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'error-message';

        const content = document.createElement('div');
        content.className = 'error-content';

        const fieldName = document.createElement('div');
        fieldName.className = 'error-field';
        fieldName.textContent = field.replace(/_/g, ' ');

        const messageText = document.createElement('div');
        messageText.className = 'error-text';
        messageText.textContent = Array.isArray(messages) ? messages[0] : messages;

        content.appendChild(fieldName);
        content.appendChild(messageText);

        const closeButton = document.createElement('span');
        closeButton.className = 'error-close';
        closeButton.innerHTML = '&times;';
        closeButton.onclick = () => messageDiv.remove();

        messageDiv.appendChild(content);
        messageDiv.appendChild(closeButton);

        return messageDiv;
    }

    highlightField(field) {
        // Map error fields to input elements
        const fieldMap = {
            'category_name': '.category-options input:checked',
            'currency': '#currency',
            'min_current_price': '#minPrice',
            'max_current_price': '#maxPrice'
        };

        const selector = fieldMap[field];
        if (selector) {
            const element = document.querySelector(selector);
            if (element) {
                element.classList.add('input-error');
                
                // Create tooltip if doesn't exist
                if (!element.nextElementSibling?.classList.contains('error-tooltip')) {
                    const tooltip = document.createElement('div');
                    tooltip.className = 'error-tooltip';
                    element.parentNode.insertBefore(tooltip, element.nextSibling);
                }
            }
        }
    }

    clearErrors() {
        // Clear error messages
        this.errorMessages.innerHTML = '';
        
        // Remove error highlights
        document.querySelectorAll('.input-error').forEach(element => {
            element.classList.remove('input-error');
        });
        
        // Remove tooltips
        document.querySelectorAll('.error-tooltip').forEach(tooltip => {
            tooltip.remove();
        });
    }
}

// Initialize error handler
const errorHandler = new ErrorHandler();

document.addEventListener('DOMContentLoaded', function() {
    const searchContainer = document.querySelector('.search-container');
    const searchInput = document.querySelector('.search-input');
    const searchButton = document.querySelector('.search-button');
    const productsGrid = document.querySelector('.products-grid');
    const modal = document.querySelector('.modal');
    const closeModal = document.querySelector('.close-modal');
    const loadingSpinner = document.querySelector('.loading-spinner');

    function showLoading() {
        loadingSpinner.style.display = 'block';
        productsGrid.innerHTML = '';
    }

    function hideLoading() {
        loadingSpinner.style.display = 'none';
    }

    // async function fetchProducts(query, filter={}) {
    //     showLoading();
    //     try {
    //         const response = await fetch(`http://localhost:8000/api/search?query=${encodeURIComponent(query)}`);
    //         const data = await response.json();
    //         displayProducts(data);
    //     } catch (error) {
    //         console.error('Error fetching products:', error);
    //         productsGrid.innerHTML = '<p>Error loading products. Please try again.</p>';
    //     }
    //     hideLoading();
    // }

    async function fetchProducts() {
        showLoading();

        const filters = {
            currency: document.getElementById('currency').value,
            priceRange: {
                min: parseInt(document.getElementById('minPrice').value) || null,
                max: parseInt(document.getElementById('maxPrice').value) || null
            },
            category_name: $('#categories-dropdown').dropdown('get values').join(','), // For Semantic UI dropdown
            status: document.querySelector('input[name="status"]:checked').value,
            region: document.getElementById('region')?.value,
            shop_name: document.querySelector('select[name="shop"]')?.value
        };
    
        // Get the current search query
        const query = document.querySelector('.search-input').value;

        try {
            // Build query parameters
            const params = new URLSearchParams({
                query: query || ''
            });
    
            // Add filter parameters if they exist
            if (filters.category_name) {
                params.append('category_name', filters.category_name);
            }
            
            if (filters.currency) {
                params.append('currency', filters.currency);
            }
            
            if (filters.priceRange?.min) {
                params.append('min_current_price', filters.priceRange.min);
            }
            
            if (filters.priceRange?.max) {
                params.append('max_current_price', filters.priceRange.max);
            }
            
            if (filters.update_date) {
                params.append('update_date', filters.update_date);
            }
            
            if (filters.shop_name) {
                params.append('shop_name', filters.shop_name);
            }
            
            if (filters.status && filters.status !== '') {
                params.append('status', filters.status);
            }
            
            if (filters.region) {
                params.append('region', filters.region);
            }
            
            if (filters.off_percent) {
                params.append('off_percent', filters.off_percent);
            }
    
            const response = await fetch(`http://localhost:8000/api/semantic-search?${params.toString()}`);
            
            const data = await response.json();
            if (!response.ok) {
                errorHandler.showErrors(data);
                return;
            }
            
            displayProducts(data);
        } catch (error) {
            console.log(error);
            errorHandler.showErrors({
                'general': ['An unexpected error occurred. Please try again.']
            });
        } finally {
            hideLoading();
        }
    }

    window.fetchProducts = fetchProducts;

    function displayProducts(products) {
        searchContainer.classList.add('results-shown');
        productsGrid.innerHTML = '';

        products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card animate__animated animate__fadeIn';

            card.innerHTML = `
<img src="${product.images[0]}" alt="${product.name}" class="product-image">
<div class="product-info">
<h3 class="product-name">${product.name}</h3>
<div class="product-sizes">
${product.sizes.map(size => `<span class="size-tag">${size}</span>`).join('')}
</div>
</div>
`;

            card.addEventListener('click', () => showProductDetails(product));
            productsGrid.appendChild(card);
        });
    }

    function showProductDetails(product) {
        const modalImages = document.querySelector('.modal-images');
        const modalDetails = document.querySelector('.modal-details');

        modalImages.innerHTML = product.images.map((img, index) => `
<img src="${img}" alt="${product.name}" class="modal-image ${index === 0 ? 'selected' : ''}" 
onclick="this.parentElement.querySelectorAll('.modal-image').forEach(img => img.classList.remove('selected')); 
this.classList.add('selected');">
`).join('');

        let details = `
<h2>${product.name}</h2>
<div class="price-tag">
<span class="current-price">${product.currency} ${product.current_price}</span>
${product.old_price ? `
<span class="old-price">${product.currency} ${product.old_price}</span>
<span class="discount-badge">${product.off_percent}% OFF</span>
` : ''}
</div>
`;

        if (product.colors && product.colors.length > 0) {
            details += `
<div class="color-swatches">
${product.colors.map(color => `
<div class="color-swatch" style="background-color: ${color}"></div>
`).join('')}
</div>
`;
        }

        const fields = {
            'Description': product.description,
            'Material': product.material,
            'Brand': product.brand_name,
            'Category': product.category_name,
            'Gender': product.gender_name,
            'Shop': product.shop_name,
            'Status': product.status,
            'Region': product.region
        };

        for (const [key, value] of Object.entries(fields)) {
            if (value) {
                details += `<p><strong>${key}:</strong> ${value}</p>`;
            }
        }

        if (product.link) {
            details += `
<a href="${product.link}" target="_blank" style="
display: inline-block;
margin-top: 20px;
padding: 10px 20px;
background: #007bff;
color: white;
text-decoration: none;
border-radius: 5px;
">View on Store</a>
`;
        }

        modalDetails.innerHTML = details;
        modal.style.display = 'block';
    }

    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    searchButton.addEventListener('click', () => {
        fetchProducts();
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            fetchProducts();
        }
    });
});