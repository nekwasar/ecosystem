// store-client.js
// Handles all Client-Side logic for the Store

const API_BASE = '/api/store';
const STATE = {
    products: [],
    cart: JSON.parse(localStorage.getItem('nekwasar_cart')) || [],
    user: null, // Will fetch from /api/auth/me
    filter: 'all'
};

document.addEventListener('DOMContentLoaded', async () => {
    await initStore();
});

async function initStore() {
    // 1. Fetch User (if any)
    try {
        const res = await fetch('/api/auth/me');
        if (res.ok) STATE.user = await res.json();
    } catch (e) {
        console.log("Guest User");
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
        const res = await fetch(`${API_BASE}/products`);
        STATE.products = await res.json();
        renderProducts();
    } catch (e) {
        grid.innerHTML = '<div class="col-span-full text-center text-red-500">Failed to load products.</div>';
    }
}

function renderProducts() {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '';

    const filtered = STATE.filter === 'all'
        ? STATE.products
        : STATE.products.filter(p => p.product_type === STATE.filter);

    filtered.forEach(p => {
        const card = document.createElement('div');
        card.className = "glass-card rounded-2xl overflow-hidden hover:shadow-2xl hover:shadow-primary/10 transition group flex flex-col h-full";

        // Image / Video Logic
        const hero = p.images.find(i => i.is_hero) || p.images[0] || { file_url: 'https://placehold.co/600x400/101010/FFF?text=No+Image' };

        // Price Logic
        let priceTag = `$${p.price}`;
        let actionBtn = `<button onclick="addToCart(${p.id})" class="w-full bg-white dark:bg-white/10 hover:bg-primary hover:text-white dark:hover:bg-primary transition py-3 rounded-b-xl font-medium border-t border-gray-100 dark:border-white/5">Add to Cart</button>`;

        if (p.is_private_listing) {
            priceTag = '<span class="text-amber-500 flex items-center gap-1"><i class="ph-fill ph-lock-key"></i> Restricted</span>';
            actionBtn = `<button onclick="openAccessModal(${p.id})" class="w-full bg-amber-500/10 text-amber-500 hover:bg-amber-500 hover:text-black transition py-3 rounded-b-xl font-medium border-t border-amber-500/20">Request Access</button>`;
        }

        if (p.billing_scheme === 'recurring') {
            priceTag += ` <span class="text-sm opacity-60">/${p.subscription_interval}</span>`;
        }

        card.innerHTML = `
            <div class="relative h-56 bg-gray-100 dark:bg-white/5 overflow-hidden">
                <img src="${hero.file_url}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500" alt="${p.name}">
                <div class="absolute top-3 right-3 bg-black/60 backdrop-blur text-white text-xs px-2 py-1 rounded-md border border-white/10">
                    ${p.product_type.replace('_', ' ')}
                </div>
            </div>
            
            <div class="p-6 flex-1 flex flex-col">
                <h3 class="text-xl font-bold font-display mb-2 text-gray-900 dark:text-white leading-tight">${p.name}</h3>
                <p class="text-gray-500 dark:text-gray-400 text-sm line-clamp-2 mb-4 flex-1">${p.short_description || p.description?.substring(0, 100) || 'No description'}</p>
                
                <div class="flex items-center justify-between mt-auto">
                    <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">${priceTag}</div>
                </div>
            </div>
            ${actionBtn}
        `;

        grid.appendChild(card);
    });
}

function updateAuthUI() {
    const container = document.getElementById('auth-section');
    if (STATE.user) {
        container.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="text-right hidden sm:block">
                    <div class="text-sm font-bold text-gray-900 dark:text-white">${STATE.user.name || STATE.user.email.split('@')[0]}</div>
                    <div class="text-xs text-gray-500">Member</div>
                </div>
                <img src="${STATE.user.avatar || 'https://ui-avatars.com/api/?name=' + (STATE.user.name || 'User')}" class="w-10 h-10 rounded-full border border-gray-200 dark:border-white/10">
            </div>
        `;
    } else {
        container.innerHTML = `
            <button onclick="openAuthModal()" class="px-5 py-2.5 bg-gray-900 dark:bg-white text-white dark:text-black font-semibold rounded-full hover:opacity-90 transition shadow-lg shadow-primary/10">
                Sign In
            </button>
        `;
    }
}

// --- Cart Actions ---

function addToCart(productId) {
    const product = STATE.products.find(p => p.id === productId);
    if (!product) return;

    // Check if exists
    const existing = STATE.cart.find(i => i.product_id === productId);
    if (existing) {
        existing.quantity += 1;
    } else {
        STATE.cart.push({ product_id: product.id, quantity: 1, name: product.name, price: product.price });
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
    const count = STATE.cart.reduce((acc, item) => acc + item.quantity, 0);
    const badge = document.getElementById('cart-count');
    badge.innerText = count;
    badge.classList.toggle('hidden', count === 0);
}

function saveCart() {
    localStorage.setItem('nekwasar_cart', JSON.stringify(STATE.cart));
    updateCartCount();
}

// --- Checkout ---

async function checkout() {
    if (STATE.cart.length === 0) return alert("Cart is empty");

    // Call Checkout API
    try {
        const res = await fetch(`${API_BASE}/checkout/intent`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(STATE.cart)
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
