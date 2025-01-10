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

async function searchProducts(query) {
showLoading();
try {
const response = await fetch(`http://localhost:8000/api/search?query=${encodeURIComponent(query)}`);
const data = await response.json();
displayProducts(data);
} catch (error) {
console.error('Error fetching products:', error);
productsGrid.innerHTML = '<p>Error loading products. Please try again.</p>';
}
hideLoading();
}

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
const query = searchInput.value.trim();
if (query) {
searchProducts(query);
}
});

searchInput.addEventListener('keypress', (e) => {
if (e.key === 'Enter') {
const query = searchInput.value.trim();
if (query) {
searchProducts(query);
}
}
});
});