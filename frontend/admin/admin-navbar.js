document.addEventListener("DOMContentLoaded", () => {
  const navContainer = document.getElementById("admin-nav-container");
  if (!navContainer) return;

  navContainer.innerHTML = `
    <nav class="nav-bar">
      <a href="dashboard.html" class="nav-brand">Platform Admin</a>
      <div class="nav-links">
        <span style="font-size: var(--type-body-sm-size); color: var(--color-ink-muted); margin-right: var(--spacing-md);">
          Superuser
        </span>
        <button id="admin-logout-btn" class="button-utility">Log out</button>
      </div>
    </nav>
  `;

  document.getElementById("admin-logout-btn").addEventListener("click", () => {
    localStorage.removeItem("adminAuthToken");
    window.location.href = "login.html";
  });
});
