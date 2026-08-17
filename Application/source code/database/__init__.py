# database package initialization
# Exposes all database API methods for backward compatibility with import database

from database.connection import connect, run_query

from database.customer_repo import (
    searchcustomer,
    searchcustomer_by_id,
    register,
    update_customer,
    searchvendor,
    registervendor,
    add_address,
    get_addresses_by_customer,
    delete_address,
    update_address
)

from database.product_repo import (
    get_all_products,
    findproduct,
    find_fashion_attributes,
    find_beauty_attributes,
    addproduct,
    add_fashion,
    add_beauty,
    updateproduct,
    update_fashion,
    update_beauty,
    deleteproduct,
    get_reviews_by_product,
    add_review
)

from database.order_repo import (
    get_all_orders,
    add_order,
    add_delivery,
    get_delivery_by_order,
    update_order,
    addtocart,
    getcart,
    removefromcart,
    checkout
)

from database.shipping_repo import (
    searchshipping,
    get_all_shipping_companies,
    register_shipping_company,
    get_deliveries_by_shipping_company,
    update_delivery_status,
    update_order_item_status
)

from database.admin_repo import (
    viewtopproducs,
    viewhighestspender,
    highestrevenue_vendors,
    top_popular_products_categories,
    get_admin_stats,
    get_admin_users,
    get_vendor_product_analytics,
    get_vendor_dashboard_stats
)
