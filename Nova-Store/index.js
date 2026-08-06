  // JavaScript to toggle between login and register forms account.html

        function toggleForms() {
            const loginSection = document.getElementById('login-section');
            const registerSection = document.getElementById('register-section');
            
            loginSection.classList.toggle('hidden');
            registerSection.classList.toggle('hidden');
        }

        function updateCartCount() {
            let cart = JSON.parse(localStorage.getItem('techstore_cart')) || [];
            const cartCount = document.getElementById('cart-count');
            if(cartCount) {
                cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
            }
        }
        document.addEventListener('DOMContentLoaded', updateCartCount);
// javascript to handle cart functionality in index.html
        function updateCartCount() {
            let cart = JSON.parse(localStorage.getItem('techstore_cart')) || [];
            const cartCount = document.getElementById('cart-count');
            if(cartCount) {
                cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
            }
        }
        document.addEventListener('DOMContentLoaded', updateCartCount);
// JavaScript to handle cart functionality in shop.html
function addToCart(title, price) {
    let cart = [];
    try {
        cart = JSON.parse(localStorage.getItem('techstore_cart')) || [];
        if (!Array.isArray(cart)) cart = [];
    } catch (e) {
        cart = [];
    }
    
    let cleanPrice = typeof price === 'string' ? price.replace('$', '') : price;
    let existingItem = cart.find(item => item.title === title);
    
    if (existingItem) {
        existingItem.quantity = (Number(existingItem.quantity) || 1) + 1;
    } else {
        cart.push({ title: title, price: cleanPrice, quantity: 1 });
    }
    
    localStorage.setItem('techstore_cart', JSON.stringify(cart));
    updateCartCount();
    alert(title + " has been added to cart!");
}
//javascript to handle cart functionality in checkout.html

    
    function renderCheckout() {
        let rawData = localStorage.getItem('techstore_cart');
        let cart = [];
        
        try {
            cart = rawData ? JSON.parse(rawData) : [];
            if (!Array.isArray(cart)) cart = [];
        } catch (e) {
            cart = [];
        }

        let container = document.getElementById('checkoutItemsList');
        let subtotalEl = document.getElementById('checkout-subtotal');
        let totalEl = document.getElementById('checkout-total');
        
        let subtotal = 0;
        
        if (container) {
            if (cart.length === 0) {
                container.innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 20px 0;">Your cart is empty.</p>';
            } else {
                container.innerHTML = '';
                cart.forEach((item, index) => {
                    let price = parseFloat(item.price) || 0;
                    let quantity = parseInt(item.quantity) || 1;
                    subtotal += price * quantity;

                    let itemEl = document.createElement('div');
                    itemEl.className = 'order-item';
                    itemEl.style.cssText = "display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #1e293b;";
                    itemEl.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                            <div class="order-item-info">
                                <strong style="color: #fff; font-size: 0.95rem;">${item.title}</strong>
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

        let shipping = subtotal > 0 ? 15.00 : 0.00;
        let total = subtotal + shipping;

        if (subtotalEl) subtotalEl.textContent = "$" + subtotal.toFixed(2);
        if (totalEl) totalEl.textContent = "$" + total.toFixed(2);
        
        let cartCount = document.getElementById('cart-count');
        if (cartCount) {
            cartCount.textContent = cart.reduce((sum, item) => sum + (Number(item.quantity) || 1), 0);
        }
    }

    function changeQty(index, delta) {
        let cart = JSON.parse(localStorage.getItem('techstore_cart')) || [];
        if (cart[index]) {
            cart[index].quantity = (Number(cart[index].quantity) || 1) + delta;
            if (cart[index].quantity <= 0) {
                cart.splice(index, 1);
            }
            localStorage.setItem('techstore_cart', JSON.stringify(cart));
            renderCheckout();
        }
    }

    function removeItem(index) {
        let cart = JSON.parse(localStorage.getItem('techstore_cart')) || [];
        cart.splice(index, 1);
        localStorage.setItem('techstore_cart', JSON.stringify(cart));
        renderCheckout();
    }
    function processOrder(event) {
        if (event) event.preventDefault();
        let cart = JSON.parse(localStorage.getItem('techstore_cart')) || [];
        if (cart.length === 0) {
            alert("Your cart is empty!");
            return;
        }
        alert("Order placed successfully! Thank you for shopping with TechStore.");
        localStorage.removeItem('techstore_cart');
        window.location.href = 'index.html';
    }

    function submitOrder() {
        processOrder();
    }

    document.addEventListener('DOMContentLoaded', renderCheckout);
    // javascript to handle contact form submission in contact.html
   
        function updateCartCount() {
            let cart = JSON.parse(localStorage.getItem('techstore_cart')) || [];
            const cartCount = document.getElementById('cart-count');
            if(cartCount) {
                cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
            }
        }
        
        document.addEventListener('DOMContentLoaded', updateCartCount);

        function handleContact(event) {
            event.preventDefault();
            
            const alertBox = document.getElementById('successAlert');
            alertBox.style.display = 'block';

            document.getElementById('contactForm').reset();


            setTimeout(() => {
                alertBox.style.display = 'none';
            }, 4000);
        }
  
