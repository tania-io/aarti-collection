from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
import json
import uuid
from .models import Product, Category, SubCategory, ProductTag, Banner, Cart, Wishlist, ShopLook, SiteSettings, Order, Review, ReviewImage, SizeOption, CustomerProfile, Colour, NewsletterSubscriber, ProductVariant, PolicyPage
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Products per page: 20 = 4 columns x 5 rows on desktop, 2 columns x 10 rows on mobile
PRODUCTS_PER_PAGE = 20
GIFT_WRAP_FEE = 49
# ==========================
# HOME
def home(request):

    gift_products = Product.objects.filter(
        Q(purpose__icontains="gift") | Q(featured=True)
    ).distinct().select_related("category").prefetch_related("variants__colour")[:4]

    personalized_products = Product.objects.none()

    if request.user.is_authenticated:
        liked_categories = Product.objects.filter(
            Q(wishlist__user=request.user) | Q(cart__user=request.user)
        ).values_list("category_id", flat=True).distinct()

        if liked_categories:
            personalized_products = Product.objects.filter(
                category_id__in=liked_categories,
                in_stock=True
            ).select_related("category").prefetch_related("variants__colour").order_by("?")[:4]

    if not personalized_products:
        personalized_products = Product.objects.filter(
            in_stock=True
        ).select_related("category").prefetch_related("variants__colour").order_by("?")[:4]

    context = {
        "trending_products": Product.objects.filter(is_trending=True).select_related("category").prefetch_related("variants__colour"),
        "best_sellers": Product.objects.filter(is_best_seller=True).select_related("category").prefetch_related("variants__colour")[:15],
        "shop_looks": ShopLook.objects.filter(active=True).prefetch_related("products")[:15],
        "banners": Banner.objects.filter(active=True),
        "categories": Category.objects.filter(show_on_home=True),
        "gift_products": gift_products,
        "personalized_products": personalized_products,
    }
    return render(request, "store/home.html", context)


def all_categories(request):
    return render(
        request,
        "store/all_categories.html",
        {"categories": Category.objects.all()},
    )


# ALL PRODUCTS
def product_list(request):

    products = Product.objects.all().distinct().select_related("category").prefetch_related("variants__colour")

    # =====================================
    # SPECIAL COLLECTIONS
    # =====================================

    filter_type = request.GET.get("filter")

    if filter_type == "trending":
        products = products.filter(is_trending=True)

    elif filter_type == "best-sellers":
        products = products.filter(is_best_seller=True)

    elif filter_type == "gifts":
        products = products.filter(
            Q(purpose__icontains="gift") | Q(featured=True)
        ).distinct()

    elif filter_type == "recommended":
        products = products.filter(
            Q(is_best_seller=True) | Q(is_trending=True) | Q(featured=True)
        ).distinct()

    # =====================================
    # SEARCH
    # =====================================

    query = request.GET.get("q", "")

    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(material__icontains=query) |
            Q(purpose__icontains=query) |
            Q(variants__colour__name__icontains=query)
        ).distinct()

    # =====================================
    # COLOUR
    # =====================================

    colours_selected = request.GET.getlist("colour")

    if colours_selected:
        products = products.filter(
            variants__colour__slug__in=colours_selected
        )

    # =====================================
    # SIZE
    # =====================================

    sizes_selected = request.GET.getlist("size")

    if sizes_selected:
        products = products.filter(
            sizes__id__in=sizes_selected
        )

    # =====================================
    # MATERIAL
    # =====================================

    materials_selected = request.GET.getlist("material")

    if materials_selected:
        products = products.filter(
            material__in=materials_selected
        )

    # =====================================
    # PURPOSE
    # =====================================

    purposes_selected = request.GET.getlist("purpose")

    if purposes_selected:
        products = products.filter(
            purpose__in=purposes_selected
        )

    # =====================================
    # CATEGORY
    # =====================================

    categories_selected = request.GET.getlist("category")

    if categories_selected:
        products = products.filter(
            category__slug__in=categories_selected
        )

    # =====================================
    # AVAILABILITY
    # =====================================

    availability_selected = request.GET.getlist("availability")

    if availability_selected:
        q = Q()
        if "in_stock" in availability_selected:
            q |= Q(in_stock=True)
        if "out_of_stock" in availability_selected:
            q |= Q(in_stock=False)
        products = products.filter(q)

    # =====================================
    # TAGS
    # =====================================

    tags_selected = request.GET.getlist("tag")

    if tags_selected:
        products = products.filter(
            tags__slug__in=tags_selected
        ).distinct()

    # =====================================
