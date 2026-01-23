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
});

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
}

async function loadProducts() {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '<div class="col-span-full text-center py-20 animate-pulse">Loading Assets...</div>';

    try {
        const res = await fetch('/api/store/products');
        if (!res.ok) throw new Error("Failed to fetch");
        STATE_STORE.products = await res.json();
        renderProducts();
    } catch (e) {
        grid.innerHTML = '<div class="col-span-full text-center text-red-500">Failed to load products.</div>';
    }
}

function renderProducts() {
    const grid = document.getElementById('product-grid');
    if (!grid) return; // Guard clause
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
        // New Premium Card Classes
        card.className = "product-card glass-panel rounded-2xl overflow-hidden group flex flex-col h-full border border-stroke-elements hover:border-accent/50";

        // Image / Video Logic
        const hero = p.images.find(i => i.is_hero) || p.images[0] || { file_url: '/store/img/placeholder.jpg' };

        // Price Logic
        let priceTag = `$${p.price}`;
        let actionBtn = `
            <button onclick="addToCart(${p.id})" class="w-full bg-base-shade hover:bg-accent text-t-bright hover:text-white transition-all py-4 font-bold border-t border-stroke-elements font-syne uppercase tracking-wider text-sm flex items-center justify-center gap-2 group-hover/btn:gap-3">
                <i class="ph-bold ph-shopping-cart"></i> Add to Cart
            </button>`;

        if (p.is_private_listing) {
            priceTag = '<span class="text-amber-500 flex items-center gap-1 text-sm font-bold uppercase tracking-wider"><i class="ph-fill ph-lock-key"></i> Restricted</span>';
            actionBtn = `
                <button onclick="openAccessModal(${p.id})" class="w-full bg-amber-500/10 hover:bg-amber-500 text-amber-500 hover:text-black transition-all py-4 font-bold border-t border-amber-500/20 font-syne uppercase tracking-wider text-sm flex items-center justify-center gap-2">
                    <i class="ph-bold ph-key"></i> Request Access
                </button>`;
        }

        if (p.billing_scheme === 'recurring') {
            priceTag += ` <span class="text-xs text-t-muted font-normal">/${p.subscription_interval}</span>`;
        }

        card.innerHTML = `
            <div class="relative h-64 bg-base-shade overflow-hidden group-hover:opacity-100 transition-all">
                <img src="${hero.file_url}" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 group-hover:scale-110 transition duration-700 ease-out" alt="${p.name}" onerror="this.src='https://placehold.co/600x400/1e293b/FFF?text=Asset'">
                
                <div class="absolute inset-0 bg-gradient-to-t from-base to-transparent opacity-90"></div>
                
                <div class="absolute top-4 right-4">
                    <span class="bg-base/80 backdrop-blur border border-stroke-elements text-t-bright text-[10px] font-bold font-syne px-3 py-1 rounded-full uppercase tracking-widest shadow-lg">
                        ${p.product_type.replace('_', ' ')}
                    </span>
                </div>

                <div class="absolute bottom-4 left-6 right-6 translate-y-2 group-hover:translate-y-0 transition-transform duration-500">
                     <h3 class="text-xl font-bold font-display text-t-bright leading-tight mb-1 group-hover:text-accent transition-colors">${p.name}</h3>
                     <div class="text-lg font-syne font-bold text-t-medium">${priceTag}</div>
                </div>
            </div>
            
            <div class="p-6 flex-1 flex flex-col bg-base-tint/30 relative">
                <p class="text-t-muted text-sm leading-relaxed line-clamp-3 mb-6 flex-1 font-inter">
                    ${p.short_description || p.description?.replace(/<[^>]*>?/gm, '').substring(0, 120) + '...' || 'Premium digital asset for professional use.'}
                </p>
                
                <!-- Quick Specs (Fake for demo, real in production) -->
                <div class="flex items-center gap-4 text-xs text-t-muted font-mono mb-4 border-t border-stroke-elements pt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-500 delay-100">
                    <span class="flex items-center gap-1"><i class="ph-bold ph-file-code"></i> Source</span>
                    <span class="flex items-center gap-1"><i class="ph-bold ph-shield-check"></i> Verified</span>
                </div>
            </div>
            ${actionBtn}
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
        container.innerHTML = `
            <button onclick="openAuthModal()" class="px-5 py-2.5 bg-t-bright text-base-shade font-bold rounded-xl hover:opacity-90 transition shadow-lg hover:shadow-accent/20">
                Sign In
            </button>
        `;
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
