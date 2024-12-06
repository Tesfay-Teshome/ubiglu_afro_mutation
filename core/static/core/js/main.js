// Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Project image preview
    const imageInput = document.querySelector('#id_image');
    const imagePreview = document.querySelector('#image-preview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Project delete confirmation
    const deleteButtons = document.querySelectorAll('.delete-project');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this project?')) {
                e.preventDefault();
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Price formatting
    const priceInput = document.querySelector('#id_price');
    if (priceInput) {
        priceInput.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    }

    // Category filter
    const categorySelect = document.querySelector('#category-filter');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            const category = this.value;
            const projects = document.querySelectorAll('.project-card');
            
            projects.forEach(project => {
                if (category === '' || project.dataset.category === category) {
                    project.style.display = 'block';
                } else {
                    project.style.display = 'none';
                }
            });
        });
    }

    // Scroll to top button
    const scrollButton = document.querySelector('#scroll-to-top');
    if (scrollButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 100) {
                scrollButton.style.display = 'block';
            } else {
                scrollButton.style.display = 'none';
            }
        });

        scrollButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Loading spinner
    const loadingSpinner = document.querySelector('#loading-spinner');
    if (loadingSpinner) {
        window.addEventListener('load', function() {
            loadingSpinner.style.display = 'none';
        });
    }

    // Profile picture preview
    const profilePicInput = document.querySelector('#id_profile_picture');
    const profilePicPreview = document.querySelector('#profile-pic-preview');
    
    if (profilePicInput && profilePicPreview) {
        profilePicInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePicPreview.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Payment processing
    const paymentForm = document.querySelector('#payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitButton = paymentForm.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.textContent = 'Processing...';

            try {
                // Add your payment processing logic here
                await processPayment();
                window.location.href = '/payment/success/';
            } catch (error) {
                console.error('Payment failed:', error);
                alert('Payment failed. Please try again.');
                submitButton.disabled = false;
                submitButton.textContent = 'Pay Now';
            }
        });
    }
});

// Helper function for payment processing
async function processPayment() {
    // Implement your payment processing logic here
    return new Promise((resolve) => {
        setTimeout(resolve, 2000); // Simulated delay
    });
}