# PRICE RANGE
# =====================================

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # =====================================
    # SORT
    # =====================================

    sort = request.GET.get("sort", "featured")

    if sort == "price_low":
        products = products.order_by("price")

    elif sort == "price_high":
        products = products.order_by("-price")

    elif sort == "newest":
        products = products.order_by("-created_at")

    elif sort == "name":
        products = products.order_by("title")

    elif sort == "best_seller":
        products = products.order_by("-is_best_seller", "-created_at")

    else:
        # "featured" (default): featured products first, then newest
        sort = "featured"
        products = products.order_by("-featured", "-created_at")

    # =====================================
    # FILTER OPTIONS
    # =====================================

    colours = Colour.objects.all()

    sizes = SizeOption.objects.all()

    materials = (
        Product.objects
        .exclude(material="")
        .values_list("material", flat=True)
        .distinct()
    )

    purposes = (
        Product.objects
        .exclude(purpose="")
        .values_list("purpose", flat=True)
        .distinct()
    )

    all_categories = Category.objects.all()

    all_tags = ProductTag.objects.all()

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    querystring = request.GET.copy()
    querystring.pop("page", None)
    querystring = querystring.urlencode()

    clear_url = reverse("product_list")
    if query:
        clear_url += f"?q={query}"
    elif filter_type:
        clear_url += f"?filter={filter_type}"

    return render(
        request,
        "store/product_list.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "querystring": querystring,
            "clear_url": clear_url,
            "query": query,
            "filter_type": filter_type,

            "colours": colours,
            "sizes": sizes,
            "materials": materials,
            "purposes": purposes,
            "all_categories": all_categories,
            "all_tags": all_tags,

            "selected_colours": colours_selected,
            "selected_sizes": sizes_selected,
            "selected_materials": materials_selected,
            "selected_purposes": purposes_selected,
            "selected_categories": categories_selected,
            "selected_availability": availability_selected,
            "selected_tags": tags_selected,
            "selected_min_price": min_price,
            "selected_max_price": max_price,
            "selected_sort": sort,
        },
    )
# PRODUCT DETAIL
# ==========================
def product_detail(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug
    )

    # ==========================
    # RECENTLY VIEWED (session-based)
    # ==========================

    viewed = request.session.get("recently_viewed", [])
    viewed = [pid for pid in viewed if pid != product.id]
    viewed.insert(0, product.id)
    request.session["recently_viewed"] = viewed[:12]

    reviews = product.reviews.filter(
        approved=True
    ).prefetch_related("images")

    variants = list(product.variants.filter(active=True))

    gallery_slides = []

    if variants:
        for v_index, variant in enumerate(variants):
            if variant.image:
                gallery_slides.append({
                    "type": "image",
                    "src": variant.image.url,
                    "variant": v_index,
                })
            for extra in variant.images.all():
                gallery_slides.append({
                    "type": "image",
                    "src": extra.image.url,
                    "variant": v_index,
                })
    else:
        if product.image:
            gallery_slides.append({
                "type": "image",
                "src": product.image.url,
                "variant": None,
            })
        if product.image_back:
            gallery_slides.append({
                "type": "image",
                "src": product.image_back.url,
                "variant": None,
            })

    # Unlimited extra gallery images (admin-managed) always show,
    # whether or not the product has colour variants.
    for extra in product.gallery_images.all():
        gallery_slides.append({
            "type": "image",
            "src": extra.image.url,
            "variant": None,
        })

    if product.video:
        gallery_slides.append({
            "type": "video",
            "src": product.video.url,
            "variant": None,
        })
    
    related_products = Product.objects.filter(
        category=product.category,
        in_stock=True
    ).exclude(
        id=product.id
    ).order_by("?")[:8]

    same_look_products = Product.objects.filter(
        shop_looks__in=product.shop_looks.all()
    ).exclude(
        id=product.id
    ).distinct()[:8]

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "variants": variants,
            "gallery_slides": gallery_slides,
            "related_products": related_products,
            "same_look_products": same_look_products,
        }
    )
