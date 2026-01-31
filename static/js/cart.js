/**
 * Cart Management - Maison Écorce
 * Session-based cart with API integration
 */

// Initialize cart count on page load
document.addEventListener('DOMContentLoaded', function () {
    initCartCount();
});

/**
 * Fetch cart and update count in header
 */
async function initCartCount() {
    try {
        const response = await fetch('/api/cart');
        const cart = await response.json();
        const count = cart.reduce((sum, item) => sum + item.quantity, 0);
        updateCartCount(count);
    } catch (error) {
        console.error('Failed to load cart:', error);
    }
}

/**
 * Update cart count badge in header
 */
function updateCartCount(count) {
    const badge = document.getElementById('cartCount');
    if (badge) {
        badge.textContent = count;
        badge.dataset.count = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

/**
 * Add item to cart
 */
async function addToCart(product) {
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: product.id,
                name: product.name,
                price: product.price,
                image: product.cloudinary_url,
                quantity: 1
            })
        });

        const data = await response.json();
        const count = data.cart.reduce((sum, item) => sum + item.quantity, 0);
        updateCartCount(count);
        showToast(`${product.name} added to cart`, 'success');

        return data;
    } catch (error) {
        showToast('Failed to add item to cart', 'error');
        throw error;
    }
}

/**
 * Update item quantity in cart
 */
async function updateCartItem(id, quantity) {
    try {
        const response = await fetch('/api/cart/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, quantity })
        });

        const data = await response.json();
        const count = data.cart.reduce((sum, item) => sum + item.quantity, 0);
        updateCartCount(count);

        return data;
    } catch (error) {
        showToast('Failed to update cart', 'error');
        throw error;
    }
}

/**
 * Remove item from cart
 */
async function removeFromCart(id) {
    try {
        const response = await fetch('/api/cart/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });

        const data = await response.json();
        const count = data.cart.reduce((sum, item) => sum + item.quantity, 0);
        updateCartCount(count);

        return data;
    } catch (error) {
        showToast('Failed to remove item', 'error');
        throw error;
    }
}

/**
 * Clear entire cart
 */
async function clearCart() {
    try {
        const response = await fetch('/api/cart/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();
        updateCartCount(0);

        return data;
    } catch (error) {
        showToast('Failed to clear cart', 'error');
        throw error;
    }
}

/**
 * Get current cart
 */
async function getCart() {
    try {
        const response = await fetch('/api/cart');
        return await response.json();
    } catch (error) {
        console.error('Failed to get cart:', error);
        return [];
    }
}

/**
 * Calculate cart total
 */
function calculateCartTotal(cart) {
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const shipping = subtotal > 50000 ? 0 : 3000;
    return {
        subtotal,
        shipping,
        total: subtotal + shipping
    };
}
