// JavaScript principal para o sistema Mavi Suporte

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('error');
                    isValid = false;
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                showNotification('Por favor, preencha todos os campos obrigatórios.', 'error');
            }
        });
    });

    // Real-time form validation
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.hasAttribute('required') && !this.value.trim()) {
                this.classList.add('error');
            } else {
                this.classList.remove('error');
            }
        });

        input.addEventListener('input', function() {
            if (this.classList.contains('error') && this.value.trim()) {
                this.classList.remove('error');
            }
        });
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Mobile menu toggle (if needed)
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }

    // Auto-refresh for dashboard (if on dashboard page)
    if (window.location.pathname.includes('dashboard')) {
        setInterval(() => {
            // Refresh metrics without full page reload
            refreshMetrics();
        }, 30000); // 30 seconds
    }

    // Copy ticket ID functionality
    const copyButtons = document.querySelectorAll('.copy-ticket-id');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const ticketId = this.dataset.ticketId;
            navigator.clipboard.writeText(ticketId).then(() => {
                showNotification('ID do ticket copiado!', 'success');
            });
        });
    });

    // Search functionality
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const searchableItems = document.querySelectorAll('.searchable-item');
            
            searchableItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
});

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)}"></i>
        ${message}
        <button class="alert-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    const container = document.querySelector('.main-content .container');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function refreshMetrics() {
    fetch('/dashboard/api/metrics')
        .then(response => response.json())
        .then(data => {
            // Update metric values
            const metricValues = document.querySelectorAll('.metric-value');
            if (metricValues.length >= 4) {
                metricValues[0].textContent = data.total_tickets;
                metricValues[1].textContent = data.pendentes;
                metricValues[2].textContent = data.em_andamento;
                metricValues[3].textContent = data.concluidos;
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar métricas:', error);
        });
}

// Form submission with loading state
function submitFormWithLoading(form, button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<div class="spinner"></div> Processando...';
    button.disabled = true;
    
    // Restore button after 3 seconds if form doesn't submit
    setTimeout(() => {
        if (button.disabled) {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }, 3000);
}

// Ticket status update (for admin)
function updateTicketStatus(ticketId, newStatus) {
    const formData = new FormData();
    formData.append('ticket_id', ticketId);
    formData.append('status', newStatus);
    
    fetch('/admin/update-ticket-status', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Status do ticket atualizado com sucesso!', 'success');
            // Refresh the page or update the UI
            location.reload();
        } else {
            showNotification('Erro ao atualizar status do ticket.', 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showNotification('Erro ao atualizar status do ticket.', 'error');
    });
}

// Export functions for global use
window.showNotification = showNotification;
window.submitFormWithLoading = submitFormWithLoading;
window.updateTicketStatus = updateTicketStatus;