def category_products(request, category_slug, sub_slug=None):

    category = get_object_or_404(
        Category,
        slug=category_slug
    )

    products = Product.objects.filter(
        category=category
    ).distinct().select_related("category").prefetch_related("variants__colour")

    selected_sub = None

    # =====================================
    # SUBCATEGORY
    # =====================================

    if sub_slug:

        selected_sub = get_object_or_404(
            SubCategory,
            slug=sub_slug,
            category=category
        )

        products = products.filter(
            subcategory=selected_sub
        )

    # =====================================
    # COLOUR FILTER (MULTIPLE)
    # =====================================

    colours_selected = request.GET.getlist("colour")

    if colours_selected:

        products = products.filter(
            variants__colour__slug__in=colours_selected
        )

    # =====================================
    # SIZE FILTER (MULTIPLE)
    # =====================================

    sizes_selected = request.GET.getlist("size")

    if sizes_selected:

        products = products.filter(
            sizes__id__in=sizes_selected
        )

    # =====================================
    # MATERIAL FILTER (MULTIPLE)
    # =====================================

    materials_selected = request.GET.getlist("material")

    if materials_selected:

        products = products.filter(
            material__in=materials_selected
        )

    # =====================================
    # PURPOSE FILTER (MULTIPLE)
    # =====================================

    purposes_selected = request.GET.getlist("purpose")

    if purposes_selected:

        products = products.filter(
            purpose__in=purposes_selected
        )

    # =====================================
    # AVAILABILITY FILTER
    # =====================================

    availability_selected = request.GET.getlist("availability")

    if availability_selected:
        q = Q()
        if "in_stock" in availability_selected:
            q |= Q(in_stock=True)
        if "out_of_stock" in availability_selected:
            q |= Q(in_stock=False)
        products = products.filter(q)

    # =====================================
    # TAGS FILTER
    # =====================================

    tags_selected = request.GET.getlist("tag")

    if tags_selected:
        products = products.filter(
            tags__slug__in=tags_selected
        ).distinct()

# =====================================
# PRICE FILTER
# =====================================

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        try:
            products = products.filter(
                price__gte=float(min_price)
            )
        except (ValueError, TypeError):
            pass

    if max_price:
        try:
            products = products.filter(
                price__lte=float(max_price)
            )
        except (ValueError, TypeError):
            pass
    # =====================================
    # FILTER OPTIONS
    # =====================================

    colours = Colour.objects.filter(
        variants__product__category=category
    ).distinct()

    sizes = SizeOption.objects.filter(
        product__category=category
    ).distinct()

    materials = (
        Product.objects.filter(category=category)
        .exclude(material="")
        .values_list("material", flat=True)
        .distinct()
    )

    purposes = (
        Product.objects.filter(category=category)
        .exclude(purpose="")
        .values_list("purpose", flat=True)
        .distinct()
    )

    all_tags = ProductTag.objects.filter(
        product__category=category
    ).distinct()
        # ==========================
    # SORTING
    # ==========================

    sort = request.GET.get("sort", "featured")

    if sort == "price_low":
        products = products.order_by("price")

    elif sort == "price_high":
        products = products.order_by("-price")

    elif sort == "newest":
        products = products.order_by("-created_at")

    elif sort == "name":
        products = products.order_by("title")

    elif sort == "best_seller":
        products = products.order_by("-is_best_seller", "-created_at")

    else:
        sort = "featured"
        products = products.order_by("-featured", "-created_at")

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    querystring = request.GET.copy()
    querystring.pop("page", None)
    querystring = querystring.urlencode()

    if selected_sub:
        clear_url = reverse("subcategory_products", args=[category.slug, selected_sub.slug])
    else:
        clear_url = reverse("category_products", args=[category.slug])

    return render(
        request,
        "store/category_products.html",
        {
            "category": category,
            "selected_sub": selected_sub,
            "products": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "querystring": querystring,
            "clear_url": clear_url,

            # Filter Options
            "colours": colours,
            "sizes": sizes,
            "materials": materials,
            "purposes": purposes,
            "all_tags": all_tags,

            # Active Filters
            "selected_colours": colours_selected,
            "selected_sizes": sizes_selected,
            "selected_materials": materials_selected,
            "selected_purposes": purposes_selected,
            "selected_availability": availability_selected,
            "selected_tags": tags_selected,
            "selected_min_price": min_price,
            "selected_max_price": max_price,
            "selected_sort": sort,
        },
    )
