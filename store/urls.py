from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .forms import CustomPasswordChangeForm
urlpatterns = [

    # HOME
    path("", views.home, name="home"),
    path("categories/", views.all_categories, name="all_categories"),

    # PRODUCTS
    path(
        "products/",
        views.product_list,
        name="product_list"
    ),

    path(
        "product/<slug:slug>/",
        views.product_detail,
        name="product_detail"
    ),
    # CATEGORIES
    path(
        "category/<slug:category_slug>/",
        views.category_products,
        name="category_products",
    ),
    path(
        "category/<slug:category_slug>/<slug:sub_slug>/",
        views.category_products,
        name="subcategory_products",
    ),

    # TAGS
    path(
        "tag/<slug:slug>/",
        views.tag_products,
        name="tag_products"
    ),

    # COLLECTION PAGES
    path(
        "trending/",
        views.trending_products,
        name="trending_products"
    ),

    path(
        "best-sellers/",
        views.best_sellers,
        name="best_sellers"
    ),

    path(
        "shop-this-look/",
        views.shop_this_look,
        name="shop_this_look"
    ),

    # SEARCH
    path(
        "search/",
        views.search_products,
        name="search_products"
    ),

    # CART
    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "add-to-cart/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    # WISHLIST
    path(
        "wishlist/",
        views.wishlist,
        name="wishlist"
    ),
    path(
        "wishlist/bulk-action/",
        views.wishlist_bulk_action,
        name="wishlist_bulk_action"
    ),
    path(
        "wishlist/share-link/",
        views.wishlist_get_share_link,
        name="wishlist_get_share_link"
    ),
    path(
        "wishlist/shared/<uuid:token>/",
        views.wishlist_shared,
        name="wishlist_shared"
    ),
    path(
        "remove-wishlist/<int:product_id>/",
        views.remove_wishlist,
        name="remove_wishlist"
    ),
    path(
        "add-to-wishlist/<int:product_id>/",
        views.add_to_wishlist,
        name="add_to_wishlist"
    ),

    # STATIC PAGES
    path(
        "about/",
        views.about,
        name="about"
    ),

    path(
        "contact/",
        views.contact,
        name="contact"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),
    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),
    path(
        "payment/<int:order_id>/",
        views.payment_page,
        name="payment_page"
    ),
    path(
        "size/<int:id>/",
        views.size_products,
        name="size_products"
    ),
    path(
        "product/<slug:slug>/review/",
        views.add_review,
        name="add_review"
    ),
    path(
        "bangle-size-guide/", 
        views.bangle_size_guide, 
        name="bangle_size_guide"
    ),
    path(
        "accessibility/",
        views.accessibility,
        name="accessibility",
    ),
    path(
        "shipping-returns/",
        views.shipping_returns,
        name="shipping_returns"
    ),
    path(
        "register/",
        views.register_view,
        name="register"
    ),
    path(
        "forgot-password/",
        views.forgot_password_view,
        name="forgot_password"
    ),
    path(
        "logout/",
        LogoutView.as_view(next_page="home"),
        name="logout",
    ),
    path(
        "profile/",
        views.profile,
        name="profile"
    ),
    path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="store/change_password.html",
            form_class=CustomPasswordChangeForm,
            success_url="/profile/",
        ),
        name="password_change",
    ),
    path(
        "profile/delete/",
        views.delete_account,
        name="delete_account",
    ),
    path(
        "cart/increase/<int:item_id>/",
        views.increase_cart,
        name="increase_cart",
    ),

    path(
        "cart/decrease/<int:item_id>/",
        views.decrease_cart,
        name="decrease_cart",
    ),

    path(
        "cart/remove/<int:item_id>/",
        views.remove_cart,
        name="remove_cart",
    ),

    path(
        "cart/note/<int:item_id>/",
        views.update_cart_note,
        name="update_cart_note",
    ),
    path(
        "buy-now/<int:product_id>/",
        views.buy_now,
        name="buy_now",
    ),
    path(
        "faq/",
        views.faq,
        name="faq",
    ),

    path(
        "privacy/",
        views.privacy,
        name="privacy",
    ),

    path(
        "terms-and-conditions/",
        views.terms_conditions,
        name="terms_conditions",
    ),

    path(
        "refund-policy/",
        views.refund_policy,
        name="refund_policy",
    ),

    path(
        "support/",
        views.support,
        name="support",
    ),

    path(
        "our-policy/",
        views.policy_index,
        name="policy_index",
    ),

    path(
        "pages/<slug:slug>/",
        views.policy_page,
        name="policy_page",
    ),

    path(
        "newsletter/subscribe/",
        views.subscribe_newsletter,
        name="subscribe_newsletter",
    ),
]




