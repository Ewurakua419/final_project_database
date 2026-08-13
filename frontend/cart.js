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
      <button class="button-primary checkout-btn" onclick="window.location.href='../g-checkout/checkout.html'">Proceed to Checkout</button>
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

  // Cart API calls and Actions
  cartItemsContainer.addEventListener("click", (e) => {
    const btn = e.target.closest(".cart-action-btn");
    if (!btn) return;
    
    const action = btn.getAttribute("data-action");
    const prodId = btn.getAttribute("data-id");
    const currentQty = parseInt(btn.getAttribute("data-qty"), 10);
    
    btn.style.opacity = "0.5";
    btn.style.pointerEvents = "none";

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
    fetch("http://127.0.0.1:5001/cart", {
      headers: {
        "Authorization": "Bearer " + localStorage.getItem("authToken")
      }
    })
      .then(res => res.json())
      .then(data => {
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
      })
      .catch(err => console.error(err));
  };
  
  // Initial fetch
  fetchCart();
