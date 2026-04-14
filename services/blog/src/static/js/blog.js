// Blog JavaScript - Modern, Interactive, and Feature-Rich

(function () {
  "use strict";

  // Robust bootstrap: run once regardless of readyState timing
  (function bootstrap() {
    function start() {
      if (window.__blogInited) return;
      window.__blogInited = true;
      initBlog();
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', start, { once: true });
    } else {
      start();
    }
  })();

  function initBlog() {
    // Initialize all blog features (resilient to isolated failures)
    const safe = (fn, name) => {
      try { fn(); } catch (e) { console.error('Blog init error in', name || fn?.name, e); }
    };

    safe(initParticleSystem, 'initParticleSystem');
    safe(initThemeToggle, 'initThemeToggle');
    safe(initBannerSlider, 'initBannerSlider');
    safe(initTrendingSlider, 'initTrendingSlider');
    safe(initArticlesSlider, 'initArticlesSlider');
    safe(initSearchModal, 'initSearchModal');
    safe(initMenuModal, 'initMenuModal');
    safe(initScrollToTop, 'initScrollToTop');
    safe(initNewsletterForm, 'initNewsletterForm');
    safe(initSmoothScrolling, 'initSmoothScrolling');
    safe(initAnimations, 'initAnimations');
    safe(initCardLinks, 'initCardLinks');
    safe(initPostModal, 'initPostModal');
    safe(forceTextWrapping, 'forceTextWrapping');
  }

  // Force text wrapping for slide titles on mobile
  function forceTextWrapping() {
    const slideTitles = document.querySelectorAll('.slide-title-text');

    slideTitles.forEach(title => {
      // Force line breaks for long titles
      const text = title.textContent;
      if (text.length > 30) {
        // Insert line breaks at word boundaries
        const words = text.split(' ');
        let currentLine = '';
        let newText = '';

        words.forEach(word => {
          if ((currentLine + ' ' + word).length > 15) {
            newText += currentLine + '\n';
            currentLine = word;
          } else {
            currentLine += (currentLine ? ' ' : '') + word;
          }
        });
        newText += currentLine;

        title.innerHTML = newText.replace(/\n/g, '<br>');
      }
    });
  }

  // Particle System for Hero Section
  function initParticleSystem() {
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;

    function resizeCanvas() {
      const rect = canvas.parentElement.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
    }

    function createParticle(x, y) {
      return {
        x: x || Math.random() * canvas.width,
        y: y || Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 4 + 2,
        life: Math.random() * 100 + 50,
        maxLife: Math.random() * 100 + 50,
        color: getCurrentThemeColor()
      };
    }

    function getCurrentThemeColor() {
      const isDark = document.documentElement.getAttribute('color-scheme') === 'dark';
      const colors = isDark ?
        ['rgba(206, 196, 239, 0.6)', 'rgba(228, 184, 191, 0.6)', 'rgba(104, 103, 105, 0.4)'] :
        ['rgba(13, 37, 85, 0.6)', 'rgba(228, 184, 191, 0.6)', 'rgba(7, 0, 17, 0.4)'];
      return colors[Math.floor(Math.random() * colors.length)];
    }

    function initParticles() {
      particles = [];
      const particleCount = Math.min(120, Math.floor((canvas.width * canvas.height) / 8000));

      for (let i = 0; i < particleCount; i++) {
        particles.push(createParticle());
      }
    }

    function updateParticles() {
      particles.forEach((particle, index) => {
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.life--;

        // Wrap around edges
        if (particle.x < 0) particle.x = canvas.width;
        if (particle.x > canvas.width) particle.x = 0;
        if (particle.y < 0) particle.y = canvas.height;
        if (particle.y > canvas.height) particle.y = 0;

        // Mouse interaction - stronger attraction
        const mouseX = window.mouseX || canvas.width / 2;
        const mouseY = window.mouseY || canvas.height / 2;
        const dx = mouseX - particle.x;
        const dy = mouseY - particle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 150) {
          const force = (150 - distance) / 150;
          particle.vx += (dx / distance) * force * 0.02;
          particle.vy += (dy / distance) * force * 0.02;
        }

        // Add some organic movement
        particle.vx += (Math.random() - 0.5) * 0.01;
        particle.vy += (Math.random() - 0.5) * 0.01;

        // Limit velocity
        const maxSpeed = 1;
        const speed = Math.sqrt(particle.vx * particle.vx + particle.vy * particle.vy);
        if (speed > maxSpeed) {
          particle.vx = (particle.vx / speed) * maxSpeed;
          particle.vy = (particle.vy / speed) * maxSpeed;
        }

        // Respawn dead particles
        if (particle.life <= 0) {
          particles[index] = createParticle();
        }
      });
    }

    function drawParticles() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach(particle => {
        const alpha = particle.life / particle.maxLife;
        ctx.globalAlpha = alpha;

        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = particle.color;
        ctx.fill();

        // Draw connections between nearby particles
        particles.forEach(otherParticle => {
          if (particle !== otherParticle) {
            const dx = particle.x - otherParticle.x;
            const dy = particle.y - otherParticle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 120) {
              ctx.globalAlpha = (120 - distance) / 120 * alpha * 0.5;
              ctx.beginPath();
              ctx.moveTo(particle.x, particle.y);
              ctx.lineTo(otherParticle.x, otherParticle.y);
              ctx.strokeStyle = particle.color;
              ctx.lineWidth = 1;
              ctx.stroke();
            }
          }
        });
      });

      ctx.globalAlpha = 1;
    }

    function animate() {
      updateParticles();
      drawParticles();
      animationId = requestAnimationFrame(animate);
    }

    // Track mouse position
    document.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      window.mouseX = e.clientX - rect.left;
      window.mouseY = e.clientY - rect.top;
    });

    // Initialize
    resizeCanvas();
    initParticles();
    animate();

    // Handle resize
    window.addEventListener('resize', () => {
      resizeCanvas();
      initParticles();
    });

    // Update colors when theme changes
    const observer = new MutationObserver(() => {
      particles.forEach(particle => {
        particle.color = getCurrentThemeColor();
      });
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['color-scheme']
    });
  }

  // Theme Toggle Functionality
  function initThemeToggle() {
    const themeBtn = document.getElementById('themeToggle') || document.getElementById('theme-toggle');
    const menuThemeBtn = document.getElementById('menuThemeToggle') || document.getElementById('menu-theme-toggle');

    // If neither exists, nothing to bind
    if (!themeBtn && !menuThemeBtn) return;

    function getCurrentTheme() {
      let theme =
        document.documentElement.getAttribute('color-scheme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      const saved = localStorage.getItem('blog.theme') || localStorage.getItem('color-scheme');
      if (saved) theme = saved;
      return theme;
    }

    function setIcons(theme) {
      const desired = theme === 'light' ? 'ph ph-sun' : 'ph ph-moon-stars';
      [themeBtn, menuThemeBtn].forEach(btn => {
        if (!btn) return;
        let iconEl = btn.querySelector('i');
        if (!iconEl) {
          iconEl = document.createElement('i');
          btn.innerHTML = '';
          btn.appendChild(iconEl);
        }
        iconEl.className = desired;
      });
      if (themeBtn) {
        themeBtn.setAttribute('aria-label', theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode');
      }
    }

    function loadTheme(theme) {
      const root = document.documentElement;
      // Persist to both keys for cross-script compatibility
      localStorage.setItem('blog.theme', theme);
      localStorage.setItem('color-scheme', theme);

      // Apply attribute + Tailwind dark class (some route pages rely on dark: variants)
      const isLight = theme === 'light';
      root.setAttribute('color-scheme', isLight ? 'light' : 'dark');
      root.setAttribute('data-theme', theme);
      if (isLight) {
        root.classList.remove('dark');
      } else {
        root.classList.add('dark');
      }
      // Inform the UA for form controls, etc.
      try { root.style.colorScheme = isLight ? 'light' : 'dark'; } catch (e) { /* no-op */ }

      setIcons(theme);
    }

    // Bind click handlers once per element (avoid duplicate bindings on SPA swaps)
    [themeBtn, menuThemeBtn].forEach(btn => {
      if (btn && !btn.dataset.bound) {
        btn.addEventListener('click', () => {
          if (typeof window.__toggleTheme === 'function') {
            window.__toggleTheme();
          } else {
            let theme = getCurrentTheme();
            theme = theme === 'dark' ? 'light' : 'dark';
            loadTheme(theme);
          }
        });
        btn.dataset.bound = 'true';
      }
    });

    // Additionally, delegate click so the toggle always works even if bindings are lost on SPA swaps
    // Avoid double-toggle if early bootstrap already installed a global handler
    if (!window.__themeBootstrap && !window.__themeDelegated) {
      document.addEventListener('click', (e) => {
        const tbtn = e.target.closest('#themeToggle, #theme-toggle, #menuThemeToggle, #menu-theme-toggle');
        if (tbtn) {
          if (typeof window.__toggleTheme === 'function') {
            window.__toggleTheme();
          } else {
            let theme = getCurrentTheme();
            theme = theme === 'dark' ? 'light' : 'dark';
            loadTheme(theme);
          }
        }
      }, true);
      window.__themeDelegated = true;
    }

    // Observe attribute changes (if any other script flips theme, keep icons in sync)
    const mo = new MutationObserver(() => setIcons(getCurrentTheme()));
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['color-scheme', 'class', 'data-theme'] });

    // Load initial theme
    loadTheme(getCurrentTheme());

    // Expose sync helper for SPA route swaps
    if (!window.ApplyThemeFromStorage) {
      window.ApplyThemeFromStorage = () => {
        try {
          const t = getCurrentTheme();
          if (typeof window.__applyTheme === 'function') {
            window.__applyTheme(t);
          } else {
            loadTheme(t);
          }
        } catch (e) { /* no-op */ }
      };
    }
  }

  // Banner Slider Functionality
  function initBannerSlider() {
    const slider = document.getElementById('bannerSlider');
    const prevBtn = document.getElementById('bannerPrev');
    const nextBtn = document.getElementById('bannerNext');
    const dotsContainer = document.getElementById('bannerDots');

    if (!slider || !prevBtn || !nextBtn) return;

    // Clean up existing state if re-initializing
    if (slider.autoSlideInterval) clearInterval(slider.autoSlideInterval);
    if (dotsContainer) dotsContainer.innerHTML = '';

    const slides = slider.querySelectorAll('.banner-slide');
    if (slides.length === 0) return;

    let currentSlide = 0;

    // Create dots
    for (let i = 0; i < slides.length; i++) {
      const dot = document.createElement('div');
      dot.className = 'slider-dot';
      if (i === 0) dot.classList.add('active');
      dot.addEventListener('click', () => goToSlide(i));
      dotsContainer.appendChild(dot);
    }

    const dots = dotsContainer.querySelectorAll('.slider-dot');

    function updateDots() {
      dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === currentSlide);
      });
    }

    function updateSlides() {
      slides.forEach((slide, index) => {
        slide.classList.toggle('active', index === currentSlide);
      });
    }

    function goToSlide(index) {
      currentSlide = index;
      slider.style.transform = `translateX(-${currentSlide * 33.333}%)`;
      updateDots();
      updateSlides();
    }

    function nextSlide() {
      currentSlide = (currentSlide + 1) % slides.length;
      goToSlide(currentSlide);
    }

    function prevSlide() {
      currentSlide = (currentSlide - 1 + slides.length) % slides.length;
      goToSlide(currentSlide);
    }

    // Event listeners - use onclick to prevent duplicates on re-init
    nextBtn.onclick = nextSlide;
    prevBtn.onclick = prevSlide;

    // Auto slide every 4 seconds
    function startAutoSlide() {
      stopAutoSlide(); // Ensure we don't have multiple
      slider.autoSlideInterval = setInterval(nextSlide, 4000);
    }

    function stopAutoSlide() {
      if (slider.autoSlideInterval) {
        clearInterval(slider.autoSlideInterval);
        slider.autoSlideInterval = null;
      }
    }

    // Pause on hover
    slider.parentElement.onmouseenter = stopAutoSlide;
    slider.parentElement.onmouseleave = startAutoSlide;

    // Initialize first slide
    updateSlides();

    // Start auto slide
    startAutoSlide();
  }
  window.initBannerSlider = initBannerSlider;

  // Trending Slider Functionality
  function initTrendingSlider() {
    const slider = document.getElementById('trendingSlider');
    const prevBtn = document.getElementById('trendingPrev');
    const nextBtn = document.getElementById('trendingNext');
    const dotsContainer = document.getElementById('trendingDots');

    if (!slider || !prevBtn || !nextBtn) return;

    // Clean up
    if (slider.autoSlideInterval) clearInterval(slider.autoSlideInterval);
    if (dotsContainer) dotsContainer.innerHTML = '';

    const slides = slider.querySelectorAll('.slide');
    if (slides.length === 0) return;

    let currentSlide = 0;

    // Create dots
    for (let i = 0; i < slides.length; i++) {
      const dot = document.createElement('div');
      dot.className = 'slider-dot';
      if (i === 0) dot.classList.add('active');
      dot.addEventListener('click', () => goToSlide(i));
      dotsContainer.appendChild(dot);
    }

    const dots = dotsContainer.querySelectorAll('.slider-dot');

    function updateDots() {
      dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === currentSlide);
      });
    }

    function updateSlides() {
      slides.forEach((slide, index) => {
        slide.classList.remove('active');
        if (index === currentSlide) {
          slide.classList.add('active');
        }
      });
    }

    function goToSlide(index) {
      currentSlide = index;
      slider.style.transform = `translateX(-${currentSlide * 33.333}%)`;
      updateDots();
      updateSlides();
    }

    function nextSlide() {
      currentSlide = (currentSlide + 1) % slides.length;
      goToSlide(currentSlide);
    }

    function prevSlide() {
      currentSlide = (currentSlide - 1 + slides.length) % slides.length;
      goToSlide(currentSlide);
    }

    // Make slides clickable
    slides.forEach((slide, index) => {
      slide.onclick = () => {
        const href = slide.getAttribute('data-href');
        if (href) {
          if (window.RouteManager && typeof window.RouteManager.navigate === 'function') {
            window.RouteManager.navigate(href.replace('/blog/', ''));
          } else {
            window.location.href = href;
          }
        }
      };
      slide.style.cursor = 'pointer';
    });

    // Event listeners
    nextBtn.onclick = nextSlide;
    prevBtn.onclick = prevSlide;

    // Auto slide
    function startAutoSlide() {
      stopAutoSlide();
      slider.autoSlideInterval = setInterval(nextSlide, 4000);
    }

    function stopAutoSlide() {
      if (slider.autoSlideInterval) {
        clearInterval(slider.autoSlideInterval);
        slider.autoSlideInterval = null;
      }
    }

    // Pause on hover
    slider.parentElement.onmouseenter = stopAutoSlide;
    slider.parentElement.onmouseleave = startAutoSlide;

    // Initialize first slide
    updateSlides();

    // Start auto slide
    startAutoSlide();
  }
  window.initTrendingSlider = initTrendingSlider;

  // Articles Slider Functionality
  function initArticlesSlider() {
    const track = document.getElementById('articlesTrack');
    const prevBtn = document.getElementById('articlesPrev');
    const nextBtn = document.getElementById('articlesNext');

    if (!track || !prevBtn || !nextBtn) return;

    // Clean up
    if (track.autoSlideInterval) clearInterval(track.autoSlideInterval);

    const cards = Array.from(track.children);
    if (cards.length === 0) return;

    let currentIndex = 0;
    const cardWidth = 340; // 320px card + 20px gap
    const visibleCards = 3;
    const totalCards = 6; // Fixed as requested

    // Ensure we have exactly 6 cards
    while (cards.length < totalCards) {
      const clone = cards[0].cloneNode(true);
      cards.push(clone);
      track.appendChild(clone);
    }

    // Clone first 3 cards for seamless infinite scroll
    for (let i = 0; i < visibleCards; i++) {
      const clone = cards[i].cloneNode(true);
      track.appendChild(clone);
    }

    function updateSlider() {
      const translateX = -currentIndex * cardWidth;
      track.style.transform = `translateX(${translateX}px)`;
    }

    function nextSlide() {
      if (currentIndex >= totalCards - visibleCards) {
        track.style.transition = 'none';
        currentIndex = 0;
        updateSlider();
        setTimeout(() => {
          track.style.transition = 'transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
          currentIndex = 1;
          updateSlider();
        }, 50);
      } else {
        currentIndex++;
        updateSlider();
      }
    }

    function prevSlide() {
      if (currentIndex <= 0) {
        track.style.transition = 'none';
        currentIndex = totalCards - visibleCards;
        updateSlider();
        setTimeout(() => {
          track.style.transition = 'transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
          currentIndex = totalCards - visibleCards - 1;
          updateSlider();
        }, 50);
      } else {
        currentIndex--;
        updateSlider();
      }
    }

    nextBtn.onclick = nextSlide;
    prevBtn.onclick = prevSlide;

    // Auto slide every 4 seconds
    track.autoSlideInterval = setInterval(nextSlide, 4000);
  }
  window.initArticlesSlider = initArticlesSlider;

  // Advanced Search Modal Functionality
  function initSearchModal() {
    const searchBtn = document.getElementById('searchToggle') || document.getElementById('search-toggle');
    const searchOverlay = document.getElementById('searchOverlay');
    const searchClose = document.getElementById('searchClose');
    const searchInput = document.getElementById('searchInput');
    const searchSubmit = document.getElementById('searchBtn');

    // State management elements
    const searchSuggestions = document.getElementById('searchSuggestions');
    const typingState = document.getElementById('typingState');
    const initialFilters = document.querySelector('.search-filters');
    const searchResultsSection = document.querySelector('.search-results-section');
    const resultsCount = document.getElementById('resultsCount');
    const searchStats = document.getElementById('searchStats');
    const resultFilters = document.getElementById('resultsSort');
    const searchResults = document.getElementById('searchResults');
    const loadMoreContainer = document.getElementById('loadMoreContainer');
    const loadMoreBtn = document.getElementById('loadMoreBtn');

    if (!searchBtn || !searchOverlay) return;

    // Search state
    let searchState = 'idle'; // 'idle' or 'active'
    let currentQuery = '';
    let currentFilters = {
      section: 'all',
      tags: [],
      sort: 'relevance'
    };
    let currentResults = [];
    let resultsOffset = 0;
    const resultsPerPage = 10;

    function openSearch() {
      searchOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
      if (searchInput) {
        searchInput.focus();
        setState('idle'); // Set to idle state when opening
      }
    }

    function closeSearch() {
      searchOverlay.classList.remove('active');
      document.body.style.overflow = '';
      resetSearchState();
    }

    function setState(newState) {
      const currentState = searchState;
      if (currentState === newState) return; // No change needed

      searchState = newState;

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
    }

    function resetSearchState() {
      currentQuery = '';
      currentFilters = { section: 'all', tags: [], sort: 'relevance' };
      currentResults = [];
      resultsOffset = 0;
      searchState = 'idle';

      if (searchInput) searchInput.value = '';

      // Reset UI to idle state
      setState('idle');
      updateUI();
      showInitialState();
    }

    function showInitialState() {
      resultsCount.textContent = 'Start typing to search...';
      searchStats.innerHTML = '';
      loadMoreContainer.style.display = 'none';

      if (searchResults) {
        searchResults.innerHTML = `
          <div class="no-results">
            <div class="no-results-icon">
              <i class="ph-bold ph-magnifying-glass"></i>
            </div>
            <h3>Discover Amazing Content</h3>
            <p>Search through our collection of articles, tutorials, and insights</p>
          </div>
        `;
      }
    }

    // Event listeners
    searchBtn.addEventListener('click', openSearch);

    if (searchClose) searchClose.addEventListener('click', closeSearch);
    searchOverlay.addEventListener('click', (e) => {
      if (e.target === searchOverlay) closeSearch();
    });

    // Filter event listeners
    initFilterListeners();

    // Search input handling with state transitions
    let searchTimeout;
    let suggestionTimeout;
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        clearTimeout(suggestionTimeout);
        currentQuery = e.target.value.trim();

        // State transition logic
        if (currentQuery.length === 0) {
          setState('idle');
          showInitialState();
          return;
        } else if (currentQuery.length === 1 && searchState === 'idle') {
          setState('active');
        }

        // Debounced search suggestions (faster response)
        suggestionTimeout = setTimeout(() => {
          if (currentQuery.length >= 2) {
            fetchSearchSuggestions(currentQuery);
          }
        }, 150);

        // Debounced search (slower, more comprehensive)
        searchTimeout = setTimeout(() => {
          if (currentQuery.length > 0) {
            performSearch();
          }
        }, 300);
      });
    }

    if (searchSubmit) {
      searchSubmit.addEventListener('click', () => {
        if (searchInput && searchInput.value.trim()) {
          currentQuery = searchInput.value.trim();
          if (searchState === 'idle') {
            setState('active');
          }
          performSearch();
        }
      });
    }

    // Load more functionality
    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', () => {
        loadMoreResults();
      });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === '/' && !searchOverlay.classList.contains('active')) {
        e.preventDefault();
        openSearch();
      }
      if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
        closeSearch();
      }
      if (e.key === 'Enter' && searchOverlay.classList.contains('active') && searchInput && searchInput.value.trim()) {
        currentQuery = searchInput.value.trim();
        if (searchState === 'idle') {
          setState('active');
        }
        performSearch();
      }
    });

    function initFilterListeners() {
      // Section filters (initial state)
      document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const section = btn.dataset.section;
          currentFilters.section = section;

          // Update active state
          document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');

          if (currentQuery) performSearch();
        });
      });

      // Tag filters
      document.querySelectorAll('.tag-chip').forEach(chip => {
        chip.addEventListener('click', () => {
          const tag = chip.dataset.tag;
          const index = currentFilters.tags.indexOf(tag);

          if (index > -1) {
            currentFilters.tags.splice(index, 1);
            chip.classList.remove('active');
          } else {
            currentFilters.tags.push(tag);
            chip.classList.add('active');
          }

          if (currentQuery) performSearch();
        });
      });

      // Sort options (results state)
      document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const sort = btn.dataset.sort;
          currentFilters.sort = sort;

          // Update active state
          document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');

          if (currentResults.length > 0) {
            sortResults();
            renderResults();
          }
        });
      });
    }

    function bindResultClickEvents() {
      const resultCards = searchResults.querySelectorAll('.result-card');
      resultCards.forEach(card => {
        card.addEventListener('click', () => {
          const href = card.getAttribute('data-href');
          if (href) {
            // Close search modal first
            closeSearch();
            
            // Navigate to the post
            if (window.RouteManager && typeof window.RouteManager.navigate === 'function') {
              const slug = href.replace('/blog/', '').replace('/', '');
              window.RouteManager.navigate(slug);
            } else {
              window.location.href = href;
            }
          }
        });
        
        // Add hover effect
        card.style.cursor = 'pointer';
      });
    }

    async function fetchSearchSuggestions(query) {
      try {
        const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}&limit=5`);
        if (!response.ok) return;
        
        const data = await response.json();
        
        // Update search input with suggestions (you can implement a dropdown here)
        // For now, we'll just log them for debugging
        
        // You could implement a suggestions dropdown here
        // showSearchSuggestions(data.suggestions);
      } catch (error) {
        console.error('Error fetching suggestions:', error);
      }
    }

    function showSearchSuggestions(suggestions) {
      // Implementation for showing suggestions dropdown
      // This would require additional HTML/CSS for the dropdown
    }

    async function performSearch() {
      if (!currentQuery) return;

      // Show loading state
      if (resultsCount) resultsCount.textContent = 'Searching...';
      if (searchResults) searchResults.innerHTML = '<div class="loading">Searching...</div>';

      try {
        // Call real backend API
        const searchData = {
          query: currentQuery,
          section: currentFilters.section,
          tags: currentFilters.tags,
          sort: currentFilters.sort,
          offset: 0,
          limit: resultsPerPage
        };

        const response = await fetch('/api/search/posts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(searchData)
        });

        if (!response.ok) {
          throw new Error(`Search failed: ${response.status}`);
        }

        const searchResponse = await response.json();
        currentResults = searchResponse.results || [];
        resultsOffset = resultsPerPage;
        
        renderSearchResults();
      } catch (error) {
        console.error('Search error:', error);
        // Show error state
        if (searchResults) {
          searchResults.innerHTML = `
            <div class="no-results">
              <div class="no-results-icon">
                <i class="ph-bold ph-warning-circle"></i>
              </div>
              <h3>Search Error</h3>
              <p>Something went wrong. Please try again.</p>
            </div>
          `;
        }
        if (resultsCount) resultsCount.textContent = 'Error occurred';
      }
    }

    async function loadMoreResults() {
      try {
        // Show loading state for load more button
        if (loadMoreBtn) {
          loadMoreBtn.disabled = true;
          loadMoreBtn.textContent = 'Loading...';
        }

        // Call real backend API with offset for pagination
        const searchData = {
          query: currentQuery,
          section: currentFilters.section,
          tags: currentFilters.tags,
          sort: currentFilters.sort,
          offset: resultsOffset,
          limit: resultsPerPage
        };

        const response = await fetch('/api/search/posts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(searchData)
        });

        if (!response.ok) {
          throw new Error(`Load more failed: ${response.status}`);
        }

        const searchResponse = await response.json();
        const nextResults = searchResponse.results || [];
        
        currentResults = [...currentResults, ...nextResults];
        resultsOffset += resultsPerPage;
        renderResults(true); // Append mode

        // Hide load more if no more results
        if (nextResults.length < resultsPerPage || searchResponse.total <= currentResults.length) {
          loadMoreContainer.style.display = 'none';
        }
      } catch (error) {
        console.error('Load more error:', error);
        // Show error state but keep load more button visible
        if (loadMoreBtn) {
          loadMoreBtn.disabled = false;
          loadMoreBtn.textContent = 'Try Again';
        }
      } finally {
        // Reset button text if not hidden
        if (loadMoreContainer.style.display !== 'none' && loadMoreBtn) {
          loadMoreBtn.textContent = 'Load More';
          loadMoreBtn.disabled = false;
        }
      }
    }

    function renderSearchResults() {
      updateUI();
      renderResults();
    }

    function updateUI() {
      const totalResults = currentResults.length;

      if (resultsCount) {
        if (totalResults === 0) {
          resultsCount.textContent = '0 results found';
        } else {
          resultsCount.textContent = totalResults === 1 ? '1 result found' : `${totalResults} results found`;
        }
      }

      // Show search stats (now using real data if available)
      if (searchStats && currentResults.length > 0) {
        // Try to get search time from first result if available
        const firstResult = currentResults[0];
        if (firstResult.search_score !== undefined) {
          // Use estimated search time based on results complexity
          const searchTime = Math.max(0.1, Math.log(totalResults + 1) * 0.1);
          searchStats.innerHTML = `<i class="ph-bold ph-clock"></i> ${searchTime.toFixed(2)}s`;
        }
      }

      // Show load more if there are potentially more results
      if (loadMoreContainer) {
        // We'll determine this more accurately after each search
        loadMoreContainer.style.display = 'block'; // Show by default, hide in loadMoreResults if needed
      }
    }

    function renderResults(append = false) {
      if (!searchResults) return;

      if (!append) {
        searchResults.innerHTML = '';
      }

      if (currentResults.length === 0) {
        searchResults.innerHTML = `
          <div class="no-results">
            <div class="no-results-icon">
              <i class="ph-bold ph-magnifying-glass"></i>
            </div>
            <h3>No Results Found</h3>
            <p>Try adjusting your search terms or filters</p>
          </div>
        `;
        return;
      }

      const resultsHTML = currentResults.map((result, index) =>
        createResultCard(result, append ? index + (resultsOffset - resultsPerPage) : index)
      ).join('');

      if (append) {
        searchResults.insertAdjacentHTML('beforeend', resultsHTML);
        // Bind click events for new results
        bindResultClickEvents();
      } else {
        searchResults.innerHTML = resultsHTML;
        // Bind click events for all results
        bindResultClickEvents();
      }
    }

    function createResultCard(result, index, append = false) {
      const delay = append ? 0 : index * 0.1;
      
      // Handle different field names from API vs mock data
      const title = result.title || 'Untitled';
      const excerpt = result.excerpt || 'No description available';
      const section = result.section || result.category || 'General';
      const author = result.author || 'NekwasaR';
      const date = result.published_at ? new Date(result.published_at).toLocaleDateString() : 'Recently';
      const views = result.view_count || result.views || 0;
      const tags = result.tags || [];
      const image = result.featured_image || result.image;
      const icon = result.icon || 'ph-article';
      
      return `
        <div class="result-card" style="animation-delay: ${delay}s" data-href="/${result.slug || ''}">
          <div class="result-media">
            ${image ? `<img src="${image}" alt="${title}" class="result-image">` :
          `<div class="result-icon"><i class="ph-bold ${icon}"></i></div>`}
          </div>
          <div class="result-content">
            <div class="result-category">${section}</div>
            <h3 class="result-title">${highlightText(title, currentQuery)}</h3>
            <p class="result-excerpt">${highlightText(excerpt, currentQuery)}</p>
            <div class="result-meta">
              <span class="result-author">${author}</span>
              <span class="result-date">${date}</span>
              ${tags.length > 0 ? `<div class="result-tags">${tags.map(tag => `<span class="result-tag">${tag}</span>`).join('')}</div>` : ''}
              <span class="result-stats">
                <i class="ph-bold ph-eye"></i> ${views}
                ${result.search_score ? `<span class="result-score" style="margin-left: 0.5rem; font-size: 0.8em; color: var(--t-muted);">Score: ${result.search_score}</span>` : ''}
              </span>
            </div>
          </div>
        </div>
      `;
    }

    function highlightText(text, query) {
      if (!query) return text;
      const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      return text.replace(regex, '<span class="highlight">$1</span>');
    }

    function sortResults() {
      currentResults.sort((a, b) => {
        switch (currentFilters.sort) {
          case 'recent':
            return new Date(b.date || 0) - new Date(a.date || 0);
          case 'popular':
            return (b.views || 0) - (a.views || 0);
          case 'relevance':
          default:
            return 0; // Keep original order for relevance
        }
      });
    }



    // Initialize suggestions
    loadDynamicSuggestions();
    initSuggestions();

    async function loadDynamicSuggestions() {
      try {
        // Fetch dynamic suggestions from real backend API
        const [trendingRes, recentRes, popularRes] = await Promise.all([
          fetch('/api/search/trending-topics?limit=3'),
          fetch('/api/search/recent-post'),
          fetch('/api/search/popular-searches?limit=3')
        ]);

        const trendingData = await trendingRes.json();
        const recentData = await recentRes.json();
        const popularData = await popularRes.json();

        // Create suggestion elements if they don't exist
        createSuggestionElements();

        // Update suggestions with real data
        // Trending: Based on highest views in past 7 days
        if (trendingData.trending_topics && trendingData.trending_topics.length > 0) {
          updateSuggestion('trending', { title: trendingData.trending_topics[0] });
        } else {
          updateSuggestion('trending', { title: 'Technology Trends' });
        }

        // Recent: Show the newest post title
        if (recentData.title) {
          updateSuggestion('recent', { title: recentData.title });
        } else {
          updateSuggestion('recent', { title: 'Latest Article' });
        }

        // Popular: Based on highest views of all time
        if (popularData.popular_searches && popularData.popular_searches.length > 0) {
          updateSuggestion('popular', { title: popularData.popular_searches[0] });
        } else {
          updateSuggestion('popular', { title: 'Popular Content' });
        }
      } catch (error) {
        console.error('Error loading dynamic suggestions:', error);
        // Fallback to default suggestions if API fails
        createSuggestionElements();
        updateSuggestion('trending', { title: 'AI & Technology' });
        updateSuggestion('recent', { title: 'Latest News' });
        updateSuggestion('popular', { title: 'Top Stories' });
      }
    }

    function createSuggestionElements() {
      const suggestionsContainer = document.getElementById('searchSuggestions');
      if (!suggestionsContainer || suggestionsContainer.children.length > 0) return;

      const suggestions = [
        { type: 'trending', icon: 'ph-trend-up', prefix: 'Trending:', text: 'Loading...' },
        { type: 'recent', icon: 'ph-clock', prefix: 'Recent:', text: 'Loading...' },
        { type: 'popular', icon: 'ph-star', prefix: 'Popular:', text: 'Loading...' }
      ];

      suggestions.forEach(suggestion => {
        const element = document.createElement('div');
        element.className = 'suggestion-item initial';
        element.setAttribute('data-type', suggestion.type);
        element.setAttribute('data-search-term', ''); // Will be updated when data loads
        element.innerHTML = `
          <i class="ph-bold ${suggestion.icon}"></i>
          <span>${suggestion.prefix} ${suggestion.text}</span>
        `;
        
        // Add click event listener
        // Add hover effects
        element.style.cursor = 'pointer';
        element.style.transition = 'all 0.2s ease';
        element.addEventListener('mouseenter', () => {
          element.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
        });
        element.addEventListener('mouseleave', () => {
          element.style.backgroundColor = '';
        });
        
        element.addEventListener('click', () => {
          const searchTerm = element.getAttribute('data-search-term') || element.querySelector('span')?.textContent || '';
          
          // Clean up the search term (remove prefix if present)
          let cleanSearchTerm = searchTerm;
          if (searchTerm.includes(': ')) {
            cleanSearchTerm = searchTerm.split(': ')[1];
          }

          if (searchInput && cleanSearchTerm.trim()) {
            searchInput.value = cleanSearchTerm.trim();
            currentQuery = cleanSearchTerm.trim();
            
            // Automatically perform the search
            if (searchState === 'idle') {
              setState('active');
            }
            performSearch();
          }
        });
        
        suggestionsContainer.appendChild(element);
      });
      
    }

    function updateSuggestion(type, postData) {
      const suggestion = document.querySelector(`[data-type="${type}"]`);
      if (!suggestion || !postData) return;
      
      const span = suggestion.querySelector('span');
      if (span) {
        const prefix = type.charAt(0).toUpperCase() + type.slice(1) + ':';
        span.textContent = `${prefix} ${postData.title || 'No posts found'}`;
        
        // Store the search term for click handling
        suggestion.setAttribute('data-search-term', postData.title || '');
      }
    }

    function initSuggestions() {
      // Use a timeout to ensure DOM elements are created first
      setTimeout(() => {
        const suggestions = document.querySelectorAll('.suggestion-item');
        suggestions.forEach(suggestion => {
          suggestion.addEventListener('click', () => {
            const type = suggestion.dataset.type;
            // Get the search term from the data attribute (more reliable)
            const searchTerm = suggestion.getAttribute('data-search-term') || suggestion.querySelector('span')?.textContent || '';
            
            // Clean up the search term (remove prefix if present)
            let cleanSearchTerm = searchTerm;
            if (searchTerm.includes(': ')) {
              cleanSearchTerm = searchTerm.split(': ')[1];
            }

            if (searchInput && cleanSearchTerm.trim()) {
              searchInput.value = cleanSearchTerm.trim();
              currentQuery = cleanSearchTerm.trim();
              
              // Automatically perform the search
              if (searchState === 'idle') {
                setState('active');
              }
              performSearch();
            }
          });
        });
      }, 100); // Small delay to ensure elements are created
    }
  }

  // Mobile Menu Modal Functionality
  function initMenuModal() {
    const menuBtn = document.getElementById('mobileMenuToggle') || document.getElementById('mobile-menu-toggle');
    const menuOverlay = document.getElementById('menuOverlay');
    const menuClose = document.getElementById('menuClose');

    if (!menuBtn || !menuOverlay) return;

    function openMenu() {
      menuOverlay.classList.add('active');
    }

    function closeMenu() {
      menuOverlay.classList.remove('active');
    }

    menuBtn.addEventListener('click', openMenu);
    if (menuClose) menuClose.addEventListener('click', closeMenu);
    menuOverlay.addEventListener('click', (e) => {
      if (e.target === menuOverlay) closeMenu();
    });

    // Close menu when clicking nav links
    const navLinks = menuOverlay.querySelectorAll('.mobile-nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', closeMenu);
    });
  }

  // Scroll to Top Functionality
  function initScrollToTop() {
    const scrollBtn = document.getElementById('scrollToTop');
    const progressRing = document.getElementById('scrollProgress');

    if (!scrollBtn) return;

    function updateScrollProgress() {
      const scrollTop = window.pageYOffset;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercent = (scrollTop / docHeight) * 100;

      if (progressRing) {
        progressRing.style.background = `conic-gradient(var(--secondary) ${scrollPercent}%, transparent ${scrollPercent}%)`;
      }

      // Show/hide button
      if (scrollTop > 300) {
        scrollBtn.classList.add('visible');
      } else {
        scrollBtn.classList.remove('visible');
      }
    }

    function scrollToTop() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }

    window.addEventListener('scroll', updateScrollProgress);
    scrollBtn.addEventListener('click', scrollToTop);
  }

  // Newsletter Form Functionality
  function initNewsletterForm() {
    const form = document.getElementById('newsletterForm');
    if (!form || form.__newsletterInited) return;

    const message = document.getElementById('newsletterMessage');
    const submitBtn = document.getElementById('subscribeBtn');
    const btnText = submitBtn ? submitBtn.querySelector('.btn-text') : null;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const nameEl = document.getElementById('subscriberName');
      const emailEl = document.getElementById('subscriberEmail');

      const name = nameEl?.value || (emailEl?.value || '').split('@')[0];
      const email = emailEl?.value || '';

      // Basic validation
      if (!email.trim()) {
        showMessage('Please enter an email address.', 'error');
        return;
      }

      if (!isValidEmail(email)) {
        showMessage('Please enter a valid email address.', 'error');
        return;
      }

      // Show loading state
      submitBtn.disabled = true;
      const originalText = btnText ? btnText.textContent : 'Subscribe';
      if (btnText) btnText.textContent = 'Subscribing...';
      if (message) message.classList.add('hidden');

      const startTime = Date.now();

      try {
        const formData = new FormData();
        formData.append('name', name);
        formData.append('email', email);

        const response = await fetch('/api/newsletter/subscribe', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();

        // Ensure "Subscribing..." shows for at least 1.5s
        const elapsed = Date.now() - startTime;
        const remaining = Math.max(0, 1500 - elapsed);

        setTimeout(() => {
          if (data.success || response.ok || (data.message && data.message.toLowerCase().includes('already'))) {
            message.innerHTML = `
              <div style="text-align: center; padding: 2rem; background: var(--base); border: 1px solid var(--stroke-elements); border-radius: var(--_radius-xl); margin-top: 2rem;">
                  <i class="ph-bold ph-check-circle" style="color: #22c55e; font-size: 4rem; margin-bottom: 1rem;"></i>
                  <h3 style="color: var(--t-bright); margin-bottom: 1rem; font-size: 2.2rem; font-weight: 700;">Successfully Subscribed!</h3>
                  <p style="color: var(--t-medium); font-size: 1.6rem;">Thank you for subscribing! We'll send the latest insights to ${email}.</p>
              </div>
            `;
            message.className = 'newsletter-message success-detailed';
            message.classList.remove('hidden');
            message.style.display = 'block';
            form.reset();
          } else {
            showMessage(data.message || 'Subscription failed. Please try again.', 'error');
          }

          submitBtn.disabled = false;
          if (btnText) btnText.textContent = originalText;
        }, remaining);

      } catch (error) {
        console.error('Newsletter Error:', error);
        const elapsed = Date.now() - startTime;
        const remaining = Math.max(0, 1500 - elapsed);

        setTimeout(() => {
          showMessage('Something went wrong. Please try again.', 'error');
          submitBtn.disabled = false;
          if (btnText) btnText.textContent = originalText;
        }, remaining);
      }
    });

    function showMessage(text, type) {
      if (!message) return;
      message.textContent = text;
      message.className = `newsletter-message ${type}`;
      message.classList.remove('hidden');
      message.style.display = 'block';

      setTimeout(() => {
        message.classList.add('hidden');
        message.style.display = 'none';
      }, 5000);
    }

    function isValidEmail(email) {
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return regex.test(email);
    }

    form.__newsletterInited = true;
  }
  window.initNewsletterForm = initNewsletterForm;

  // Smooth Scrolling
  function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
      link.addEventListener('click', (e) => {
        const targetId = link.getAttribute('href');
        const targetElement = document.querySelector(targetId);

        if (targetElement) {
          e.preventDefault();
          targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  // Card Link Click Handler - Now using Global Event Delegation for 100% reliability
  function initCardLinks() {
    // We use delegation on the document level to ensure all existing and future elements work
    // This is especially important for SPA navigation and dynamic content loading
    if (window.__globalClickDelegationActive) return;

    document.addEventListener('click', function (e) {
      // Find the closest clickable element (handling nested icons/text)
      // Priority: find the closest element that actually has a target URL
      const target = e.target.closest('[data-href], a[href], .nav-link[data-route]');

      if (!target) return;

      // EXCLUSION: If the user explicitly clicked an engagement area (like/comment/share), DON'T open the post modal
      if (e.target.closest('.engagement-metric, .post-modal-actions, .social-links, .share-links, .post-modal-action-btn')) {
        return;
      }

      // EXCLUSION: Respect target="_blank" attribute
      if (target.getAttribute('target') === '_blank') {
        return;
      }

      const href = target.getAttribute('data-href') || target.getAttribute('href');
      if (href) {
        e.preventDefault();
        e.stopPropagation();

        // Determine if it's a blog post or an SPA route
        const isInternal = href.startsWith('/') || href.startsWith(window.location.origin);

        // If it's an external link (like Portfolio), let the browser handle it
        if (!isInternal) return;

        // Standardize the path
        const path = href.replace(window.location.origin, '').split('?')[0];
        const segments = path.split('/').filter(Boolean);
        const systemRoutes = ['latest', 'popular', 'featured', 'others', 'topics', 'home', 'search', 'admin', 'api', 'back'];

        const isHome = path === '/' || path === '';
        const isSystem = segments.length > 0 && systemRoutes.includes(segments[0]);
        const isBlogPost = segments.length > 0 && !isSystem;

        if (isBlogPost) {
          e.preventDefault();
          e.stopPropagation();
          window.location.href = href;
        } else if (target.hasAttribute('data-route') || isSystem) {
          e.preventDefault();
          e.stopPropagation();

          const cleanPath = path.replace(/^\//, '');
          const [route, query] = cleanPath.split('?');
          const finalRoute = route || 'home';

          if (window.RouteManager && typeof window.RouteManager.navigate === 'function') {
            window.RouteManager.navigate(finalRoute, href.includes('?') ? '?' + href.split('?')[1] : '');
          } else {
            window.location.href = href;
          }
        }
      }
    }, true);

    window.__globalClickDelegationActive = true;
  }
  window.initCardLinks = initCardLinks;

  // Post Modal Functionality
  function initPostModal() {
    const modal = document.getElementById('postModal');
    const closeBtn = document.getElementById('postModalClose');
    const overlay = document.getElementById('postModal');

    if (!modal) return;

    // Close button functionality
    if (closeBtn) {
      closeBtn.addEventListener('click', closePostModal);
    }

    // Overlay click to close
    if (overlay) {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          closePostModal();
        }
      });
    }

    // Escape key to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.classList.contains('active')) {
        closePostModal();
      }
    });

    // Initialize like functionality
    initPostLike();
  }

  function openPostModal(postUrl) {
    const modal = document.getElementById('postModal');
    const content = document.getElementById('postModalContent');
    const title = document.querySelector('.post-modal-title-text');
    const category = document.querySelector('.post-modal-category');

    if (!modal || !content) return;

    // Show loading state
    content.innerHTML = `
      <div class="post-modal-loading">
        <div class="loading-spinner"></div>
        <p>Loading post content...</p>
      </div>
    `;

    // Set default title
    if (title) title.textContent = 'Loading...';
    if (category) category.textContent = 'Article';

    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Fetch post content (mock for now - replace with real API call)
    loadPostContent(postUrl);
  }
  window.openPostModal = openPostModal;

  function closePostModal() {
    const modal = document.getElementById('postModal');
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  }
  window.closePostModal = closePostModal;

  // Like functionality for post modal
  function initPostLike() {
    const likeBtn = document.getElementById('postModalLike');
    if (!likeBtn) return;

    let isLiked = false;
    let currentLikes = 0;
    let currentPostId = null;
    let currentFingerprint = null;

    // Generate a robust fallback fingerprint
    function generateFallbackFingerprint() {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillText('fallback fingerprint test', 2, 2);

      const fingerprint = [
        navigator.userAgent,
        navigator.language,
        screen.width + 'x' + screen.height,
        new Date().getTimezoneOffset(),
        canvas.toDataURL()
      ].join('|');

      // Simple hash function
      let hash = 0;
      for (let i = 0; i < fingerprint.length; i++) {
        const char = fingerprint.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
      }

      return 'fallback_' + Math.abs(hash) + '_' + Date.now();
    }

    // Function to reset like state for new post
    window.resetPostLike = async function (postId, likeCount = 0) {
      currentPostId = postId;
      currentLikes = likeCount;
      isLiked = false; // Reset to not liked for new post

      // Get device fingerprint with multiple fallback strategies
      let fingerprintReady = false;

      // Strategy 1: Try to use getDeviceFingerprint() if available
      if (window.getDeviceFingerprint && typeof window.getDeviceFingerprint === 'function') {
        try {
          currentFingerprint = window.getDeviceFingerprint();
          fingerprintReady = !!currentFingerprint;
        } catch (error) {
          console.warn('getDeviceFingerprint() failed:', error);
        }
      }

      // Strategy 2: Try async generation if sync failed
      if (!fingerprintReady && window.generateDeviceFingerprint) {
        try {
          currentFingerprint = await window.generateDeviceFingerprint();
          fingerprintReady = !!currentFingerprint;
        } catch (error) {
          console.warn('generateDeviceFingerprint() failed:', error);
        }
      }

      // Strategy 3: Generate a robust fallback fingerprint
      if (!fingerprintReady) {
        currentFingerprint = generateFallbackFingerprint();
      }

      // Update UI
      const countSpan = likeBtn.querySelector('.action-count');
      const icon = likeBtn.querySelector('i');

      if (countSpan) {
        countSpan.textContent = currentLikes;
      }
      if (icon) {
        icon.className = 'ph-bold ph-heart';
      }

      // Check like status with backend
      try {
        await checkLikeStatus();
      } catch (error) {
        console.warn('Failed to check like status:', error);
      }
    };

    // Check if user has already liked this post
    async function checkLikeStatus() {
      if (!currentFingerprint || !currentPostId) return;

      try {
        const response = await fetch(`/api/blogs/${currentPostId}/likes/status?fingerprint=${encodeURIComponent(currentFingerprint)}`);
        if (response.ok) {
          const data = await response.json();
          isLiked = data.liked;

          const icon = likeBtn.querySelector('i');
          if (icon) {
            icon.className = isLiked ? 'ph-fill ph-heart text-red-500' : 'ph-bold ph-heart';
          }
        }
      } catch (error) {
        console.warn('Failed to check like status:', error);
      }
    }

    likeBtn.addEventListener('click', async () => {
      const countSpan = likeBtn.querySelector('.action-count');
      const icon = likeBtn.querySelector('i');

      if (!currentFingerprint) {
        console.error('No device fingerprint available');
        return;
      }

      try {
        // Toggle like state
        isLiked = !isLiked;

        // Update UI immediately
        if (isLiked) {
          icon.className = 'ph-fill ph-heart text-red-500';
          currentLikes++;
        } else {
          icon.className = 'ph-bold ph-heart';
          currentLikes--;
        }

        if (countSpan) {
          countSpan.textContent = currentLikes;
        }

        if (isLiked) {
          // Like the post
          const response = await fetch(`/api/blogs/${currentPostId}/likes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              fingerprint: currentFingerprint,
              user_identifier: currentFingerprint // Legacy field
            })
          });

          if (!response.ok) {
            throw new Error(`Like failed: ${response.status}`);
          }
        } else {
          // Unlike the post
          const response = await fetch(`/api/blogs/${currentPostId}/likes?fingerprint=${encodeURIComponent(currentFingerprint)}`, {
            method: 'DELETE'
          });

          if (!response.ok) {
            throw new Error(`Unlike failed: ${response.status}`);
          }
        }

      } catch (error) {
        console.error('Like error:', error);
        // Revert UI on error
        isLiked = !isLiked;
        if (isLiked) {
          icon.className = 'ph-fill ph-heart text-red-500';
          currentLikes++;
        } else {
          icon.className = 'ph-bold ph-heart';
          currentLikes--;
        }
        if (countSpan) {
          countSpan.textContent = currentLikes;
        }
      }
    });
  }

  async function loadPostContent(postUrl) {
    try {
      // Extract post slug from URL
      const slug = postUrl.split('/').pop();
      const apiUrl = `/api/blogs/${slug}`;

      const response = await fetch(apiUrl);
      const postData = await response.json();

      renderPostInModal(postData);
    } catch (error) {
      console.error('Error loading post:', error);
      // Fallback to mock content
      renderMockPostInModal(postUrl);
    }
  }

  function renderPostInModal(postData) {
    const content = document.getElementById('postModalContent');
    const title = document.querySelector('.post-modal-title-text');
    const category = document.querySelector('.post-modal-category');

    if (!content) return;

    // Update title and category
    if (title) title.textContent = postData.title || 'Post Title';
    if (category) category.textContent = postData.category || 'Article';

    // Reset like state for new post
    if (window.resetPostLike) {
      window.resetPostLike(postData.id || postData.slug, postData.like_count || 0);
    }

    // Render content
    content.innerHTML = `
      <div class="post-meta">
        <span class="author">${postData.author || 'NekwasaR'}</span>
        <span class="date">${postData.published_at ? new Date(postData.published_at).toLocaleDateString() : 'Recent'}</span>
        <span class="views">${postData.view_count || 0} views</span>
      </div>
      <div class="post-content">
        ${postData.content || '<p>Post content would appear here...</p>'}
      </div>
    `;
  }

  function renderMockPostInModal(postUrl) {
    const content = document.getElementById('postModalContent');
    const title = document.querySelector('.post-modal-title-text');
    const category = document.querySelector('.post-modal-category');

    if (!content) return;

    // Mock data based on URL
    const mockPosts = {
      'ai-revolutionizing-healthcare': {
        title: 'How AI is Revolutionizing Healthcare',
        category: 'Technology',
        author: 'NekwasaR',
        like_count: 42,
        content: `
          <h2>The Future of Medical Diagnosis</h2>
          <p>Artificial Intelligence is transforming healthcare in unprecedented ways. From early disease detection to personalized treatment plans, AI systems are becoming indispensable tools for medical professionals.</p>

          <h3>Key Applications</h3>
          <ul>
            <li>Medical imaging analysis</li>
            <li>Drug discovery acceleration</li>
            <li>Patient risk prediction</li>
            <li>Telemedicine enhancement</li>
          </ul>

          <blockquote>
            "AI doesn't replace doctors—it empowers them to make better decisions faster."
          </blockquote>

          <p>The integration of AI in healthcare represents one of the most promising developments of our time, with the potential to save millions of lives and improve healthcare outcomes worldwide.</p>
        `
      },
      'rise-of-quantum-computing': {
        title: 'The Rise of Quantum Computing',
        category: 'Technology',
        author: 'NekwasaR',
        like_count: 28,
        content: `
          <h2>Understanding Quantum Advantage</h2>
          <p>Quantum computing represents a paradigm shift in computational power. Unlike classical computers that use bits, quantum computers use quantum bits or qubits that can exist in multiple states simultaneously.</p>

          <h3>Current Developments</h3>
          <p>Major tech companies and research institutions are racing to build practical quantum computers. Recent breakthroughs in error correction and qubit stability have brought us closer to quantum advantage.</p>

          <h3>Real-World Applications</h3>
          <ul>
            <li>Cryptographic systems</li>
            <li>Drug discovery</li>
            <li>Financial modeling</li>
            <li>Climate simulation</li>
          </ul>
        `
      }
    };

    const slug = postUrl.split('/').pop();
    const postData = mockPosts[slug] || {
      title: 'Post Title',
      category: 'Article',
      author: 'NekwasaR',
      like_count: 0,
      content: '<p>This is a preview of the post content. Click "Read Full Article" to view the complete post.</p>'
    };

    if (title) title.textContent = postData.title;
    if (category) category.textContent = postData.category;

    // Reset like state for new post
    if (window.resetPostLike) {
      window.resetPostLike(slug, postData.like_count);
    }

    content.innerHTML = `
      <div class="post-meta">
        <span class="author">${postData.author}</span>
        <span class="date">Recent</span>
        <span class="views">1.2k views</span>
      </div>
      <div class="post-content">
        ${postData.content}
      </div>
    `;
  }


  // Animation Triggers
  function initAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
        }
      });
    }, observerOptions);

    // Observe elements for animation
    const animateElements = document.querySelectorAll('.article-card, .featured-post, .large-post, .sidebar-widget');
    animateElements.forEach(el => observer.observe(el));
  }

  // Utility Functions
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  function throttle(func, limit) {
    let inThrottle;
    return function () {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    }
  }

  // Performance optimizations
  window.addEventListener('load', () => {
    // Preload critical resources
    const images = document.querySelectorAll('img[data-src]');
    images.forEach(img => {
      img.src = img.dataset.src;
    });
  });

  // Error handling
  window.addEventListener('error', (e) => {
    console.error('Blog JavaScript Error:', e.error);
  });

  // Service worker registration (for PWA features)
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      // Register service worker when ready
      // navigator.serviceWorker.register('/sw.js');
    });
  }

  // --- Topics & Tags Functionality ---

  async function initTopics() {
    const params = new URLSearchParams(window.location.search);
    const activeTagSlug = params.get('tag');

    // Update UI for active tag
    const indicator = document.getElementById('active-tag-indicator');
    const tagNameSpan = document.getElementById('active-tag-name');
    const topicsTitle = document.getElementById('topics-title');
    const topicsDescription = document.getElementById('topics-description');

    if (activeTagSlug) {
      indicator?.classList.remove('hidden');
      if (tagNameSpan) tagNameSpan.textContent = activeTagSlug.charAt(0).toUpperCase() + activeTagSlug.slice(1);
      if (topicsTitle) topicsTitle.textContent = `#${activeTagSlug}`;
      if (topicsDescription) topicsDescription.textContent = `Browse all articles featuring the #${activeTagSlug} tag.`;
    } else {
      indicator?.classList.add('hidden');
      if (topicsTitle) topicsTitle.textContent = 'Explore Everything';
      if (topicsDescription) topicsDescription.textContent = 'Dive into curated bundles, expert lists, and detailed guides across various disciplines.';
    }

    try {
      // 1. Fetch and render tag cloud
      const tagsRes = await fetch('/api/blogs/tags');
      const tagsData = await tagsRes.json();
      renderTagCloud(tagsData.tags, activeTagSlug);

      // 2. Fetch and render posts
      const searchBody = activeTagSlug ? { tags: [activeTagSlug], limit: 20 } : { query: '', limit: 20 };
      const postsRes = await fetch('/api/search/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchBody)
      });
      const postsData = await postsRes.json();
      renderTopicResults(postsData.results);

    } catch (error) {
      console.error('Error loading topics:', error);
    }
  }

  function renderTagCloud(tags, activeSlug) {
    const cloud = document.getElementById('topics-tag-cloud');
    if (!cloud) return;

    if (!tags || tags.length === 0) {
      cloud.innerHTML = '<p class="text-t-muted text-sm italic">No tags found.</p>';
      return;
    }

    cloud.innerHTML = tags.map(tag => `
      <a href="/topics?tag=${tag.slug}" 
         class="tag-pill px-5 py-2 border border-stroke-elements rounded-full text-sm font-semibold transition-colors ${tag.slug === activeSlug ? 'active bg-purple-600 text-white' : 'text-t-bright bg-white'}"
         onclick="event.preventDefault(); window.RouteManager.navigate('topics', '?tag=${tag.slug}')">
        #${tag.name}
      </a>
    `).join('');
  }

  function renderTopicResults(posts) {
    const container = document.getElementById('topics-results');
    const emptyState = document.getElementById('topics-empty');
    if (!container) return;

    if (!posts || posts.length === 0) {
      container.classList.add('hidden');
      emptyState?.classList.remove('hidden');
      return;
    }

    container.classList.remove('hidden');
    emptyState?.classList.add('hidden');

    container.innerHTML = posts.map(post => `
    <article class="article-card rounded-[1.5rem] border border-stroke-elements bg-white overflow-hidden flex flex-col shadow-sm hover:shadow-xl transition-all h-full cursor-pointer" data-href="/${post.slug}">
      <div class="card-link h-full flex flex-col">
          <div class="relative aspect-video overflow-hidden">
            <img src="${post.featured_image || 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop'}" 
                 class="w-full h-full object-cover transition-transform duration-500 hover:scale-105" 
                 alt="${post.title}" loading="lazy">
            <div class="absolute top-4 left-4 bg-purple-600 text-white px-3 py-1 rounded-full text-xs font-bold">${(post.tags && post.tags.length) ? post.tags[0] : 'Tech'}</div>
          </div>
          <div class="p-6 flex flex-col flex-grow">
            <div class="flex items-center gap-2 text-xs text-t-muted mb-3">
              <span>${post.published_at ? new Date(post.published_at).toLocaleDateString() : 'Recent'}</span>
              <span>•</span>
              <span>${post.view_count || 0} views</span>
            </div>
            <h3 class="text-xl font-bold text-t-bright leading-tight mb-3 line-clamp-2">${post.title}</h3>
            <p class="text-sm text-t-medium line-clamp-3 mb-4">${post.excerpt || 'Read this insightful article from our collection...'}</p>
            <div class="mt-auto flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-widest text-purple-600 hover:text-purple-700">Read More →</span>
              <div class="flex items-center gap-3 text-t-muted text-xs">
                <span class="flex items-center gap-1"><i class="ph-bold ph-heart"></i> ${post.like_count || 0}</span>
                <span class="flex items-center gap-1"><i class="ph-bold ph-chat-circle"></i> ${post.comment_count || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </article>
    `).join('');

    // Re-bind click events for new cards
    if (window.initCardLinks) window.initCardLinks();

    // Re-trigger entrance animations
    initAnimations();
  }

  window.clearTagFilter = function () {
    if (window.RouteManager) {
      window.RouteManager.navigate('topics');
    } else {
      window.location.href = '/topics';
    }
  };

  window.initTopics = initTopics;

  // --- End Topics & Tags ---

  // Expose re-init for SPA route swaps
  window.BlogPageInit = initBlog;

  // Share functions for inline social buttons
  window.shareOnFacebook = function () {
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent(document.title);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}&title=${title}`, '_blank', 'width=600,height=400');
  };

  window.shareOnTelegram = function () {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(document.title);
    window.open(`https://t.me/share/url?url=${url}&text=${text}`, '_blank');
  };

  window.shareOnReddit = function () {
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent(document.title);
    window.open(`https://www.reddit.com/submit?url=${url}&title=${title}`, '_blank');
  };

  window.shareOnWhatsApp = function () {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(document.title);
    window.open(`https://wa.me/?text=${text}%20${url}`, '_blank');
  };

})();
