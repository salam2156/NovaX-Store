// ==========================
// Nova-Store shared front-end
// Cart helpers, toast notifications, shop search and checkout flow.
// These constants MUST stay in sync with the business rules in app1.py.
// ==========================

const MAX_QUANTITY_PER_ITEM = 99;  // mirrors app1.py MAX_QUANTITY_PER_ITEM
const SHIPPING_FEE = 15.00;        // mirrors app1.py SHIPPING_FEE

// ==========================
// Toast notifications (replaces blocking alert() popups)
// ==========================

let toastStylesInjected = false;

function injectToastStyles() {
    if (toastStylesInjected) return;
    toastStylesInjected = true;
    const style = document.createElement('style');
    style.textContent = `
        #toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: min(360px, calc(100vw - 40px));
        }
        .toast-item {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 12px 14px;
            border-radius: 10px;
            font-size: 0.9rem;
            line-height: 1.45;
            color: #f1f5f9;
            background: #1e293b;
            border: 1px solid #334155;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
            opacity: 0;
            transform: translateY(-8px);
            animation: toast-in 0.25s ease forwards;
            cursor: pointer;
        }
        .toast-item.success { border-left: 4px solid #22c55e; }
        .toast-item.error { border-left: 4px solid #ef4444; }
        .toast-item.info { border-left: 4px solid #38bdf8; }
        .toast-icon { flex-shrink: 0; margin-top: 1px; }
        @keyframes toast-in {
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);
}

const TOAST_ICONS = { success: '\\u2713', error: '\\u26a0', info: '\\u24d8' };

function showToast(message, type) {
    type = (type === 'error' || type === 'info') ? type : 'success';
    injectToastStyles();

    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.setAttribute('aria-live', 'polite');
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-item ' + type;
    toast.setAttribute('role', 'status');
    toast.innerHTML =
        '<span class="toast-icon" aria-hidden="true">' + TOAST_ICONS[type] + '</span>' +
        '<span>' + escapeHtml(message) + '</span>';
    toast.title = 'Click to dismiss';
    toast.addEventListener('click', function () {
        toast.remove();
    });
    container.appendChild(toast);

    // Auto-dismiss after 4.5s so the toast never blocks the page.
    window.setTimeout(function () {
        if (toast.parentNode) toast.remove();
    }, 4500);
}

// ==========================
// Shared cart helpers
// ==========================

function getCart() {
    try {
        if (!sessionStorage.getItem('techstore_cart')) {
            const legacy = localStorage.getItem('techstore_cart');
            if (legacy) sessionStorage.setItem('techstore_cart', legacy);
            localStorage.removeItem('techstore_cart');
        }
    } catch (e) {
    }
    try {
        const cart = JSON.parse(sessionStorage.getItem('techstore_cart'));
        return Array.isArray(cart) ? cart : [];
    } catch (e) {
        return [];
    }
}

function saveCart(cart) {
    try {
        sessionStorage.setItem('techstore_cart', JSON.stringify(cart));
    } catch (e) {
    }
}

function cartQuantity(cart) {
    return cart.reduce(function (sum, item) {
        const qty = parseInt(item.quantity, 10);
        return sum + (qty > 0 ? qty : 0);
    }, 0);
}

function updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        cartCount.textContent = cartQuantity(getCart());
    }
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (ch) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
    });
}

// Safely wipe the cart from both storage layers and refresh the badge.
function clearCartStorage() {
    try { localStorage.removeItem('techstore_cart'); } catch (e) { }
    try { sessionStorage.removeItem('techstore_cart'); } catch (e) { }
    updateCartCount();
}

// Keep the badge in sync across open tabs.
window.addEventListener('storage', function (event) {
    if (event.key === 'techstore_cart' || event.key === null) {
        updateCartCount();
    }
});

// A fresh cart starts whenever the user logs out.
document.addEventListener('click', function (event) {
    const link = event.target.closest('a[href$="/logout"]');
    if (link) clearCartStorage();
});

document.addEventListener('DOMContentLoaded', function () {
    updateCartCount();
    renderCheckout();

    // Post-checkout landing: clear the stored cart, refresh the badge and
    // replace the ?order_placed URL so refresh/back never re-triggers it.
    const params = new URLSearchParams(window.location.search);
    if (params.get('order_placed')) {
        const orderId = params.get('order_id');
        clearCartStorage();
        history.replaceState({}, '', window.location.pathname);
        showToast(orderId
            ? 'Order #' + orderId + ' placed successfully!'
            : 'Your order was placed successfully!');
    }
});

// ==========================
// Account: toggle login / register
// ==========================

function toggleForms() {
    const loginSection = document.getElementById('login-section');
    const registerSection = document.getElementById('register-section');
    if (loginSection && registerSection) {
        loginSection.classList.toggle('hidden');
        registerSection.classList.toggle('hidden');
    }
}

// ==========================
// shop.html: add to cart + search filter
// ==========================

function addToCart(trigger) {
    // Prices come from the server-rendered data attributes (DB prices), so a
    // stale or manually edited product card can never push a wrong price
    // into the cart. The server re-validates at checkout anyway.
    const card = trigger.closest('.product-card');
    if (!card) return;
    const title = (card.getAttribute('data-name') || '').trim();
    const price = parseFloat(card.getAttribute('data-price'));
    if (!title || !(price > 0)) return;

    const cart = getCart();
    const existingItem = cart.find(function (item) { return item.title === title; });

    if (existingItem) {
        if (existingItem.quantity >= MAX_QUANTITY_PER_ITEM) {
            showToast('You can add at most ' + MAX_QUANTITY_PER_ITEM + ' of this item.', 'error');
            return;
        }
        existingItem.quantity = Number(existingItem.quantity) + 1;
        existingItem.price = price; // keep in sync with the catalogue
    } else {
        cart.push({ title: title, price: price, quantity: 1 });
    }

    saveCart(cart);
    updateCartCount();
    showToast(title + ' has been added to cart!');
}

function filterProducts() {
    const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
    let anyVisible = false;
    let visibleCount = 0;
    let totalCount = 0;

    document.querySelectorAll('.category-section').forEach(function (section) {
        let visibleInSection = 0;
        section.querySelectorAll('.product-card').forEach(function (card) {
            totalCount += 1;
            const text = (card.getAttribute('data-search') || '').toLowerCase();
            const matches = text.indexOf(query) !== -1;
            card.style.display = matches ? '' : 'none';
            if (matches) visibleInSection += 1;
        });
        section.style.display = visibleInSection > 0 ? '' : 'none';
        if (visibleInSection > 0) anyVisible = true;
        visibleCount += visibleInSection;
    });

    const emptyState = document.getElementById('search-empty');
    if (emptyState) {
        emptyState.classList.toggle('hidden', !query || anyVisible);
    }

    // Optional result counter (rendered on the shop page).
    const counter = document.getElementById('search-result-count');
    if (counter) {
        if (query && anyVisible) {
            counter.textContent = visibleCount + ' of ' + totalCount + ' products match your search';
            counter.classList.remove('hidden');
        } else {
            counter.classList.add('hidden');
        }
    }
}

// ==========================
// checkout.html: order summary + submit
// ==========================

function renderCheckout() {
    const cart = getCart();
    const container = document.getElementById('checkoutItemsList');

    let subtotal = 0;
    if (container) {
        if (cart.length === 0) {
            container.innerHTML =
                '<p style="color: #94a3b8; text-align: center; padding: 20px 0;">' +
                'Your cart is empty.</p>';
        } else {
            container.innerHTML = '';
            cart.forEach(function (item, index) {
                const price = parseFloat(item.price) || 0;
                const quantity = parseInt(item.quantity, 10) || 1;
                subtotal += price * quantity;

                const itemEl = document.createElement('div');
                itemEl.className = 'order-item';
                itemEl.style.cssText =
                    'display: flex; justify-content: space-between; align-items: center; ' +
                    'padding: 12px 0; border-bottom: 1px solid #1e293b;';
                itemEl.innerHTML =
                    '<div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">' +
                    '<div class="order-item-info">' +
                    '<strong style="color: #fff; font-size: 0.95rem;">' + escapeHtml(item.title) + '</strong>' +
                    '<span style="display: block; color: #94a3b8; font-size: 0.8rem; margin-top: 3px;">' +
                    '$' + price.toFixed(2) + ' each (x' + quantity + ')</span>' +
                    '</div>' +
                    '<div style="display: flex; align-items: center; gap: 8px;">' +
                    '<button type="button" onclick="changeQty(' + index + ', -1)" ' +
                    'style="background: #1e293b; color: #fff; border: none; width: 26px; height: 26px; ' +
                    'border-radius: 6px; cursor: pointer; font-weight: bold;">-</button>' +
                    '<span style="color: #fff; font-weight: 600; min-width: 20px; text-align: center;">' + quantity + '</span>' +
                    '<button type="button" onclick="changeQty(' + index + ', 1)" ' +
                    'style="background: #1e293b; color: #fff; border: none; width: 26px; height: 26px; ' +
                    'border-radius: 6px; cursor: pointer; font-weight: bold;">+</button>' +
                    '<button type="button" onclick="removeItem(' + index + ')" ' +
                    'style="background: #ef4444; color: #fff; border: none; padding: 4px 10px; ' +
                    'border-radius: 6px; cursor: pointer; font-size: 0.75rem; margin-left: 6px;">Delete</button>' +
                    '</div>' +
                    '</div>';

                container.appendChild(itemEl);
            });
        }
    }

    const shipping = subtotal > 0 ? SHIPPING_FEE : 0;
    const total = subtotal + shipping;

    const subtotalEl = document.getElementById('checkout-subtotal');
    if (subtotalEl) subtotalEl.textContent = '$' + subtotal.toFixed(2);
    const shippingEl = document.getElementById('checkout-shipping');
    if (shippingEl) shippingEl.textContent = '$' + shipping.toFixed(2);
    const totalEl = document.getElementById('checkout-total');
    if (totalEl) totalEl.textContent = '$' + total.toFixed(2);

    const totalInput = document.getElementById('total_amount');
    if (totalInput) totalInput.value = total.toFixed(2);
    const cartInput = document.getElementById('cart_data');
    if (cartInput) cartInput.value = JSON.stringify(cart);

    // Disable both "Place Order" buttons while the cart is empty so a click
    // can't silently do nothing (and toasts explain why it's disabled).
    document.querySelectorAll('.btn-checkout').forEach(function (button) {
        button.disabled = cart.length === 0;
    });

    updateCartCount();
}

function changeQty(index, delta) {
    const cart = getCart();
    if (!cart[index]) return;

    const current = parseInt(cart[index].quantity, 10) || 1;
    const next = current + delta;

    if (next > MAX_QUANTITY_PER_ITEM) {
        showToast('You can add at most ' + MAX_QUANTITY_PER_ITEM + ' of this item.', 'error');
        return;
    }
    if (next <= 0) {
        cart.splice(index, 1);
    } else {
        cart[index].quantity = next;
    }
    saveCart(cart);
    renderCheckout();
}

function removeItem(index) {
    const cart = getCart();
    if (cart[index]) {
        cart.splice(index, 1);
        saveCart(cart);
        renderCheckout();
    }
}

// ==========================
// Checkout submission guard (UI layer).
// The first click submits; any follow-up click is ignored. The server has its
// own fingerprint-based dedupe, so this is UX protection, not the security
// boundary.
// ==========================

let orderSubmitted = false;

function processOrder(event) {
    event.preventDefault();
    const cart = getCart();

    if (cart.length === 0) {
        showToast('Your cart is empty. Add some products before placing your order.', 'error');
        return;
    }
    if (orderSubmitted) {
        showToast('Your order is already being processed, please wait...', 'info');
        return;
    }

    orderSubmitted = true;
    document.querySelectorAll('.btn-checkout').forEach(function (button) {
        button.disabled = true;
    });
    showToast('Placing your order...', 'info');

    // Submit programmatically (native .submit() bypasses the onsubmit
    // handler, preventing recursion; the browser then still performs HTML5
    // validation via the requestSubmit() path used by the second button).
    event.target.submit();
}