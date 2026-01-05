// Client-side JavaScript for Dessertable

document.addEventListener('DOMContentLoaded', function() {
    // Get form and button elements
    const searchForm = document.getElementById('searchForm');
    const searchButton = document.getElementById('searchButton');
    const zipCodeInput = document.getElementById('zip_code');

    if (searchForm) {
        // Form submission handler
        searchForm.addEventListener('submit', function(event) {
            // Validate zip code
            const zipCode = zipCodeInput.value.trim();

            if (!zipCode) {
                event.preventDefault();
                alert('Please enter a zip code');
                zipCodeInput.focus();
                return false;
            }

            if (!/^\d{5}$/.test(zipCode)) {
                event.preventDefault();
                alert('Please enter a valid 5-digit zip code');
                zipCodeInput.focus();
                return false;
            }

            // Show loading state
            if (searchButton) {
                searchButton.classList.add('loading');
                searchButton.disabled = true;
            }
        });

        // Zip code input validation (only allow digits)
        if (zipCodeInput) {
            zipCodeInput.addEventListener('input', function(e) {
                // Remove non-digit characters
                this.value = this.value.replace(/\D/g, '');

                // Limit to 5 digits
                if (this.value.length > 5) {
                    this.value = this.value.slice(0, 5);
                }
            });
        }
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
