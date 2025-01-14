// document.addEventListener('DOMContentLoaded', function() {
//     const filterToggle = document.querySelector('.filter-toggle');
//     const filterPanel = document.querySelector('.filter-panel');
//     const productsGrid = document.querySelector('.products-grid');
//     let isFilterPanelOpen = false;

//     filterToggle.addEventListener('click', function() {
//         isFilterPanelOpen = !isFilterPanelOpen;
//         filterPanel.classList.toggle('open');
//         productsGrid.classList.toggle('shifted');

//         // Rotate filter icon
//         const filterIcon = filterToggle.querySelector('i');
//         filterIcon.style.transform = isFilterPanelOpen ? 'rotate(180deg)' : 'rotate(0deg)';
//         filterIcon.style.transition = 'transform 0.3s ease';
//     });

//     // Fetch and populate currencies
//     async function fetchCurrencies() {
//         try {
//             const response = await fetch('/api/lists');
//             if (!response.ok) throw new Error('Failed to fetch currencies');
//             const data = await response.json();

//             const currencySelect = document.getElementById('currency');
//             // first remove current options from the currency list
//             currencySelect.innerHTML = '';
//             data.currencies.forEach(currency => {
//                 const option = document.createElement('option');
//                 option.value = currency;
//                 option.textContent = currency;
//                 currencySelect.appendChild(option);
//             });
//             // add a default option which value is ""
//             const defaultOption = document.createElement('option');
//             defaultOption.value = "";
//             defaultOption.textContent = "Select currency";
//             currencySelect.insertBefore(defaultOption, currencySelect.firstChild);
//             // select this option by default
//             currencySelect.selectedIndex = 0;
//         } catch (error) {
//             console.error('Error fetching currencies:', error);
//         }
//     }

//     fetchCurrencies();

//     // Connect price slider with input fields
//     const minPriceInput = document.getElementById('minPrice');
//     const maxPriceInput = document.getElementById('maxPrice');

//     // Handle apply filters
//     const applyFiltersButton = document.querySelector('.apply-filters');
//     applyFiltersButton.addEventListener('click', function() {
//         // Collect filter values
//         const filters = {
//             priceRange: {
//                 min: parseInt(minPriceInput.value),
//                 max: parseInt(maxPriceInput.value)
//             },
//             categories: Array.from(document.querySelectorAll('.category-options input:checked'))
//                 .map(input => input.value),
//             status: document.querySelector('.status-options input:checked').value
//         };

//         // Here you can implement the filter application logic
//         console.log('Applied filters:', filters);

//         // Close filter panel after applying
//         filterPanel.classList.remove('open');
//         productsGrid.classList.remove('shifted');
//         isFilterPanelOpen = false;
//         filterToggle.querySelector('i').style.transform = 'rotate(0deg)';
//     });
// });

document.addEventListener('DOMContentLoaded', function() {
    const filterToggle = document.querySelector('.filter-toggle');
    const filterPanel = document.querySelector('.filter-panel');
    const productsGrid = document.querySelector('.products-grid');
    let isFilterPanelOpen = false;
    
    filterToggle.addEventListener('click', function() {
    isFilterPanelOpen = !isFilterPanelOpen;
    filterPanel.classList.toggle('open');
    productsGrid.classList.toggle('shifted');
    
    const filterIcon = filterToggle.querySelector('i');
    filterIcon.style.transform = isFilterPanelOpen ? 'rotate(180deg)' : 'rotate(0deg)';
    filterIcon.style.transition = 'transform 0.3s ease';
    });
    
    // Handle apply filters
    const applyFiltersButton = document.querySelector('.apply-filters');
    applyFiltersButton.addEventListener('click', function() {
    // Collect filter values
    const filters = {
    priceRange: {
    min: parseInt(document.getElementById('minPrice').value) || null,
    max: parseInt(document.getElementById('maxPrice').value) || null
    },
    currency: document.getElementById('currency').value,
    region: document.getElementById('region').value,
    categories: Array.from(document.querySelectorAll('input[name="categories"]:checked'))
    .map(input => input.value),
    shops: Array.from(document.querySelectorAll('input[name="shops"]:checked'))
    .map(input => input.value),
    status: document.querySelector('input[name="status"]:checked').value
    };
    
    // Send filters to server
    applyFilters(filters);
    
    // Close filter panel
    filterPanel.classList.remove('open');
    productsGrid.classList.remove('shifted');
    isFilterPanelOpen = false;
    filterToggle.querySelector('i').style.transform = 'rotate(0deg)';
    });
    
    async function applyFilters(filters) {
    try {
    const response = await fetch('/api/filter-products', {
    method: 'POST',
    headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': '{{ csrf_token }}'
    },
    body: JSON.stringify(filters)
    });
    
    if (!response.ok) throw new Error('Failed to apply filters');
    
    const data = await response.json();
    updateProductsGrid(data.products);
    } catch (error) {
    console.error('Error applying filters:', error);
    }
    }
    
    function updateProductsGrid(products) {
    // Implementation of updating the products grid
    // This should match your existing product display logic
    }
    });