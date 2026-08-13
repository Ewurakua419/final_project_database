// 1. Inject Cart HTML
const cartHtml = `
  <div id="cart-overlay" class="cart-overlay"></div>
  <div id="cart-drawer" class="cart-drawer">
    <div class="cart-header">
      <h2 class="cart-title">Your Cart</h2>
      <button id="close-cart-btn" class="close-cart" aria-label="Close cart">&times;</button>
    </div>
    <div id="cart-items-container" class="cart-body">
      <div class="loading-state">Loading cart...</div>
    </div>
    <div class="cart-footer">
      <div class="cart-total-row">
        <span class="cart-total-label">Subtotal</span>
        <span id="cart-total-value" class="cart-total-value">$0.00</span>
      </div>
      <button id="checkout-btn" class="button-primary checkout-btn">Proceed to Checkout</button>
    </div>
  </div>
`;
document.body.insertAdjacentHTML('beforeend', cartHtml);

// 2. Setup Elements
const cartOverlay = document.getElementById("cart-overlay");
const cartDrawer = document.getElementById("cart-drawer");
const openCartBtn = document.getElementById("open-cart-btn"); // Must exist in nav
const closeCartBtn = document.getElementById("close-cart-btn");
const cartItemsContainer = document.getElementById("cart-items-container");
const cartTotalValue = document.getElementById("cart-total-value");
const cartCountBadge = document.getElementById("cart-count"); // Must exist in nav
const checkoutBtn = document.getElementById("checkout-btn");

// Helper guest cart storage functions
function getGuestCart() {
  try {
    return JSON.parse(localStorage.getItem("guestCart")) || [];
  } catch (e) {
    return [];
  }
}

function saveGuestCart(cart) {
  localStorage.setItem("guestCart", JSON.stringify(cart));
}

// 3. Define Functions
export const openCart = () => {
  cartOverlay.classList.add("active");
  setTimeout(() => cartDrawer.classList.add("open"), 10);
  fetchCart();
};

export const closeCart = () => {
  cartDrawer.classList.remove("open");
  setTimeout(() => cartOverlay.classList.remove("active"), 300);
};

// 4. Attach Events
if (openCartBtn) {
  openCartBtn.addEventListener("click", (e) => {
    e.preventDefault();
    openCart();
  });
}

closeCartBtn.addEventListener("click", closeCart);
cartOverlay.addEventListener("click", closeCart);

if (checkoutBtn) {
  checkoutBtn.addEventListener("click", (e) => {
    e.preventDefault();
    if (!localStorage.getItem("authToken")) {
      // Redirect to login page with query param
      window.location.href = "../login.html?redirect=checkout";
    } else {
      window.location.href = "../g-checkout/checkout.html";
    }
  });
}

// Render UI function to avoid duplication
function renderCartUI(data) {
  const dynamicCartBadge = document.getElementById("cart-count");
  if (dynamicCartBadge) dynamicCartBadge.innerText = data.total_items;
  cartTotalValue.innerText = "$" + (data.total_price / 100).toFixed(2);
  
  if (data.cart.length === 0) {
    cartItemsContainer.innerHTML = '<div class="loading-state" style="margin: auto;">Your cart is empty.</div>';
    return;
  }

  cartItemsContainer.innerHTML = "";
  data.cart.forEach(item => {
    const product = item.product;
    const price = (product.priceCents / 100).toFixed(2);
    
    const itemDiv = document.createElement("div");
    itemDiv.className = "cart-item";
    itemDiv.innerHTML = `
      <img src="${product.image}" alt="${product.name}" class="cart-item-image">
      <div class="cart-item-details">
        <h4 class="cart-item-title">${product.name}</h4>
        <div class="cart-item-price">$${price}</div>
        <div class="cart-item-qty">Qty: ${item.quantity}</div>
        <div class="cart-item-actions">
          <button class="cart-action-btn" data-action="increase" data-id="${product.id}" data-qty="${item.quantity}" aria-label="Increase quantity">➕</button>
          <button class="cart-action-btn" data-action="decrease" data-id="${product.id}" data-qty="${item.quantity}" aria-label="Decrease quantity">➖</button>
          <button class="cart-action-btn delete-btn" data-action="remove" data-id="${product.id}" aria-label="Remove item">🗑️</button>
        </div>
      </div>
    `;
    cartItemsContainer.appendChild(itemDiv);
  });
}

