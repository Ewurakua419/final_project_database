// navbar.js
import { fetchCart, openCart } from './cart.js';

function initNavbar() {
  const container = document.getElementById("navbar-container");
  if (!container) return;

  container.innerHTML = `
    <nav class="nav-bar">
      <a href="../products/products.html" class="logo" style="font-weight: 600; text-decoration: none; color: var(--color-ink); font-size: 1.25rem;">Ecommerce store</a>
      <div class="nav-links">
        <a href="../login.html" class="button-utility">Log in</a>
        <a href="../orders/orders.html" class="cart-link">
          Returns & Orders
        </a>
        <a href="#" id="open-cart-btn" class="cart-link" style="margin-left: 12px; font-weight: bold;">
          🛒 Cart <span id="cart-count">0</span>
        </a>
      </div>
    </nav>
  `;

  // Bind cart button events
  const openCartBtn = document.getElementById("open-cart-btn");
  if (openCartBtn) {
    openCartBtn.addEventListener("click", openCart);
  }

  // Update cart count
  fetchCart();
}

initNavbar();
