// Contact Form Integration with Backend API
class ContactFormHandler {
    constructor(formSelector = '#contact-form') {
        this.form = document.querySelector(formSelector);
        this.submitBtn = this.form?.querySelector('button[type="submit"]');
        this.replyMessage = document.getElementById('formReply');
        this.replyIcon = document.getElementById('replyIcon');
        this.replyTitle = document.getElementById('replyTitle');
        this.replyText = document.getElementById('replyText');

        if (this.form) {
            this.init();
        }
    }

    init() {
        // Production: rely on native HTML5 validation (required fields in HTML)
        console.debug('[contact-form] initialized, attaching submit handler', this.form);
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    // Resolve the API base URL in a way that works for local dev and production.
    // - If window.API_BASE is provided (e.g., via a script tag), use it.
    // - If running locally on port 8000 (static server), target FastAPI on 8001.
    // - Otherwise, use the current origin (expecting a reverse proxy in production).
    getApiBase() {
        try {
            if (window.API_BASE && typeof window.API_BASE === 'string') {
                return window.API_BASE.replace(/\/$/, '');
            }
        } catch (_) {}
        const loc = window.location;
        if (loc.port === '8000') {
            return 'http://127.0.0.1:8001';
        }
        return `${loc.protocol}//${loc.host}`;
    }

    async handleSubmit(e) {
        e.preventDefault();
        console.debug('[contact-form] submit intercepted');

        if (!this.form) {
            console.error('[contact-form] form not found');
            return;
        }

        // Get form data
        const formData = new FormData(this.form);
        const data = {
            name: (formData.get('Name') || '').toString().trim(),
            email: (formData.get('E-mail') || '').toString().trim(),
            message: (formData.get('Message') || '').toString().trim()
        };

        // Add optional fields
        const company = formData.get('Company');
        const phone = formData.get('Phone');
        if (company && company.toString().trim()) {
            data.company = company.toString().trim();
        }
        if (phone && phone.toString().trim()) {
            data.phone = phone.toString().trim();
        }

        console.debug('[contact-form] payload', data);

        // Basic client-side validation
        if (!this.validateForm(data)) {
            return;
        }

        // Disable submit button and show loading
        this.setLoadingState(true);

        try {
            const apiUrl = `${this.getApiBase()}/api/contacts/`;
            console.log('[contact-form] sending request to:', apiUrl);

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            console.log('[contact-form] response status:', response.status);
            console.log('[contact-form] response ok:', response.ok);

            if (response.ok) {
                const result = await response.json();
                console.log('[contact-form] success response:', result);
                this.showSuccess('Message sent successfully');
                this.form.reset();
            } else {
                console.log('[contact-form] error response status:', response.status);
                try {
                    const error = await response.json();
                    console.log('[contact-form] error response body:', error);
                    this.showError('There was an error sending your message');
                } catch (parseError) {
                    console.log('[contact-form] could not parse error response:', parseError);
                    this.showError('There was an error sending your message');
                }
            }
        } catch (error) {
            console.error('[contact-form] network/connection error:', error);

            // Check if it's a network connectivity issue
            if (!navigator.onLine) {
                console.log('[contact-form] user is offline');
                this.showError('Connection error. Please check your internet connection and try again.');
            } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
                console.log('[contact-form] network request failed');
                this.showError('Connection error. Please check your internet connection and try again.');
            } else {
                console.log('[contact-form] unknown error type:', error.name);
                this.showError('Connection error. Please try again later.');
            }
        } finally {
            this.setLoadingState(false);
        }
    }

    validateForm(data) {
        // Clear previous errors
        this.clearErrors();

        let isValid = true;
        const errors = [];

        // Name validation (minimum 2 characters, required)
        if (!data.name || data.name.length < 2) {
            errors.push('Name must be at least 2 characters long');
            isValid = false;
            console.log('[contact-form] validation failed: name too short', data.name);
        }

        // Email validation (required, proper email format)
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!data.email) {
            errors.push('Email address is required');
            isValid = false;
            console.log('[contact-form] validation failed: email missing');
        } else if (!emailRegex.test(data.email)) {
            errors.push('Please enter a valid email address (format: user@domain.com)');
            isValid = false;
            console.log('[contact-form] validation failed: invalid email format', data.email);
        }

        // Message validation (minimum 3 characters, required)
        if (!data.message || data.message.length < 3) {
            errors.push('Message must be at least 3 characters long');
            isValid = false;
            console.log('[contact-form] validation failed: message too short', data.message);
        }

        // Phone and Company are optional - no validation needed
        console.log('[contact-form] validation result:', isValid ? 'PASSED' : 'FAILED', { errors: errors.length });

        if (!isValid) {
            this.showError(errors.join('<br>'));
        }

        return isValid;
    }

    parseError(error) {
        if (error.detail) {
            if (Array.isArray(error.detail)) {
                return error.detail.map(err => {
                    if (err.loc && err.msg) {
                        const field = err.loc[err.loc.length - 1];
                        return `${field}: ${err.msg}`;
                    }
                    return err.msg || 'Validation error';
                }).join('<br>');
            }
            return error.detail;
        }
        return error.message || 'An error occurred. Please try again.';
    }

    setLoadingState(loading) {
        if (this.submitBtn) {
            this.submitBtn.disabled = loading;
            const btnCaption = this.submitBtn.querySelector('.btn-caption');
            if (btnCaption) {
                btnCaption.textContent = loading ? 'Sending...' : 'Send Message';
            }
        }
    }

    showSuccess(message) {
        this.showReply('success', 'Done!', message);
    }

    showError(message) {
        this.showReply('error', 'Error', message);
    }

    showReply(type, title, message) {
        if (this.replyMessage) {
            // Reset classes
            this.replyMessage.className = 'form__reply centered text-center';

            if (type === 'success') {
                this.replyMessage.classList.add('success');
                if (this.replyIcon) {
                    this.replyIcon.className = 'ph-bold ph-smiley reply__icon';
                }
            } else {
                this.replyMessage.classList.add('error');
                if (this.replyIcon) {
                    this.replyIcon.className = 'ph-bold ph-x-circle reply__icon';
                }
            }

            if (this.replyTitle) {
                this.replyTitle.textContent = title;
            }

            if (this.replyText) {
                this.replyText.innerHTML = message;
            }

            this.replyMessage.style.display = 'block';
            // Ensure the user actually sees the feedback
            try { this.replyMessage.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (_) {}

            // Auto-hide messages after 4 seconds
            setTimeout(() => {
                this.replyMessage.style.display = 'none';
            }, 4000);
        }
    }

    clearErrors() {
        if (this.replyMessage) {
            this.replyMessage.style.display = 'none';
        }
    }
}

// Initialize contact form when DOM is ready or if already loaded
(function initContactForm(){
    const start = () => {
        try {
            new ContactFormHandler();
        } catch (e) {
            console.error('Failed to initialize ContactFormHandler:', e);
        }
    };
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start, { once: true });
    } else {
        // DOM is already parsed at this point (scripts loaded at end of body)
        start();
    }
})();

// Export for potential use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ContactFormHandler;
}