# ==========================
# TAG PAGE
# ==========================

def tag_products(request, slug):

    tag = get_object_or_404(
        ProductTag,
        slug=slug
    )

    products = Product.objects.filter(
        tags=tag
    )

    return render(
        request,
        "store/tag_products.html",
        {
            "tag": tag,
            "products": products
        }
    )
# ==========================
# TRENDING PRODUCTS
# ==========================

def trending_products(request):

    products = Product.objects.filter(
        is_trending=True
    )

    return render(
        request,
        "store/trending_products.html",
        {
            "products": products
        }
    )


# ==========================
# BEST SELLERS
# ==========================

def best_sellers(request):

    products = Product.objects.filter(
        is_best_seller=True
    )

    return render(
        request,
        "store/best_sellers.html",
        {
            "products": products
        }
    )


# ==========================
# SHOP THIS LOOK
# ==========================

def shop_this_look(request):

    shop_looks = ShopLook.objects.filter(
        active=True
    )

    return render(
        request,
        "store/shop_this_look.html",
        {
            "shop_looks": shop_looks
        }
    )


# ==========================
# SEARCH
def search_products(request):

    query = request.GET.get("q", "")

    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(variants__colour__name__icontains=query)
    ).distinct()

    return render(
        request,
        "store/product_list.html",
        {
            "products": products,
            "query": query,
        },
    )
# ==========================
# CART
# ==========================

def _cart_queryset(user):
    return (
        Cart.objects.filter(user=user)
        .select_related("product", "variant", "variant__colour")
        .order_by("-created_at")
    )


def _cart_payload(request, extra=None):
    """
    Single source of truth for cart state. Every endpoint that mutates the
    cart (add/increase/decrease/remove/note) returns this same shape, and
    both the header drawer and the full /cart/ page render from it, so the
    two views can never drift out of sync with each other.
    """

    cart_items = _cart_queryset(request.user) if request.user.is_authenticated else Cart.objects.none()

    cart_count = sum(item.quantity for item in cart_items)
    subtotal = sum(item.line_total for item in cart_items)

    payload = {
        "success": True,
        "cart_count": cart_count,
        "subtotal": str(subtotal),
        "drawer_html": render_to_string(
            "store/includes/cart_drawer_body.html",
            {"cart_items": cart_items, "total": subtotal},
            request=request,
        ),
        "table_html": render_to_string(
            "store/includes/cart_table_rows.html",
            {"cart_items": cart_items},
            request=request,
        ),
    }

    if extra:
        payload.update(extra)

    return payload


def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    try:
        qty = max(1, int(request.GET.get("qty", 1)))
    except (TypeError, ValueError):
        qty = 1

    variant = None
    variant_id = request.GET.get("variant_id")
    if variant_id:
        variant = ProductVariant.objects.filter(id=variant_id, product=product).first()

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse(
                {"success": False, "error": "login_required"},
                status=401,
            )
        return redirect(f"{reverse('login')}?next={request.META.get('HTTP_REFERER', '/')}")

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        variant=variant,
        defaults={"quantity": qty},
    )

    if not created:
        cart_item.quantity += qty
        cart_item.save()

    if is_ajax:
        return JsonResponse(_cart_payload(request, extra={
            "product_name": product.title,
            "product_image": product.image.url if product.image else "",
        }))

    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def cart(request):

    cart_items = _cart_queryset(request.user)
    subtotal = sum(item.line_total for item in cart_items)

    return render(
        request,
        "store/cart.html",
        {
            "cart_items": cart_items,
            "total": subtotal,
        }
    )


@login_required
@require_POST
def increase_cart(request, item_id):

    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()

    return JsonResponse(_cart_payload(request, extra={"quantity": cart_item.quantity}))


@login_required
@require_POST
def decrease_cart(request, item_id):

    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        new_quantity = cart_item.quantity
    else:
        cart_item.delete()
        new_quantity = 0

    return JsonResponse(_cart_payload(request, extra={"quantity": new_quantity}))


@login_required
@require_POST
def remove_cart(request, item_id):

    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()

    return JsonResponse(_cart_payload(request, extra={"removed": True}))


