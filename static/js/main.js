document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Cart quantity controls
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    if (quantityInputs) {
        quantityInputs.forEach(input => {
            const minusBtn = input.parentElement.querySelector('.quantity-minus');
            const plusBtn = input.parentElement.querySelector('.quantity-plus');
            
            if (minusBtn) {
                minusBtn.addEventListener('click', function() {
                    let value = parseInt(input.value);
                    if (value > 1) {
                        input.value = value - 1;
                        triggerChange(input);
                    }
                });
            }
            
            if (plusBtn) {
                plusBtn.addEventListener('click', function() {
                    let value = parseInt(input.value);
                    input.value = value + 1;
                    triggerChange(input);
                });
            }
        });
    }
    
    function triggerChange(input) {
        // Create and dispatch a change event
        const event = new Event('change', { bubbles: true });
        input.dispatchEvent(event);
        
        // If this is in the cart, auto-submit the update form
        const updateForm = input.closest('.cart-update-form');
        if (updateForm) {
            updateForm.submit();
        }
    }
    
    // Product filter on products page
    const categoryLinks = document.querySelectorAll('.category-filter');
    const searchForm = document.getElementById('product-search-form');
    
    if (categoryLinks) {
        categoryLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const category = this.dataset.category;
                
                // Get the current URL
                let url = new URL(window.location.href);
                
                // Update the category parameter
                if (category) {
                    url.searchParams.set('category', category);
                } else {
                    url.searchParams.delete('category');
                }
                
                // Navigate to the new URL
                window.location.href = url.toString();
            });
        });
    }
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const searchInput = this.querySelector('input[name="search"]');
            if (!searchInput.value.trim()) {
                return;
            }
            
            // Get the current URL
            let url = new URL(window.location.href);
            
            // Update the search parameter
            url.searchParams.set('search', searchInput.value);
            
            // Navigate to the new URL
            window.location.href = url.toString();
        });
    }
    
    // Product carousel initialization for product detail page
    const productCarousel = document.getElementById('productCarousel');
    if (productCarousel) {
        new bootstrap.Carousel(productCarousel, {
            interval: 5000
        });
    }
    
    // Address copy functionality on checkout page
    const sameAsShipping = document.getElementById('same-as-shipping');
    const shippingAddress = document.getElementById('shipping_address');
    const billingAddress = document.getElementById('billing_address');
    
    if (sameAsShipping && shippingAddress && billingAddress) {
        sameAsShipping.addEventListener('change', function() {
            if (this.checked) {
                billingAddress.value = shippingAddress.value;
                billingAddress.disabled = true;
            } else {
                billingAddress.disabled = false;
            }
        });
        
        shippingAddress.addEventListener('input', function() {
            if (sameAsShipping.checked) {
                billingAddress.value = this.value;
            }
        });
    }
    
    // Add animation classes
    const fadeElements = document.querySelectorAll('.should-fade');
    if (fadeElements) {
        fadeElements.forEach(element => {
            element.classList.add('fade-in');
        });
    }
});
