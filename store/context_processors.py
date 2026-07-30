from .models import SiteSettings, Category, Cart, Wishlist, PolicyPage


def site_settings(request):
    settings = SiteSettings.objects.first()

    return {
        "site_settings": settings,
        "categories": Category.objects.all(),
        "footer_policies": PolicyPage.objects.filter(
            show_in_policy_footer=True
        ).order_by("footer_order", "title"),
    }


def global_data(request):

    wishlist_items = Wishlist.objects.none()
    wishlist_product_ids = []

    cart_items = Cart.objects.none()
    cart_count = 0
    total = 0

    if request.user.is_authenticated:

        wishlist_items = Wishlist.objects.filter(
            user=request.user
        )

        wishlist_product_ids = list(
            wishlist_items.values_list(
                "product_id",
                flat=True
            )
        )

        cart_items = Cart.objects.filter(
            user=request.user
        ).select_related("product", "variant", "variant__colour")

        cart_count = sum(
            item.quantity
            for item in cart_items
        )

        total = sum(
            item.product.price * item.quantity
            for item in cart_items
        )

    return {

        # Site
        "wishlist_items": wishlist_items,
        "wishlist_product_ids": wishlist_product_ids,
        "wishlist_count": len(wishlist_product_ids),

        # Cart
        "cart_items": cart_items,
        "cart_count": cart_count,
        "total": total,
    }