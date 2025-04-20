// Wait for document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle quantity input changes
    const quantityInputs = document.querySelectorAll('.quantity-input');
    if (quantityInputs) {
        quantityInputs.forEach(input => {
            input.addEventListener('change', function() {
                const min = parseInt(this.getAttribute('min') || 1);
                const max = parseInt(this.getAttribute('max') || 100);
                let val = parseInt(this.value) || 1;
                
                // Ensure value is within bounds
                if (val < min) val = min;
                if (val > max) val = max;
                
                this.value = val;
                
                // If this is in a form, submit it to update cart
                const form = this.closest('form[data-update-cart]');
                if (form) {
                    form.submit();
                }
            });
        });
    }

    // Product gallery image selection
    const productThumbnails = document.querySelectorAll('.product-thumbnail');
    const mainProductImage = document.querySelector('.main-product-image');
    
    if (productThumbnails && mainProductImage) {
        productThumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                const imgSrc = this.getAttribute('data-img-src');
                mainProductImage.setAttribute('src', imgSrc);
                
                // Update active state
                productThumbnails.forEach(item => item.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Category filter on product page
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) form.submit();
        });
    }

    // Search form submission
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    
    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', function(e) {
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                return false;
            }
        });
    }

    // Payment method selection
    const paymentMethods = document.querySelectorAll('.payment-method');
    if (paymentMethods) {
        paymentMethods.forEach(method => {
            method.addEventListener('change', function() {
                const paymentDetails = document.querySelectorAll('.payment-details');
                paymentDetails.forEach(detail => {
                    detail.style.display = 'none';
                });
                
                const selectedMethod = document.getElementById(this.getAttribute('data-details'));
                if (selectedMethod) {
                    selectedMethod.style.display = 'block';
                }
            });
        });
    }

    // Add to cart animation
    const addToCartBtn = document.querySelector('.add-to-cart-btn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function() {
            // Create the animation element
            const notification = document.createElement('div');
            notification.className = 'cart-notification';
            notification.innerHTML = '<i class="fas fa-check"></i> Added to cart!';
            document.body.appendChild(notification);
            
            // Show and then remove after animation
            setTimeout(() => {
                notification.classList.add('show');
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        document.body.removeChild(notification);
                    }, 300);
                }, 2000);
            }, 10);
        });
    }

    // Form validation for checkout
    const checkoutForm = document.getElementById('checkoutForm');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            const form = this;
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    }
});

// Function to update subtotal when quantity changes
function updateSubtotal(productId, price) {
    const quantityInput = document.getElementById(`quantity-${productId}`);
    const subtotalElement = document.getElementById(`subtotal-${productId}`);
    
    if (quantityInput && subtotalElement) {
        const quantity = parseInt(quantityInput.value) || 1;
        const subtotal = (quantity * price).toFixed(2);
        subtotalElement.textContent = '₹' + subtotal;
    }
}

// Function to confirm product deletion
function confirmDelete(productName) {
    return confirm(`Are you sure you want to delete "${productName}"?`);
}