@login_required
@require_POST
def update_cart_note(request, item_id):

    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.note = request.POST.get("note", "")[:200]
    cart_item.save(update_fields=["note"])

    return JsonResponse(_cart_payload(request))
# ==========================
# WISHLIST
@login_required
def wishlist(request):

    items = (
        Wishlist.objects.filter(user=request.user)
        .select_related("product")
    )

    sort = request.GET.get("sort", "date")

    if sort == "price_low":
        items = items.order_by("product__price")
    elif sort == "price_high":
        items = items.order_by("-product__price")
    elif sort == "availability":
        items = items.order_by("-product__in_stock", "-created_at")
    else:
        items = items.order_by("-created_at")

    recently_viewed_ids = request.session.get("recently_viewed", [])
    recently_viewed = list(Product.objects.filter(id__in=recently_viewed_ids))
    recently_viewed.sort(
        key=lambda p: recently_viewed_ids.index(p.id) if p.id in recently_viewed_ids else 0
    )

    return render(
        request,
        "store/wishlist.html",
        {
            "wishlist_items": items,
            "current_sort": sort,
            "recently_viewed": recently_viewed[:8],
        },
    )


@login_required
@require_POST
def wishlist_bulk_action(request):

    try:
        payload = json.loads(request.body or "{}")
    except (ValueError, TypeError):
        payload = {}

    action = payload.get("action")
    product_ids = payload.get("product_ids", [])

    qs = Wishlist.objects.filter(user=request.user)

    if action == "remove_all":
        qs.delete()

    elif action == "remove_selected":
        qs.filter(product_id__in=product_ids).delete()

    elif action == "move_selected_to_cart":
        wishlist_qs = qs.filter(product_id__in=product_ids).select_related("product")
        for item in wishlist_qs:
            cart_item, created = Cart.objects.get_or_create(
                user=request.user, product=item.product, variant=None,
                defaults={"quantity": 1},
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()
        wishlist_qs.delete()

    elif action == "move_all_to_cart":
        wishlist_qs = qs.select_related("product")
        for item in wishlist_qs:
            cart_item, created = Cart.objects.get_or_create(
                user=request.user, product=item.product, variant=None,
                defaults={"quantity": 1},
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()
        wishlist_qs.delete()

    else:
        return JsonResponse({"success": False, "error": "Unknown action."}, status=400)

    remaining = Wishlist.objects.filter(user=request.user).count()
    cart_count = sum(c.quantity for c in Cart.objects.filter(user=request.user))

    return JsonResponse({
        "success": True,
        "wishlist_count": remaining,
        "cart_count": cart_count,
    })


@login_required
@require_POST
def wishlist_get_share_link(request):

    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    if not profile.wishlist_share_token:
        profile.wishlist_share_token = uuid.uuid4()
        profile.save(update_fields=["wishlist_share_token"])

    share_url = request.build_absolute_uri(
        reverse("wishlist_shared", args=[profile.wishlist_share_token])
    )

    return JsonResponse({"success": True, "share_url": share_url})


def wishlist_shared(request, token):

    profile = get_object_or_404(CustomerProfile, wishlist_share_token=token)

    items = (
        Wishlist.objects.filter(user=profile.user)
        .select_related("product")
        .order_by("-created_at")
    )

    return render(
        request,
        "store/wishlist_shared.html",
        {
            "wishlist_items": items,
            "owner_name": profile.user.first_name or profile.user.username,
        },
    )


@login_required
def add_to_wishlist(request, product_id):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return JsonResponse({
        "success": True,
        "wishlisted": True
    })


@login_required
def remove_wishlist(request, product_id):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    return JsonResponse({
        "success": True,
        "wishlisted": False
    })
# STATIC PAGES
# ==========================

def policy_page(request, slug):

    page = PolicyPage.objects.filter(slug=slug).first()

    if page is None:
        # Graceful fallback instead of a 404 while admin hasn't created
        # this page yet — matches the "hide/soft-fail rather than break"
        # approach used elsewhere on the site.
        page = PolicyPage(slug=slug, title=slug.replace("-", " ").title())

    return render(
        request,
        "store/policy_page.html",
        {"page": page},
    )


def policy_index(request):

    policies = PolicyPage.objects.filter(
        show_in_policy_footer=True
    ).order_by("footer_order", "title")

    return render(
        request,
        "store/policy_index.html",
        {"policies": policies},
    )


def about(request):
    return policy_page(request, "about-us")


def faq(request):
    return policy_page(request, "faqs")


def privacy(request):
    return policy_page(request, "privacy-policy")


def terms_conditions(request):
    return policy_page(request, "terms-and-conditions")


def refund_policy(request):
    return policy_page(request, "refund-policy")


def support(request):
    return policy_page(request, "support")


def contact(request):

    page = PolicyPage.objects.filter(slug="contact-information").first()

    return render(
        request,
        "store/contact.html",
        {"page": page},
    )


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("home")

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(
        request,
        "store/login.html"
    )
def register_view(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        # Username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        # Email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name,
        )

        login(request, user)

        messages.success(
            request,
            "Welcome to Aarti Collection!"
        )

        return redirect("home")

    return render(
        request,
        "store/register.html"
    )


def forgot_password_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = User.objects.filter(
            username=username,
            email__iexact=email
        ).first()

        if not user:
            messages.error(
                request,
                "We couldn't find an account with that username and email combination."
            )
            return redirect("forgot_password")

        if not new_password or new_password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )
            return redirect("forgot_password")

        if len(new_password) < 8:
            messages.error(
                request,
                "Password must be at least 8 characters long."
            )
            return redirect("forgot_password")

        user.set_password(new_password)
        user.save()

        messages.success(
            request,
            "Your password has been reset. You can now log in."
        )

        return redirect("login")

    return render(
        request,
        "store/forgot_password.html"
    )

@login_required
def profile(request):

    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        # ==========================
        # USER DETAILS
        # ==========================

        request.user.first_name = request.POST.get(
            "first_name",
            ""
        )

        request.user.last_name = request.POST.get(
            "last_name",
            ""
        )

        request.user.email = request.POST.get(
            "email",
            ""
        )

        request.user.save()

        # ==========================
        # CUSTOMER PROFILE
        # ==========================

        profile.phone = request.POST.get(
            "phone",
            ""
        )

        profile.address = request.POST.get(
            "address",
            ""
        )

        profile.city = request.POST.get(
            "city",
            ""
        )

        profile.state = request.POST.get(
            "state",
            ""
        )

        profile.pincode = request.POST.get(
            "pincode",
            ""
        )

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES["profile_image"]

        profile.save()

        messages.success(
            request,
            "Your profile has been updated successfully."
        )

        return redirect("profile")

    # ==========================
    # DASHBOARD DATA
    # ==========================

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    cart_count = Cart.objects.filter(
        user=request.user
    ).count()

    total_orders = Order.objects.filter(user=request.user).count()

    recent_orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    recently_viewed_ids = request.session.get("recently_viewed", [])
    recently_viewed = list(
        Product.objects.filter(id__in=recently_viewed_ids)
    )
    # Preserve the most-recently-viewed-first order from the session list
    recently_viewed.sort(
        key=lambda p: recently_viewed_ids.index(p.id) if p.id in recently_viewed_ids else 0
    )

    context = {

        "profile": profile,
        "recent_orders": recent_orders,
        "total_orders": total_orders,
        "wishlist_count": wishlist_count,
        "cart_count": cart_count,
        "recently_viewed": recently_viewed[:8],
    }

    return render(
        request,
        "store/profile.html",
        context,
    )
@login_required
def checkout(request):

    cart_items = Cart.objects.filter(
        user=request.user
    )

    if not cart_items.exists():
        return redirect("cart")

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    if request.method == "POST":

        shipping_option = request.POST.get("shipping_option", "standard")
        shipping_fee = 149 if shipping_option == "express" else 0
        is_gift = request.POST.get("is_gift") == "on"
        gift_message = request.POST.get("gift_message", "").strip() if is_gift else ""

        gift_wrap = request.POST.get("gift_wrap") == "on"
        gift_paper = request.POST.get("gift_paper", "") if gift_wrap else ""
        valid_papers = dict(Order.GIFT_PAPER_CHOICES)
        if gift_paper not in valid_papers:
            gift_paper = next(iter(valid_papers)) if gift_wrap else ""
        gift_wrap_fee = GIFT_WRAP_FEE if gift_wrap else 0

        order = Order.objects.create(

            user=request.user,

            customer_name=request.POST.get("name"),

            phone=request.POST.get("phone"),

            address=request.POST.get("address"),

            total_amount=total + shipping_fee + gift_wrap_fee,

            shipping_option=shipping_option,

            shipping_fee=shipping_fee,

            is_gift=is_gift,

            gift_message=gift_message,

            gift_wrap=gift_wrap,

            gift_paper=gift_paper,

            gift_wrap_fee=gift_wrap_fee,

        )

        return redirect(
            "payment_page",
            order_id=order.id
        )

    return render(
        request,
        "store/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
            "gift_wrap_fee": GIFT_WRAP_FEE,
            "gift_paper_choices": Order.GIFT_PAPER_CHOICES,
        }
    )
