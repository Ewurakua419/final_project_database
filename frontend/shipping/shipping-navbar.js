document.addEventListener("DOMContentLoaded", () => {
  const navContainer = document.getElementById("shipping-nav-container");
  if (!navContainer) return;

  navContainer.innerHTML = `
    <nav class="nav-bar">
      <a href="dashboard.html" class="nav-brand">Logistics Portal</a>
      <div class="nav-links">
        <span style="font-size: var(--type-body-sm-size); color: var(--color-ink-muted); margin-right: var(--spacing-md);">
          Shipping Partner
        </span>
        <button id="shipping-logout-btn" class="button-utility">Log out</button>
      </div>
    </nav>
  `;

  document.getElementById("shipping-logout-btn").addEventListener("click", () => {
    localStorage.removeItem("shippingAuthToken");
    window.location.href = "login.html";
  });
});
