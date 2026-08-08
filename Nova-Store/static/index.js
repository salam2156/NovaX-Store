// ==========================
// Shared cart helpers
// ==========================

function getCart() {
    try {
        const cart = JSON.parse(localStorage.getItem('techstore_cart'));
        return Array.isArray(cart) ? cart : [];
    } catch (e) {
        return [];
    }
}

function saveCart(cart) {
    localStorage.setItem('techstore_cart', JSON.stringify(cart));
}

function cartQuantity(cart) {
    return cart.reduce((sum, item) => sum + (Number(item.quantity) || 1), 0);
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

document.addEventListener('DOMContentLoaded', updateCartCount);

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

function addToCart(title, price) {
    const cart = getCart();
    const existingItem = cart.find(item => item.title === title);

    if (existingItem) {
        existingItem.quantity = (Number(existingItem.quantity) || 1) + 1;
    } else {
        cart.push({ title: title, price: Number(price) || 0, quantity: 1 });
    }

    saveCart(cart);
    updateCartCount();
    alert(title + ' has been added to cart!');
}

function filterProducts() {
    const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
    document.querySelectorAll('.product-card').forEach(function (card) {
        const name = (card.getAttribute('data-name') || '').toLowerCase();
        card.style.display = name.includes(query) ? '' : 'none';
    });
}

// ==========================
// checkout.html: order summary + submit
// ==========================

function renderCheckout() {
    const cart = getCart();
    const container = document.getElementById('checkoutItemsList');
    const subtotalEl = document.getElementById('checkout-subtotal');
    const totalEl = document.getElementById('checkout-total');

    let subtotal = 0;

    if (container) {
        if (cart.length === 0) {
            container.innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 20px 0;">Your cart is empty.</p>';
        } else {
            container.innerHTML = '';
            cart.forEach((item, index) => {
                const price = parseFloat(item.price) || 0;
                const quantity = parseInt(item.quantity) || 1;
                subtotal += price * quantity;

                const itemEl = document.createElement('div');
                itemEl.className = 'order-item';
                itemEl.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #1e293b;';
                itemEl.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                        <div class="order-item-info">
                            <strong style="color: #fff; font-size: 0.95rem;">${escapeHtml(item.title)}</strong>
                            <span style="display: block; color: #94a3b8; font-size: 0.8rem; margin-top: 3px;">$${price.toFixed(2)} each</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <button type="button" onclick="changeQty(${index}, -1)" style="background: #1e293b; color: #fff; border: none; width: 26px; height: 26px; border-radius: 6px; cursor: pointer; font-weight: bold;">-</button>
                            <span style="color: #fff; font-weight: 600; min-width: 20px; text-align: center;">${quantity}</span>
                            <button type="button" onclick="changeQty(${index}, 1)" style="background: #1e293b; color: #fff; border: none; width: 26px; height: 26px; border-radius: 6px; cursor: pointer; font-weight: bold;">+</button>
                            <button type="button" onclick="removeItem(${index})" style="background: #ef4444; color: #fff; border: none; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; margin-left: 6px;">Delete</button>
                        </div>
                    </div>
                `;
                container.appendChild(itemEl);
            });
        }
    }

    const shipping = subtotal > 0 ? 15.00 : 0.00;
    const total = subtotal + shipping;

    if (subtotalEl) subtotalEl.textContent = '$' + subtotal.toFixed(2);
    if (totalEl) totalEl.textContent = '$' + total.toFixed(2);

    const totalInput = document.getElementById('total_amount');
    if (totalInput) totalInput.value = total.toFixed(2);
    const cartInput = document.getElementById('cart_data');
    if (cartInput) cartInput.value = JSON.stringify(cart);

    updateCartCount();
}

function changeQty(index, delta) {
    const cart = getCart();
    if (cart[index]) {
        cart[index].quantity = (Number(cart[index].quantity) || 1) + delta;
        if (cart[index].quantity <= 0) {
            cart.splice(index, 1);
        }
        saveCart(cart);
        renderCheckout();
    }
}

function removeItem(index) {
    const cart = getCart();
    cart.splice(index, 1);
    saveCart(cart);
    renderCheckout();
}

function processOrder(event) {
    if (event) event.preventDefault();

    if (getCart().length === 0) {
        alert('Your cart is empty!');
        return;
    }

    const form = document.getElementById('checkoutForm');
    if (form) {
        localStorage.removeItem('techstore_cart');
        form.submit();
    }
}

function submitOrder() {
    processOrder();
}

document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('checkoutItemsList')) {
        renderCheckout();
    }
});