@login_required
def payment_page(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    if request.method == "POST":

        order.upi_transaction_id = request.POST.get(
            "transaction_id"
        )

        if "screenshot" in request.FILES:
            order.payment_screenshot = request.FILES[
                "screenshot"
            ]

        if order.status == "pending":
            order.status = "submitted"

        order.save()

        Cart.objects.filter(
            user=request.user
        ).delete()

        return render(
            request,
            "store/payment_success.html",
            {
                "order": order
            }
        )

    return render(
        request,
        "store/payment_page.html",
        {
            "order": order
        }
    )
def size_products(request, id):
    size = get_object_or_404(SizeOption, id=id)

    products = Product.objects.filter(
        sizes=size
    )

    return render(
        request,
        "store/size_products.html",
        {
            "size": size,
            "products": products,
        }
    )
def add_review(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug
    )
    if request.method == "POST":
        review = Review.objects.create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            rating=request.POST.get("rating"),
            comment=request.POST.get("comment"),
        )

        # Optional photo attachments — cap at 5 to keep this sane
        attachments = request.FILES.getlist("attachments")[:5]

        for photo in attachments:
            ReviewImage.objects.create(review=review, image=photo)

        messages.success(
            request,
            "Thank you! Your review has been submitted."
        )
    return redirect(
        "product_detail",
        slug=slug
    )

