// store-client.js
// Handles all Client-Side logic for the Store

const API_BASE = '/api/store';
const STATE_STORE = { // Renamed safely to avoid global conflicts
    products: [],
    cart: JSON.parse(localStorage.getItem('nekwasar_cart')) || [],
    user: null,
    filter: 'all'
};

document.addEventListener('DOMContentLoaded', () => {
    initStore().catch(console.error);

    // Scroll Listener for Hero Hiding
    window.addEventListener('scroll', () => {
        if (!localStorage.getItem('store_hero_hidden')) {
            const catalog = document.getElementById('catalog');
            if (catalog && window.scrollY > catalog.offsetTop - 100) {
                hideHero();
            }
        }
    }, { passive: true });
});

// Modal Logic (Moved from inline)
function openAccessModal() {
    const modal = document.getElementById('access-modal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
}
window.openAccessModal = openAccessModal; // Expose to global scope for HTML onclick

async function initStore() {
    // 1. Fetch User (if any)
    try {
        const res = await fetch('/api/auth/me');
        if (res.ok) STATE_STORE.user = await res.json();
    } catch (e) {
        // console.log("Guest User");
    }

    updateAuthUI();

    // 2. Fetch Products
    await loadProducts();

    // 3. Update Cart Badge
    updateCartCount();

    // 4. Check Hero State (Removed: Slider is permanent now)
}

async function loadProducts() {
    const grid = document.getElementById('product-grid');
    // Removed loading spinner to support SSR (Server Side Rendering)

    try {
        const res = await fetch('/api/store/products');
        if (!res.ok) {
            const errBody = await res.text();
            throw new Error(`Server returned ${res.status}: ${errBody}`);
        }
        STATE_STORE.products = await res.json();
        // Optional: Only render if we need to update/hydrate. 
        // For now, re-rendering ensures client-side state matches UI for filtering.
        // renderProducts(); // Disabled to prevent flicker of SSR content
    } catch (e) {
        console.error("Failed to hydrate products:", e);
        // Don't show error to user if SSR content is already there
    }
}

function setFilter(type) {
    STATE_STORE.filter = type;

    // Update active button state visually
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach(btn => {
        if (btn.dataset.filter === type) {
            btn.classList.add('bg-accent', 'text-white', 'shadow-lg');
            btn.classList.remove('bg-base-tint', 'text-t-muted', 'border');
        } else {
            btn.classList.remove('bg-accent', 'text-white', 'shadow-lg');
            btn.classList.add('bg-base-tint', 'text-t-muted', 'border');
        }
    });

    renderProducts();
}
window.setFilter = setFilter; // Expose global

function renderProducts() {
    const grid = document.getElementById('product-grid');
    if (!grid) return;
    grid.innerHTML = '';

    const filtered = STATE_STORE.filter === 'all'
        ? STATE_STORE.products
        : STATE_STORE.products.filter(p => p.product_type === STATE_STORE.filter);

    if (filtered.length === 0) {
        grid.innerHTML = '<div class="col-span-full text-center text-t-muted py-20">No assets found in this category.</div>';
        return;
    }

    filtered.forEach(p => {
        const card = document.createElement('div');
        card.className = "product-card bg-base-shade rounded-xl overflow-hidden group flex flex-col h-full border border-stroke-elements hover:border-accent/50 cursor-pointer transition-all duration-300 hover:-translate-y-1 shadow-lg";
        card.onclick = (e) => {
            if (e.target.closest('button')) return;
            window.location.href = `/product/${p.slug}`;
        };

        const hero = p.images.find(i => i.is_hero) || p.images[0] || { file_url: '/store/img/placeholder.jpg' };

        // Price Tag
        let priceTag = `<span class="text-t-bright font-bold">$${p.price}</span>`;
        if (p.is_private_listing) {
            priceTag = '<span class="text-amber-500 font-bold uppercase text-xs tracking-wider"><i class="ph-fill ph-lock-key"></i> Restricted</span>';
        }

        card.innerHTML = `
            <div class="relative aspect-[4/3] bg-base-shade overflow-hidden">
                <img src="${hero.file_url}" class="w-full h-full object-cover group-hover:scale-105 transition duration-700 ease-out" alt="${p.name}" onerror="this.src='https://placehold.co/600x400/1e293b/FFF?text=Asset'">
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60"></div>
                <div class="absolute top-3 right-3">
                    <span class="bg-black/60 backdrop-blur border border-white/10 text-white text-[10px] font-bold font-syne px-2 py-1 rounded uppercase tracking-wider">
                        ${p.product_type.replace('_', ' ')}
                    </span>
                </div>
            </div>
            <div class="p-4 bg-[#141414] flex-1 flex flex-col justify-between border-t border-stroke-elements">
                <div>
                    <h3 class="text-lg font-bold font-display text-white leading-tight mb-1 group-hover:text-accent transition-colors line-clamp-1">${p.name}</h3>
                    <div class="flex justify-between items-center mt-2">
                        <span class="text-xs text-t-muted font-medium uppercase tracking-wide">${p.category ? p.category.name : 'Digital Asset'}</span>
                        <div class="font-syne">${priceTag}</div>
                    </div>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function updateAuthUI() {
    const container = document.getElementById('auth-section');
    if (!container) return;

    if (STATE_STORE.user) {
        container.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="text-right hidden sm:block">
                    <div class="text-sm font-bold text-t-bright">${STATE_STORE.user.name || STATE_STORE.user.email.split('@')[0]}</div>
                    <div class="text-xs text-t-muted">Member</div>
                </div>
                <img src="${STATE_STORE.user.avatar || 'https://ui-avatars.com/api/?name=' + (STATE_STORE.user.name || 'User')}" class="w-10 h-10 rounded-full border border-stroke-elements">
            </div>
        `;
    } else {
        <button onclick="openAuthModal()" class="flex items-center justify-center p-2 md:p-0 md:px-5 md:py-2.5 md:bg-t-bright md:text-base-shade md:font-bold md:rounded-xl md:shadow-lg hover:opacity-90 transition text-t-muted hover:text-accent">
            <i class="ph ph-user text-2xl md:hidden"></i>
            <span class="hidden md:inline">Sign In</span>
        </button>
    }
}

// --- Cart Actions ---

function addToCart(productId) {
    const product = STATE_STORE.products.find(p => p.id === productId);
    if (!product) return;

    // Check if exists
    const existing = STATE_STORE.cart.find(i => i.product_id === productId);
    if (existing) {
        existing.quantity += 1;
    } else {
        STATE_STORE.cart.push({ product_id: product.id, quantity: 1, name: product.name, price: product.price });
    }

    saveCart();

    // Visual Feedback (Toast)
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-5 right-5 bg-green-500 text-white px-6 py-3 rounded-xl shadow-2xl z-[200] flex items-center gap-3 animate-bounce';
    toast.innerHTML = '<i class="ph-fill ph-check-circle text-xl"></i> Added to Cart';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
}

function updateCartCount() {
    const count = STATE_STORE.cart.reduce((acc, item) => acc + item.quantity, 0);
    const badge = document.getElementById('cart-count');
    badge.innerText = count;
    badge.classList.toggle('hidden', count === 0);
}

function saveCart() {
    localStorage.setItem('nekwasar_cart', JSON.stringify(STATE_STORE.cart));
    updateCartCount();
}

// --- Checkout ---

async function checkout() {
    if (STATE_STORE.cart.length === 0) return alert("Cart is empty");

    // Call Checkout API
    try {
        const res = await fetch(`${API_BASE}/checkout/intent`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(STATE_STORE.cart)
        });

        const data = await res.json();
        if (data.url) {
            window.location.href = data.url; // Redirect to Stripe
        } else {
            alert("Checkout Error: " + JSON.stringify(data));
        }
    } catch (e) {
        alert("Network Error");
    }
}

// Global Search Helper (For Hero)
function searchProducts(query) {
    if (!query) {
        // Reset to current category filter
        renderProducts();
        return;
    }

    const term = query.toLowerCase();
    const filtered = STATE_STORE.products.filter(p =>
        p.name.toLowerCase().includes(term) ||
        (p.description && p.description.toLowerCase().includes(term))
    );

    const grid = document.getElementById('product-grid');
    if (!grid) return;
    grid.innerHTML = '';

    if (filtered.length === 0) {
        grid.innerHTML = '<div class="col-span-full text-center text-t-muted py-20">No matches found.</div>';
        return;
    }

    // Reuse Card Logic (Ideally this should be a shared component function, but duplication is safe here for speed)
    filtered.forEach(p => {
        const card = document.createElement('div');
        card.className = "product-card bg-base-shade rounded-xl overflow-hidden group flex flex-col h-full border border-stroke-elements hover:border-accent/50 cursor-pointer transition-all duration-300 hover:-translate-y-1 shadow-lg";
        card.onclick = (e) => {
            if (e.target.closest('button')) return;
            window.location.href = `/product/${p.slug}`;
        };

        const hero = p.images.find(i => i.is_hero) || p.images[0] || { file_url: '/store/img/placeholder.jpg' };

        let priceTag = `<span class="text-t-bright font-bold">$${p.price}</span>`;
        if (p.is_private_listing) {
            priceTag = '<span class="text-amber-500 font-bold uppercase text-xs tracking-wider"><i class="ph-fill ph-lock-key"></i> Restricted</span>';
        }

        card.innerHTML = `
            <div class="relative aspect-[4/3] bg-base-shade overflow-hidden">
                <img src="${hero.file_url}" class="w-full h-full object-cover group-hover:scale-105 transition duration-700 ease-out" alt="${p.name}" onerror="this.src='https://placehold.co/600x400/1e293b/FFF?text=Asset'">
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60"></div>
                <div class="absolute top-3 right-3">
                    <span class="bg-black/60 backdrop-blur border border-white/10 text-white text-[10px] font-bold font-syne px-2 py-1 rounded uppercase tracking-wider">
                        ${p.product_type.replace('_', ' ')}
                    </span>
                </div>
            </div>
            <div class="p-4 bg-[#141414] flex-1 flex flex-col justify-between border-t border-stroke-elements">
                <div>
                    <h3 class="text-lg font-bold font-display text-white leading-tight mb-1 group-hover:text-accent transition-colors line-clamp-1">${p.name}</h3>
                    <div class="flex justify-between items-center mt-2">
                        <span class="text-xs text-t-muted font-medium uppercase tracking-wide">${p.category ? p.category.name : 'Digital Asset'}</span>
                        <div class="font-syne">${priceTag}</div>
                    </div>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}
window.handleHeroSearch = searchProducts; // Map the index.html function name
