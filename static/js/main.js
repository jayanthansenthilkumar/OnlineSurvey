/**
 * Main JavaScript file for SurveyPulse
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add fade-out effect to flash messages
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.classList.add('fade');
                setTimeout(() => {
                    message.remove();
                }, 500);
            }, 5000);
        });
    }

    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath && currentPath.includes(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        } else if (currentPath === '/' && linkPath === '/') {
            link.classList.add('active');
        }
    });
    
    // Add loading spinner to all form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                // Save original button text
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                // Add spinner and "Processing..." text
                submitBtn.innerHTML = '<span class="spinner"></span>Processing...';
                submitBtn.disabled = true;
                
                // If form submission takes too long, restore button after 10 seconds
                setTimeout(() => {
                    if (submitBtn.disabled && submitBtn.innerHTML.includes('spinner')) {
                        submitBtn.innerHTML = submitBtn.dataset.originalText;
                        submitBtn.disabled = false;
                    }
                }, 10000);
            }
        });
    });

    // Add confirmation for delete actions
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Add hover effect to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            if (!card.classList.contains('no-hover')) {
                card.style.transform = 'translateY(-5px)';
                card.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.1)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            if (!card.classList.contains('no-hover')) {
                card.style.transform = '';
                card.style.boxShadow = '';
            }
        });
    });
});