def bangle_size_guide(request):
    return render(request, "store/bangle_size_guide.html")
def accessibility(request):
    return render(
        request,
        "store/accessibility.html"
    )
def shipping_returns(request):
    return policy_page(request, "shipping-returns")
@login_required
def delete_account(request):

    if request.method == "POST":

        user = request.user
        password = request.POST.get("password", "")

        if not user.check_password(password):
            messages.error(
                request,
                "Incorrect password. Your account was not deleted."
            )
            return redirect("profile")

        # Soft delete: deactivate + anonymise login-identifying fields,
        # but keep the row (and order history) intact rather than a hard
        # delete, since that would also cascade-delete Orders.
        user.is_active = False
        user.email = f"deleted-{user.id}@aarticollection.invalid"
        user.save(update_fields=["is_active", "email"])

        from django.contrib.auth import logout
        logout(request)

        messages.success(
            request,
            "Your account has been deactivated. Contact support if you'd like it fully removed."
        )

        return redirect("home")

    return redirect("profile")

def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Remove previous cart items (optional)
    Cart.objects.filter(user=request.user).delete()

    # Add only this product
    Cart.objects.create(
        user=request.user,
        product=product,
        quantity=1
    )

    return redirect("checkout")

def subscribe_newsletter(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()

        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if email:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)

            if created:
                try:
                    send_mail(
                        subject="Welcome to Aarti Collection 💚",
                        message=(
                            "Thank you for subscribing to Aarti Collection!\n\n"
                            "Here's what you'll receive:\n"
                            "- New arrivals\n"
                            "- Exclusive offers\n"
                            "- Festive collections\n"
                            "- Styling inspiration\n\n"
                            "Use code WELCOME10 for 10% off your first order."
                        ),
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                        recipient_list=[email],
                        fail_silently=True,
                    )
                except Exception:
                    # Email backend may not be configured yet — the
                    # subscription itself still succeeds either way.
                    pass

            if is_ajax:
                return JsonResponse({"success": True, "already_subscribed": not created})

            messages.success(request, "You're subscribed! Watch your inbox for 10% off.")
        else:
            if is_ajax:
                return JsonResponse({"success": False, "error": "Please enter a valid email."})

            messages.error(request, "Please enter a valid email.")

    return redirect(request.META.get("HTTP_REFERER", "home"))
