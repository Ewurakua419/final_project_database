// navbar.js
import { fetchCart, openCart } from './cart.js';

function initNavbar() {
  const container = document.getElementById("navbar-container");
  if (!container) return;

  const pathParts = window.location.pathname.split('/');
  const frontendIdx = pathParts.indexOf('frontend');
  const depth = frontendIdx !== -1 ? (pathParts.length - 1 - frontendIdx - 1) : (pathParts.length - 2);
  const prefix = depth > 0 ? '../'.repeat(depth) : './';

  const isLoggedIn = !!localStorage.getItem("authToken");
  const authBtn = isLoggedIn 
    ? `<a href="${prefix}login.html" class="button-utility" onclick="localStorage.removeItem('authToken')">Log out</a>` 
    : `<a href="${prefix}login.html" class="button-utility">Log in</a>`;
  const profileLink = isLoggedIn 
    ? `<a href="${prefix}profile.html" class="cart-link">Profile</a>` 
    : '';

  container.innerHTML = `
    <nav class="nav-bar">
      <a href="${prefix}products/products.html" class="logo" style="font-weight: 600; text-decoration: none; color: var(--color-ink); font-size: 1.25rem;">Ecommerce store</a>
      <div class="nav-links">
        ${profileLink}
        ${authBtn}
        <a href="${prefix}orders/orders.html" class="cart-link">
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
