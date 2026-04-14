/*! Blog Templates JavaScript - Professional Interactions
 * Matching NekwasaR Portfolio Brand
 * ------------------------------------------------ */

/**
 * Blog Templates JavaScript - Core functionality for all blog templates
 * Provides smooth interactions, social sharing, video controls, and more
 */

(function () {
    'use strict';

    // Configuration
    const CONFIG = {
        smoothScrollDuration: 800,
        animationDuration: 600,
        socialShare: {
            twitter: 'https://twitter.com/intent/tweet?text=',
            linkedin: 'https://www.linkedin.com/sharing/share-offsite/?url=',
            facebook: 'https://www.facebook.com/sharer/sharer.php?u=',
            reddit: 'https://www.reddit.com/submit?url='
        },
        debug: false
    };

    // Utility Functions
    const Utils = {
        /**
         * Debounce function to limit function calls
         */
        debounce: function (func, wait, immediate) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    timeout = null;
                    if (!immediate) func(...args);
                };
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func(...args);
            };
        },

        /**
         * Check if element is in viewport
         */
        isInViewport: function (element) {
            const rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        },

        /**
         * Get current page URL
         */
        getCurrentURL: function () {
            return window.location.href;
        },

        /**
         * Get page title
         */
        getPageTitle: function () {
            return document.title;
        },

        /**
         * Log debug messages
         */
        debug: function (message, data) {
            if (CONFIG.debug) {
            }
        }
    };

    // Social Share Module
    const SocialShare = {
        init: function () {
            this.bindEvents();
            Utils.debug('Social Share initialized');
        },

        bindEvents: function () {
            // Share button clicks
            document.addEventListener('click', (e) => {
                const target = e.target.closest('.social-share-btn, [data-share]');
                if (target) {
                    e.preventDefault();
                    const platform = target.dataset.share || target.title.toLowerCase().includes('twitter') ? 'twitter' :
                        target.title.toLowerCase().includes('linkedin') ? 'linkedin' :
                            target.title.toLowerCase().includes('facebook') ? 'facebook' :
                                target.title.toLowerCase().includes('reddit') ? 'reddit' :
                                    target.title.toLowerCase().includes('copy') ? 'copy' : null;

                    if (platform) {
                        this.share(platform);
                    }
                }
            });
        },

        share: function (platform) {
            const url = encodeURIComponent(Utils.getCurrentURL());
            const title = encodeURIComponent(Utils.getPageTitle());
            const text = encodeURIComponent(document.querySelector('meta[name="description"]')?.content || title);

            let shareUrl = '';

            switch (platform) {
                case 'twitter':
                    shareUrl = `${CONFIG.socialShare.twitter}${text}&url=${url}`;
                    break;
                case 'linkedin':
                    shareUrl = `${CONFIG.socialShare.linkedin}${url}`;
                    break;
                case 'facebook':
                    shareUrl = `${CONFIG.socialShare.facebook}${url}`;
                    break;
                case 'reddit':
                    shareUrl = `${CONFIG.socialShare.reddit}${url}&title=${title}`;
                    break;
                case 'copy':
                    this.copyToClipboard();
                    return;
                default:
                    Utils.debug('Unknown share platform:', platform);
                    return;
            }

            // Open share window
            window.open(shareUrl, '_blank', 'width=600,height=400,scrollbars=yes,resizable=yes');

            Utils.debug('Shared to:', platform);
        },

        copyToClipboard: function () {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(Utils.getCurrentURL()).then(() => {
                    this.showCopyFeedback();
                });
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = Utils.getCurrentURL();
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                this.showCopyFeedback();
            }
        },

        showCopyFeedback: function () {
            const feedback = document.createElement('div');
            feedback.textContent = 'Link copied to clipboard!';
            feedback.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--accent);
                color: var(--t-opp-bright);
                padding: 1rem 2rem;
                border-radius: var(--_radius-m);
                z-index: 10000;
                font-family: var(--_font-default);
                font-size: 1.4rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                transform: translateX(100%);
                transition: transform 0.3s var(--_animbezier);
            `;

            document.body.appendChild(feedback);

            // Animate in
            setTimeout(() => {
                feedback.style.transform = 'translateX(0)';
            }, 10);

            // Animate out and remove
            setTimeout(() => {
                feedback.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    document.body.removeChild(feedback);
                }, 300);
            }, 2000);
        }
    };

    // Smooth Scrolling Module
    const SmoothScroll = {
        init: function () {
            this.bindEvents();
            Utils.debug('Smooth Scroll initialized');
        },

        bindEvents: function () {
            document.addEventListener('click', (e) => {
                const target = e.target.closest('a[href^="#"]');
                if (target && target.getAttribute('href') !== '#') {
                    e.preventDefault();
                    this.scrollToTarget(target.getAttribute('href'));
                }
            });
        },

        scrollToTarget: function (targetId) {
            const target = document.querySelector(targetId);
            if (target) {
                const offsetTop = target.offsetTop - 80; // Account for fixed headers

                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });

                // Update URL without jumping
                if (history.pushState) {
                    history.pushState(null, null, targetId);
                }

                Utils.debug('Scrolled to:', targetId);
            }
        }
    };

    // Reading Progress Module
    const ReadingProgress = {
        progressBar: null,

        init: function () {
            this.createProgressBar();
            this.bindEvents();
            Utils.debug('Reading Progress initialized');
        },

        createProgressBar: function () {
            this.progressBar = document.createElement('div');
            this.progressBar.id = 'reading-progress';
            this.progressBar.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 0%;
                height: 3px;
                background: linear-gradient(90deg, var(--accent), var(--secondary));
                z-index: 9999;
                transition: width 0.1s ease-out;
            `;
            document.body.appendChild(this.progressBar);
        },

        bindEvents: function () {
            window.addEventListener('scroll', Utils.debounce(() => {
                this.updateProgress();
            }, 100));
        },

        updateProgress: function () {
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight - windowHeight;
            const scrolled = window.scrollY;
            const progress = (scrolled / documentHeight) * 100;

            this.progressBar.style.width = Math.min(progress, 100) + '%';
        }
    };

    // Table of Contents Module
    const TableOfContents = {
        tocLinks: [],
        sections: [],

        init: function () {
            this.setupToc();
            this.bindEvents();
            Utils.debug('Table of Contents initialized');
        },

        setupToc: function () {
            this.tocLinks = Array.from(document.querySelectorAll('.toc-link'));
            this.sections = this.tocLinks.map(link => {
                return document.querySelector(link.getAttribute('href'));
            }).filter(section => section !== null);
        },

        bindEvents: function () {
            window.addEventListener('scroll', Utils.debounce(() => {
                this.highlightActiveSection();
            }, 100));

            // Initial highlight
            this.highlightActiveSection();
        },

        highlightActiveSection: function () {
            const scrollPos = window.scrollY + 100; // Offset for better UX

            let activeIndex = -1;
            for (let i = this.sections.length - 1; i >= 0; i--) {
                if (this.sections[i].offsetTop <= scrollPos) {
                    activeIndex = i;
                    break;
                }
            }

            // Update active states
            this.tocLinks.forEach((link, index) => {
                if (index === activeIndex) {
                    link.classList.add('active');
                    link.style.color = 'var(--t-accent)';
                } else {
                    link.classList.remove('active');
                    link.style.color = 'var(--t-medium)';
                }
            });
        }
    };

    // Animation Module
    const Animations = {
        observer: null,

        init: function () {
            this.setupIntersectionObserver();
            this.observeElements();
            Utils.debug('Animations initialized');
        },

        setupIntersectionObserver: function () {
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });
        },

        observeElements: function () {
            const elementsToAnimate = document.querySelectorAll(
                '.blog-card, .listing-item, .content-section, blockquote'
            );

            elementsToAnimate.forEach(element => {
                this.observer.observe(element);
            });
        }
    };

    // Newsletter Module
    const Newsletter = {
        init: function () {
            this.bindEvents();
            Utils.debug('Newsletter initialized');
        },

        bindEvents: function () {
            const form = document.getElementById('newsletterForm');
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleSubmission(form);
                });
            }
        },

        handleSubmission: function (form) {
            const formData = new FormData(form);
            const data = {
                name: formData.get('name') || document.getElementById('subscriberName')?.value || formData.get('email')?.split('@')[0],
                email: formData.get('email') || document.getElementById('subscriberEmail')?.value
            };

            // Show loading state
            const submitBtn = form.querySelector('.subscribe-btn') || form.querySelector('button[type="submit"]');
            if (!submitBtn) return;

            const originalText = submitBtn.textContent;
            submitBtn.innerHTML = '<i class="ph-bold ph-circle-notch" style="animation: spin 1s linear infinite;"></i> Subscribing...';
            submitBtn.disabled = true;

            // Simulate API call (replace with actual implementation)
            setTimeout(() => {
                this.showSuccessMessage(data.email);
                form.reset();
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                Utils.debug('Newsletter subscription:', data);
            }, 2000);
        },

        showSuccessMessage: function (email) {
            const message = document.getElementById('newsletterMessage') ||
                document.createElement('div');
            message.id = 'newsletterMessage';
            message.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <i class="ph-bold ph-check-circle" style="color: #22c55e; font-size: 4rem; margin-bottom: 1rem;"></i>
                    <h3 style="color: var(--t-bright); margin-bottom: 1rem;">Successfully Subscribed!</h3>
                    <p style="color: var(--t-medium);">Thank you for subscribing! We'll send the latest insights to ${email}.</p>
                </div>
            `;
            message.style.cssText = `
                background: var(--base);
                border: 1px solid var(--stroke-elements);
                border-radius: var(--_radius-xl);
                margin-top: 2rem;
                opacity: 0;
                transform: translateY(20px);
                transition: all 0.3s var(--_animbezier);
            `;

            if (!message.parentNode) {
                document.getElementById('newsletterForm')?.parentNode.appendChild(message);
            }

            // Animate in
            setTimeout(() => {
                message.style.opacity = '1';
                message.style.transform = 'translateY(0)';
            }, 10);

            // Remove after delay
            setTimeout(() => {
                message.style.opacity = '0';
                message.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    if (message.parentNode) {
                        message.parentNode.removeChild(message);
                    }
                }, 300);
            }, 5000);
        }
    };

    // Dark/Light Theme Toggle
    const ThemeToggle = {
        init: function () {
            this.bindEvents();
            Utils.debug('Theme Toggle initialized');
        },

        bindEvents: function () {
            // Bind to existing theme buttons in header
            const themeButtons = document.querySelectorAll('[onclick*="toggleTheme"]');
            themeButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleTheme();
                });
            });
        },

        toggleTheme: function () {
            const html = document.documentElement;
            const currentScheme = html.getAttribute('color-scheme') || 'light';
            const newScheme = currentScheme === 'light' ? 'dark' : 'light';

            html.setAttribute('color-scheme', newScheme);

            // Update all theme button icons
            const themeButtons = document.querySelectorAll('[onclick*="toggleTheme"] i');
            themeButtons.forEach(icon => {
                icon.className = newScheme === 'light' ?
                    'ph-bold ph-moon-stars text-lg' :
                    'ph-bold ph-sun text-lg';
            });

            // Save preference
            localStorage.setItem('color-scheme', newScheme);

            Utils.debug('Theme changed to:', newScheme);
        }
    };

    // Search Modal Module
    const SearchModal = {
        // State management
        searchState: 'idle',
        currentQuery: '',
        currentFilters: {
            section: 'all',
            tags: [],
            sort: 'relevance'
        },

        init: function () {
            this.bindEvents();
            // Load tags immediately on initialization
            this.loadTags();
            Utils.debug('Search Modal initialized');
        },

        bindEvents: function () {
            // Bind to existing search buttons in header
            const searchButtons = document.querySelectorAll('[onclick*="openSearchModal"]');
            searchButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.openModal();
                });
            });

            // Close modal when clicking outside or on close button
            document.addEventListener('click', (e) => {
                const modal = document.getElementById('searchOverlay') || document.getElementById('search-modal');
                const closeBtn = e.target.closest('.search-close') || e.target.closest('.search-modal-close');
                if (modal && (e.target === modal || closeBtn)) {
                    this.closeModal();
                }
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeModal();
                }
            });
        },

        openModal: function () {
            const modal = document.getElementById('searchOverlay') || document.getElementById('search-modal');
            if (modal) {
                modal.classList.add('active');
                const input = modal.querySelector('.search-input') || modal.querySelector('.search-modal-input');
                if (input) {
                    setTimeout(() => input.focus(), 100);
                }
            }
        },

        closeModal: function () {
            const modal = document.getElementById('searchOverlay') || document.getElementById('search-modal');
            if (modal) {
                modal.classList.remove('active');
            }
        },

        setState(newState) {
            if (this.searchState === newState) return; // No change needed
            this.searchState = newState;

            const modal = document.getElementById('searchOverlay') || document.getElementById('search-modal');
            if (!modal) return;

            const searchResultsSection = modal.querySelector('.search-results-section');
            const searchSuggestions = modal.querySelector('.search-suggestions');
            const typingState = modal.querySelector('.search-typing-state');
            const initialFilters = modal.querySelector('.search-filters');

            if (newState === 'idle') {
                // Fade out active state components
                if (searchResultsSection) {
                    searchResultsSection.classList.remove('visible');
                    setTimeout(() => {
                        if (searchResultsSection) searchResultsSection.style.display = 'none';
                    }, 300);
                }

                // Wait for fade out animation, then show idle state
                setTimeout(() => {
                    if (searchSuggestions) {
                        searchSuggestions.style.display = 'flex';
                        searchSuggestions.classList.remove('hidden');
                    }
                    if (typingState) {
                        typingState.style.display = 'block';
                        typingState.classList.remove('hidden');
                    }
                    if (initialFilters) {
                        initialFilters.style.display = 'block';
                        initialFilters.classList.remove('hidden');
                    }
                }, 350);
            } else if (newState === 'active') {
                // Fade out idle state components
                if (searchSuggestions) {
                    searchSuggestions.classList.add('hidden');
                    setTimeout(() => {
                        if (searchSuggestions) searchSuggestions.style.display = 'none';
                    }, 300);
                }
                if (typingState) {
                    typingState.classList.add('hidden');
                    setTimeout(() => {
                        if (typingState) typingState.style.display = 'none';
                    }, 300);
                }
                if (initialFilters) {
                    initialFilters.classList.add('hidden');
                    setTimeout(() => {
                        if (initialFilters) initialFilters.style.display = 'none';
                    }, 300);
                }

                // Wait for fade out animation, then show active state
                setTimeout(() => {
                    if (searchResultsSection) {
                        searchResultsSection.style.display = 'flex';
                        searchResultsSection.classList.add('visible');
                    }
                }, 350);
            }
        },

        async loadTags() {
            try {
                const response = await fetch('/api/search/filters');
                if (!response.ok) throw new Error('Failed to load filters');

                const filters = await response.json();
                this.updateTags(filters);
            } catch (error) {
                Utils.debug('Error loading tags:', error);
                this.showTagsError();
            }
        },

        showTagsError() {
            const modal = document.getElementById('searchOverlay') || document.getElementById('search-modal');
            if (!modal) return;

            const tagContainer = modal.querySelector('#tagFilters') || modal.querySelector('.tag-filters');
            if (tagContainer) {
                tagContainer.innerHTML = `
                    <div class="tag-error">
                        <span>An error occurred, can't load tags filter</span>
                    </div>
                `;
            }
        },

        updateTags(filters) {
            const modal = document.getElementById('searchOverlay') || document.getElementById('search-modal');
            if (!modal) return;

            const tagContainer = modal.querySelector('#tagFilters') || modal.querySelector('.tag-filters');
            if (tagContainer && filters.tags) {
                tagContainer.innerHTML = '';

                // Sort tags by post count (descending) and take top 8
                const sortedTags = Object.entries(filters.counts?.tags || {})
                    .sort(([,a], [,b]) => b - a)
                    .slice(0, 8);

                sortedTags.forEach(([tag, count]) => {
                    const tagChip = document.createElement('span');
                    tagChip.className = 'tag-chip';
                    tagChip.setAttribute('data-tag', tag);
                    tagChip.innerHTML = `
                        <span>${tag}</span>
                        <span class="tag-count">${count}</span>
                    `;
                    
                    // Add click handler for tag filtering (just like in topics page)
                    tagChip.addEventListener('click', () => {
                        this.handleTagClick(tag);
                    });
                    
                    tagContainer.appendChild(tagChip);
                });

                Utils.debug('Updated tags with real data:', sortedTags.length, 'tags');
            }
        },

        handleTagClick(tag) {
            const modal = document.getElementById('searchOverlay') || document.getElementById('search-modal');
            if (!modal) return;

            // Update tag chip active states
            const tagChips = modal.querySelectorAll('.tag-chip');
            tagChips.forEach(chip => {
                chip.classList.toggle('active', chip.dataset.tag === tag);
            });

            // Set the search input to the tag name and trigger search
            const searchInput = modal.querySelector('.search-input') || modal.querySelector('.search-modal-input');
            if (searchInput) {
                searchInput.value = tag;
                this.searchByTag(tag);
            }
        },

        async searchByTag(tag) {
            const modal = document.getElementById('searchOverlay') || document.getElementById('search-modal');
            if (!modal) return;

            // Show active state if not already active
            if (this.searchState !== 'active') {
                this.setState('active');
            }

            // Update current query and filters
            this.currentQuery = tag;
            this.currentFilters = {
                ...this.currentFilters,
                tags: [tag]
            };

            // Show loading state
            const resultsCount = modal.querySelector('#resultsCount');
            const searchResults = modal.querySelector('#searchResults');
            
            if (resultsCount) {
                resultsCount.textContent = `Searching #${tag} posts...`;
            }
            
            if (searchResults) {
                searchResults.innerHTML = `
                    <div class="loading">
                        <div class="loading-spinner"></div>
                        <p>Finding #${tag} posts...</p>
                    </div>
                `;
            }

            try {
                // Make API call to search posts by tag
                const response = await fetch('/api/search/posts', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        query: '', // Empty query for tag-only search
                        tags: [tag],
                        section: 'all',
                        sort: 'recent',
                        limit: 20,
                        offset: 0
                    })
                });

                if (!response.ok) {
                    throw new Error(`Search failed: ${response.status}`);
                }

                const searchData = await response.json();
                this.renderTagResults(searchData.results, tag);

            } catch (error) {
                console.error('Tag search error:', error);
                
                if (searchResults) {
                    searchResults.innerHTML = `
                        <div class="no-results">
                            <div class="no-results-icon">
                                <i class="ph-bold ph-warning-circle"></i>
                            </div>
                            <h3>Search Error</h3>
                            <p>Unable to load posts for #${tag}. Please try again.</p>
                        </div>
                    `;
                }
                
                if (resultsCount) {
                    resultsCount.textContent = 'Search failed';
                }
            }
        },

        renderTagResults(results, tag) {
            const modal = document.getElementById('searchOverlay') || document.getElementById('search-modal');
            if (!modal) return;

            const resultsCount = modal.querySelector('#resultsCount');
            const searchResults = modal.querySelector('#searchResults');
            const searchStats = modal.querySelector('#searchStats');
            const loadMoreContainer = modal.querySelector('#loadMoreContainer');

            // Update results count
            if (resultsCount) {
                const count = results.length;
                resultsCount.textContent = count === 1 
                    ? `1 post found for #${tag}` 
                    : `${count} posts found for #${tag}`;
            }

            // Update search stats
            if (searchStats) {
                searchStats.innerHTML = `<i class="ph-bold ph-hash"></i> Tag: #${tag}`;
            }

            // Show/hide load more button
            if (loadMoreContainer) {
                loadMoreContainer.style.display = results.length >= 20 ? 'block' : 'none';
            }

            // Render results
            if (searchResults) {
                if (results.length === 0) {
                    searchResults.innerHTML = `
                        <div class="no-results">
                            <div class="no-results-icon">
                                <i class="ph-bold ph-hash"></i>
                            </div>
                            <h3>No posts found</h3>
                            <p>No posts found with the #${tag} tag. Try exploring other topics.</p>
                        </div>
                    `;
                    return;
                }

                const resultsHTML = results.map(result => this.createResultCard(result, tag)).join('');
                searchResults.innerHTML = resultsHTML;
            }
        },

        createResultCard(result, tag) {
            return `
                <div class="result-card">
                    <div class="result-media">
                        ${result.featured_image ? 
                            `<img src="${result.featured_image}" alt="${result.title}" class="result-image">` :
                            `<div class="result-icon"><i class="ph-bold ph-article"></i></div>`
                        }
                    </div>
                    <div class="result-content">
                        <div class="result-category">${result.section || 'Article'}</div>
                        <h3 class="result-title">${this.highlightText(result.title, tag)}</h3>
                        <p class="result-excerpt">${this.highlightText(result.excerpt || 'No excerpt available', tag)}</p>
                        <div class="result-meta">
                            <span class="result-author">${result.author || 'NekwasaR'}</span>
                            <span class="result-date">${result.published_at ? new Date(result.published_at).toLocaleDateString() : 'Recent'}</span>
                            <span class="result-stats">
                                <i class="ph-bold ph-eye"></i> ${result.view_count || 0}
                            </span>
                            ${result.tags ? `<div class="result-tags">${result.tags.slice(0, 3).map(t => `<span class="result-tag">#${t}</span>`).join('')}</div>` : ''}
                        </div>
                    </div>
                </div>
            `;
        },

        highlightText(text, query) {
            if (!query) return text;
            const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
            return text.replace(regex, '<span class="highlight">$1</span>');
        }
    };

    // Video Controls Module
    const VideoControls = {
        init: function () {
            this.bindEvents();
            Utils.debug('Video Controls initialized');
        },

        bindEvents: function () {
            document.addEventListener('click', (e) => {
                const playPauseBtn = e.target.closest('#playPauseBtn');
                const muteBtn = e.target.closest('#muteBtn');
                const fullscreenBtn = e.target.closest('#fullscreenBtn');

                const video = document.getElementById('heroVideo');
                if (!video) return;

                if (playPauseBtn) {
                    this.togglePlayPause(video, playPauseBtn);
                } else if (muteBtn) {
                    this.toggleMute(video, muteBtn);
                } else if (fullscreenBtn) {
                    this.toggleFullscreen(video, fullscreenBtn);
                }
            });
        },

        togglePlayPause: function (video, button) {
            if (video.paused) {
                video.play();
                button.innerHTML = '<i class="ph-bold ph-pause"></i>';
            } else {
                video.pause();
                button.innerHTML = '<i class="ph-bold ph-play"></i>';
            }
        },

        toggleMute: function (video, button) {
            if (video.muted) {
                video.muted = false;
                button.innerHTML = '<i class="ph-bold ph-speaker-simple-high"></i>';
            } else {
                video.muted = true;
                button.innerHTML = '<i class="ph-bold ph-speaker-simple-x"></i>';
            }
        },

        toggleFullscreen: function (video, button) {
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                video.requestFullscreen().catch(err => {
                    Utils.debug('Fullscreen failed:', err);
                });
            }
        }
    };

    // Print Module
    const Print = {
        init: function () {
            this.bindEvents();
            Utils.debug('Print functionality initialized');
        },

        bindEvents: function () {
            document.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
                    this.prepareForPrint();
                }
            });
        },

        prepareForPrint: function () {
            // Add print-specific styles
            const printStyles = document.createElement('style');
            printStyles.id = 'print-styles';
            printStyles.textContent = `
                @media print {
                    .social-share,
                    .video-controls,
                    .banner-cta,
                    #theme-toggle,
                    #reading-progress {
                        display: none !important;
                    }
                    
                    .blog-post {
                        background: white !important;
                        color: black !important;
                    }
                    
                    .blog-post h1,
                    .blog-post h2,
                    .blog-post h3,
                    .blog-post h4 {
                        color: black !important;
                        -webkit-text-fill-color: black !important;
                    }
                    
                    a {
                        color: black !important;
                        text-decoration: underline !important;
                    }
                    
                    .banner-image-overlay,
                    .banner-video-overlay {
                        display: none !important;
                    }
                    
                    .banner-content {
                        color: black !important;
                    }
                    
                    blockquote {
                        background: #f5f5f5 !important;
                        border-left: 4px solid #000 !important;
                        color: #000 !important;
                    }
                }
            `;

            document.head.appendChild(printStyles);

            // Remove after print
            setTimeout(() => {
                const styles = document.getElementById('print-styles');
                if (styles) {
                    styles.remove();
                }
            }, 1000);
        }
    };

    // Main initialization
    const BlogTemplates = {
        init: function () {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeModules());
            } else {
                this.initializeModules();
            }
        },

        initializeModules: function () {
            // Load saved theme preference (unified with blog.js + early bootstrap in base)
            const savedBlogTheme = localStorage.getItem('blog.theme');
            const savedTheme = savedBlogTheme || localStorage.getItem('color-scheme');
            if (savedTheme) {
                const root = document.documentElement;
                const isLight = savedTheme === 'light';
                // Apply attribute + Tailwind class + color-scheme for native controls
                root.setAttribute('color-scheme', savedTheme);
                root.setAttribute('data-theme', savedTheme);
                root.classList.toggle('dark', !isLight);
                try { root.style.colorScheme = isLight ? 'light' : 'dark'; } catch (e) { }
                // If early bootstrap API is present, normalize through it
                try {
                    if (typeof window.__applyTheme === 'function') {
                        window.__applyTheme(savedTheme);
                    }
                } catch (e) { }
            }

            // Keep theme fully in sync if other contexts update it
            window.addEventListener('storage', (e) => {
                if (e.key === 'blog.theme' || e.key === 'color-scheme') {
                    const t = localStorage.getItem('blog.theme') || localStorage.getItem('color-scheme');
                    if (!t) return;
                    try {
                        if (typeof window.__applyTheme === 'function') {
                            window.__applyTheme(t);
                        } else {
                            const root = document.documentElement;
                            const isLight = t === 'light';
                            root.setAttribute('color-scheme', t);
                            root.setAttribute('data-theme', t);
                            root.classList.toggle('dark', !isLight);
                            try { root.style.colorScheme = isLight ? 'light' : 'dark'; } catch (err) { }
                        }
                    } catch (err) {
                        // no-op
                    }
                }
            });

            // Initialize all modules
            try {
                SmoothScroll.init();
                SocialShare.init();
                ReadingProgress.init();

                // Only initialize if elements exist
                if (document.querySelector('.toc')) {
                    TableOfContents.init();
                }

                if (document.querySelector('.blog-card, .listing-item, blockquote')) {
                    Animations.init();
                }

                // if (document.getElementById('newsletterForm')) {
                //     Newsletter.init();
                // }

                if (document.getElementById('heroVideo')) {
                    VideoControls.init();
                }

                ThemeToggle.init();
                SearchModal.init();
                Print.init();

                Utils.debug('All modules initialized successfully');
            } catch (error) {
                console.error('Error initializing modules:', error);
            }
        }
    };

    const RouteManager = {
        routes: ['home', 'latest', 'popular', 'others', 'featured', 'topics'],
        fallback: 'home',
        init: function () {
            this.container = document.getElementById('route-container');
            this.bindNavLinks();
            window.addEventListener('popstate', () => {
                this.renderRoute(this.getCurrentRoute(), false);
            });
            // If we land on '/', do not force-load another route; content is already server-rendered
            const current = this.getCurrentRoute();
            if (current !== 'home') {
                this.renderRoute(current, false);
            }
        },
        bindNavLinks() {
            document.querySelectorAll('a[data-route]').forEach(link => {
                link.addEventListener('click', (event) => {
                    event.preventDefault();
                    const route = link.dataset.route;
                    this.navigate(route);
                });
            });
        },
        routeToPath(route) {
            return route === 'home' ? '/' : `/${route}`;
        },
        getCurrentRoute() {
            const path = window.location.pathname.replace(/^\/+|\/+$/g, '').toLowerCase();
            if (!path) return 'home';
            return this.routes.includes(path) ? path : this.fallback;
        },
        navigate(route, query = '') {
            if (!this.routes.includes(route)) {
                route = this.fallback;
            }
            const path = this.routeToPath(route);
            const url = query ? `${path}${query}` : path;
            history.pushState({}, '', url);
            this.renderRoute(route, true);
        },
        async renderRoute(route, smoothScroll = true) {
            if (!this.container) return;
            try {
                const url = this.routeToPath(route);
                const res = await fetch(url, {
                    headers: { 'X-Requested-With': 'fetch' }
                });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const html = await res.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newContainer = doc.querySelector('#route-container');
                if (!newContainer) throw new Error('Missing #route-container in response');

                // Swap main content
                this.container.innerHTML = newContainer.innerHTML;

                // Ensure theme state/icons are synced after swap
                if (window.ApplyThemeFromStorage && typeof window.ApplyThemeFromStorage === 'function') {
                    try { window.ApplyThemeFromStorage(); } catch (e) { console.error('ApplyThemeFromStorage failed:', e); }
                }

                // Re-initialize page-level JS for newly injected content
                if (window.BlogPageInit && typeof window.BlogPageInit === 'function') {
                    try { window.BlogPageInit(); } catch (e) { console.error('BlogPageInit failed:', e); }
                }

                // Call page-specific initialization (e.g., initHome, initLatest)
                const pageInitFunction = `init${route.charAt(0).toUpperCase() + route.slice(1)}`;
                if (typeof window[pageInitFunction] === 'function') {
                    try { window[pageInitFunction](); } catch (e) { console.error(`${pageInitFunction} failed:`, e); }
                }

                // Update title and meta description
                const newTitle = doc.querySelector('title')?.textContent?.trim();
                if (newTitle) document.title = newTitle;
                const newMetaDescription = doc.querySelector('meta[name="description"]')?.getAttribute('content') || '';
                const meta = document.querySelector('meta[name="description"]');
                if (meta && newMetaDescription) meta.setAttribute('content', newMetaDescription);

                // Highlight active nav link
                document.querySelectorAll('a[data-route]').forEach(a => {
                    a.classList.toggle('active', a.dataset.route === route);
                });

                if (smoothScroll) this.scrollToTop();
            } catch (err) {
                console.warn('SPA fetch failed, falling back to full navigation:', err);
                window.location.href = this.routeToPath(route);
            }
        },
        scrollToTop() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    // Start the application
    BlogTemplates.init();

    // Initialize SPA router if enabled via body[data-use-routing="true"]
    try {
        const body = document.body;
        const useRouting = body && (body.dataset.useRouting === 'true' || body.getAttribute('data-use-routing') === 'true');
        if (useRouting && typeof RouteManager !== 'undefined' && RouteManager.init) {
            RouteManager.init();
        }
    } catch (e) {
        console.error('RouteManager init error:', e);
    }

    // Export for global access if needed
    window.BlogTemplates = BlogTemplates;
    window.BlogTemplatesUtils = Utils;

})();