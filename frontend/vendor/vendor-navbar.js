export function initVendorSidebar() {
  const container = document.getElementById("vendor-nav-container");
  if (!container) return;

  // Determine active page
  const path = window.location.pathname;
  const isDashboard = path.includes("dashboard.html");
  const isProducts = path.includes("products.html") || path.includes("add_product.html");
  const isOrders = path.includes("orders.html");

  container.innerHTML = `
    <nav class="nav-bar">
      <a href="dashboard.html" class="logo" style="font-weight: 700; text-decoration: none; color: var(--color-ink); font-size: 1.25rem; letter-spacing: -0.5px;">
        <span class="sticker-dot bg-sticker-teal" style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; vertical-align: middle;"></span>
        Vendor Portal
      </a>
      <div class="nav-links" style="display: flex; gap: var(--spacing-lg); align-items: center;">
        <a href="dashboard.html" style="text-decoration: none; color: ${isDashboard ? 'var(--color-primary)' : 'var(--color-ink-secondary)'}; font-weight: ${isDashboard ? '600' : '400'};">Overview</a>
        <a href="products.html" style="text-decoration: none; color: ${isProducts ? 'var(--color-primary)' : 'var(--color-ink-secondary)'}; font-weight: ${isProducts ? '600' : '400'};">Inventory</a>
        <a href="orders.html" style="text-decoration: none; color: ${isOrders ? 'var(--color-primary)' : 'var(--color-ink-secondary)'}; font-weight: ${isOrders ? '600' : '400'};">Orders</a>
        <a href="login.html" class="button-utility" onclick="sessionStorage.removeItem('vendor_logged_in')">Log out</a>
      </div>
    </nav>
  `;
}

// Auto-initialize if the container exists
document.addEventListener("DOMContentLoaded", initVendorSidebar);