// Cart API calls and Actions
cartItemsContainer.addEventListener("click", (e) => {
  const btn = e.target.closest(".cart-action-btn");
  if (!btn) return;
  
  const action = btn.getAttribute("data-action");
  const prodId = btn.getAttribute("data-id");
  const currentQty = parseInt(btn.getAttribute("data-qty"), 10);
  
  btn.style.opacity = "0.5";
  btn.style.pointerEvents = "none";

  if (!localStorage.getItem("authToken")) {
    const guestCart = getGuestCart();
    if (action === "remove") {
      const idx = guestCart.findIndex(item => item.product_id === prodId);
      if (idx > -1) guestCart.splice(idx, 1);
    } else if (action === "increase" || action === "decrease") {
      const item = guestCart.find(item => item.product_id === prodId);
      if (item) {
        if (action === "increase") item.quantity += 1;
        if (action === "decrease") item.quantity -= 1;
        if (item.quantity <= 0) {
          const idx = guestCart.indexOf(item);
          guestCart.splice(idx, 1);
        }
      }
    }
    saveGuestCart(guestCart);
    fetchCart();
    return;
  }

  if (action === "remove") {
    fetch(`http://127.0.0.1:5001/cart/${prodId}`, { 
      method: "DELETE",
      headers: {
        "Authorization": "Bearer " + localStorage.getItem("authToken")
      }
    })
      .then(res => res.json())
      .then(() => fetchCart())
      .catch(err => console.error(err));
  } else if (action === "increase" || action === "decrease") {
    let newQty = currentQty;
    if (action === "increase") newQty += 1;
    if (action === "decrease") newQty -= 1;
    
    fetch(`http://127.0.0.1:5001/cart/${prodId}/quantity`, {
      method: "PUT",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": "Bearer " + localStorage.getItem("authToken")
      },
      body: JSON.stringify({ quantity: newQty })
    })
    .then(res => res.json())
    .then(() => fetchCart())
    .catch(err => console.error(err));
  }
});

export const addToCart = (prod_id, quantity) => {
  if (!localStorage.getItem("authToken")) {
    const guestCart = getGuestCart();
    const existing = guestCart.find(item => item.product_id === prod_id);
    if (existing) {
      existing.quantity += quantity;
    } else {
      guestCart.push({ product_id: prod_id, quantity: quantity });
    }
    saveGuestCart(guestCart);
    fetchCart();
    return Promise.resolve({ message: "Added to guest cart successfully" });
  }

  return fetch("http://127.0.0.1:5001/cart", {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "Authorization": "Bearer " + localStorage.getItem("authToken")
    },
    body: JSON.stringify({ product_id: prod_id, quantity: quantity })
  }).then(res => res.json());
};

export const fetchCart = () => {
  if (!localStorage.getItem("authToken")) {
    const guestCart = getGuestCart();
    if (guestCart.length === 0) {
      renderCartUI({ cart: [], total_items: 0, total_price: 0 });
      return;
    }

    fetch("http://127.0.0.1:5001/product-items")
      .then(res => res.json())
      .then(data => {
        const productsMap = {};
        (data.products || []).forEach(p => {
          productsMap[p.id] = p;
        });

        let total_items = 0;
        let total_price = 0;
        const cartList = [];

        guestCart.forEach(item => {
          const product = productsMap[item.product_id];
          if (product) {
            total_items += item.quantity;
            total_price += product.priceCents * item.quantity;
            cartList.push({
              product: product,
              quantity: item.quantity
            });
          }
        });

        renderCartUI({ cart: cartList, total_items, total_price });
      })
      .catch(err => console.error("Failed to load products for guest cart", err));
    return;
  }

  fetch("http://127.0.0.1:5001/cart", {
    headers: {
      "Authorization": "Bearer " + localStorage.getItem("authToken")
    }
  })
    .then(res => res.json())
    .then(data => {
      renderCartUI(data);
    })
    .catch(err => console.error(err));
};

// Initial fetch
fetchCart();
