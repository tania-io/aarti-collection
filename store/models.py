from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

class SiteSettings(models.Model):
    brand_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    pinterest = models.URLField(blank=True)
    logo = models.ImageField(upload_to="logo/", blank=True, null=True)

    whatsapp = models.CharField(
        max_length=20,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    upi_id = models.CharField(
        max_length=100,
        blank=True
    )
    gst_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="GST Number"
    )
    qr_code = models.ImageField(
        upload_to="payment/",
        blank=True,
        null=True
    )
    gift_section_video = models.FileField(
        upload_to="homepage/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["mp4"]
            )
        ],
        help_text="Homepage Gift Section promotional video."
    )
    gift_section_image = models.ImageField(
        upload_to="gift_section/",
        blank=True,
        null=True
    )
    gift_wrapper_image = models.ImageField(
        upload_to="gift_section/",
        blank=True,
        null=True,
        help_text="Decorative gift-wrap/ribbon accent image shown over the main gift banner."
    )
    gift_background_image = models.ImageField(
        upload_to="gift_section/",
        blank=True,
        null=True,
        help_text="Background texture/pattern behind the whole gift section."
    )
    footer_text = models.CharField(
        max_length=255,
        blank=True
    )
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    def __str__(self):
        return self.brand_name


class Banner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="banners/",
        help_text="Used as the poster/fallback image, and as the banner itself if no video is uploaded."
    )
    video = models.FileField(
        upload_to="banners/videos/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["mp4"])],
        help_text="Optional MP4 banner video. If uploaded, it plays instead of the image."
    )
    button_text = models.CharField(
        max_length=50,
        blank=True,
        default="Explore Collection"
    )
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


# MAIN CATEGORY
class Category(models.Model):

    name = models.CharField(max_length=100)

    slug = models.SlugField(unique=True)

    description = models.TextField(blank=True)

    image = models.ImageField(upload_to="categories/")

    show_on_home = models.BooleanField(
        default=True,
        help_text="Show this category in the homepage 'Shop by Category' section."
    )

    home_sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first in the homepage section."
    )

    class Meta:
        ordering = ["home_sort_order", "name"]

    def __str__(self):
        return self.name


# SUBCATEGORY
class SubCategory(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories"
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="subcategories/",
        blank=True,
        null=True
    )
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# TAGS / COLLECTIONS
class ProductTag(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.name

class Colour(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(unique=True)
    hex_code = models.CharField(
        max_length=6,
        blank=True,
        help_text="Example: FFD700"
    )
    css_style = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional CSS for gradients or transparent swatches."
    )
    def __str__(self):
        return self.name

class SizeCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SizeOption(models.Model):
    category = models.ForeignKey(
        SizeCategory,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
class Product(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(unique=True)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Original / MRP price. Leave blank if there's no discount. Used to show the discount badge."
    )
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )
    image_back = models.ImageField(
        upload_to="products/back/",
        blank=True,
        null=True,
        help_text="Optional second image shown on hover in product listings (e.g. a back/side view)."
    )
    video = models.FileField(
        upload_to="products/videos/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["mp4"])],
        help_text="Optional MP4 product video, shown alongside the images in the gallery."
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tags = models.ManyToManyField(
        ProductTag,
        blank=True
    )
    is_best_seller = models.BooleanField(
        default=False
    )

    is_trending = models.BooleanField(
        default=False
    )
    featured = models.BooleanField(default=False)

    is_gift_collection = models.BooleanField(
        default=False,
        verbose_name="Gift Collection"
    )
    in_stock = models.BooleanField(
        default=True
    )

    stock_quantity = models.PositiveIntegerField(
        default=50,
        help_text="Used to show live stock messages like 'Only 2 left'. Set to 0 to mark sold out."
    )

    def get_stock_status(self):
        """Returns (message, css_class) for the dynamic stock badge."""
        if not self.in_stock or self.stock_quantity == 0:
            return ("Out of Stock", "stock-out")
        if self.stock_quantity <= 3:
            return (f"Only {self.stock_quantity} left", "stock-critical")
        if self.stock_quantity <= 10:
            return (f"Only {self.stock_quantity} left", "stock-low")
        if self.stock_quantity <= 20:
            return ("Selling Fast", "stock-selling-fast")
        if self.stock_quantity <= 40:
            return ("Limited Stock", "stock-limited")
        return ("In Stock", "stock-in")

    material = models.CharField(
        max_length=150,
        blank=True,
        help_text="Example: Cotton Silk, Brass, Glass"
    )
    purpose = models.CharField(
        max_length=150,
        blank=True,
        help_text="Example: Wedding, Party, Puja, Festival"
    )
    
    size_category = models.ForeignKey(
        SizeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    sizes = models.ManyToManyField(
        SizeOption,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def get_badge(self):
        """
        Badge for recommendation cards (Just For You, etc). Priority
        order below — admin controls this entirely through the existing
        is_best_seller / is_trending / featured checkboxes and doesn't
        need a separate field.
        """
        from django.utils import timezone
        from datetime import timedelta

        if self.is_best_seller:
            return "Best Seller"
        if self.is_trending:
            return "Trending Now"
        if self.created_at and self.created_at >= timezone.now() - timedelta(days=30):
            return "New Arrival"
        if self.featured:
            return "Recommended"
        return None

    def get_care_instructions(self):
        category = (self.category.name or "").lower()

        CARE_MAP = {
            "sarees": [
                "Dry clean recommended",
                "Do not bleach",
                "Store folded properly",
            ],
            "bangles": [
                "Avoid water & perfume",
                "Avoid perfume",
                "Store separately",
            ],
            "earrings": [
                "Avoid moisture",
                "Clean after use",
                "Store in pouch or jewellery box",
            ],
            "jewellery box": [
                "Clean with dry cloth",
                "Keep away from moisture",
            ],
            "bracelets": [
                "Remove before bathing, exercising or swimming",
                "Clean with a soft dry cloth",
                "Store in a jewellery pouch",
            ],
            "accessories": [
                "Avoid excessive pulling or bending",
                "Store separately to prevent scratches",
            ],
        }

        return CARE_MAP.get(category, [])

    def average_rating(self):
        """Average of approved review ratings, rounded to 1 decimal. None if no reviews."""
        approved = self.reviews.filter(approved=True)
        if not approved.exists():
            return None
        total = sum(r.rating for r in approved)
        return round(total / approved.count(), 1)

    def review_count(self):
        return self.reviews.filter(approved=True).count()

    def discount_percent(self):
        """Whole-number % off, based on old_price vs price. None if no discount."""
        if self.old_price and self.old_price > self.price:
            return round((self.old_price - self.price) / self.old_price * 100)
        return None

    def __str__(self):
        return self.title


class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


class Cart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        "ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items"
    )

    note = models.CharField(
        max_length=200,
        blank=True,
        default=""
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def line_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"
    
# Layout Size:

class ShopLook(models.Model):

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    TALL = "tall"

    SIZE_CHOICES = [
        (SMALL, "Small"),
        (MEDIUM, "Medium"),
        (LARGE, "Large"),
        (TALL, "Tall"),
    ]

    title = models.CharField(max_length=200)

    slug = models.SlugField(unique=True)
    image = models.ImageField(
        upload_to="shop_looks/"
    )

    subtitle = models.CharField(
        max_length=250,
        blank=True,
        help_text="Short supporting line shown under the title."
    )

    description = models.TextField(blank=True)

    cta_text = models.CharField(
        max_length=50,
        blank=True,
        default="Shop The Look",
        help_text="Call-to-action button label."
    )

    cta_url = models.URLField(
        blank=True,
        help_text="Optional external link. Leave blank to link to this look's product list instead."
    )

    products = models.ManyToManyField(
        Product,
        related_name="shop_looks"
    )

    layout_size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES,
        default=MEDIUM
    )

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    """
    Unlimited extra gallery images for a product (beyond the fixed
    image/image_back fields). Admin can add, reorder (via 'order'),
    and delete these directly from the Product admin page.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gallery_images"
    )

    image = models.ImageField(upload_to="products/gallery/")

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product.title} - image {self.order}"


class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    colour = models.ForeignKey(
        Colour,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    image = models.ImageField(
        upload_to="variants/"
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.product.title} - {self.colour.name}"


class ProductVariantImage(models.Model):
    """Extra gallery/thumbnail images for a colour variant (variant.image stays the primary shot)."""

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="variants/gallery/")

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.variant} - image {self.order}"


class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("submitted", "Payment Submitted"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    ]

    SHIPPING_CHOICES = [
        ("standard", "Standard Delivery (Free, 5-7 days)"),
        ("express", "Special Delivery (₹149, 1-2 days)"),
    ]

    shipping_option = models.CharField(
        max_length=20,
        choices=SHIPPING_CHOICES,
        default="standard"
    )

    shipping_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    is_gift = models.BooleanField(default=False)

    gift_message = models.TextField(
        blank=True,
        help_text="Optional message to include on the gift note."
    )

    GIFT_PAPER_CHOICES = [
        ("kraft", "Rustic Kraft"),
        ("floral", "Floral Print"),
        ("gold_dot", "Gold Dot"),
    ]

    gift_wrap = models.BooleanField(default=False)

    gift_paper = models.CharField(
        max_length=20,
        choices=GIFT_PAPER_CHOICES,
        blank=True,
    )

    gift_wrap_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )
    customer_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    address = models.TextField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    upi_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    payment_screenshot = models.ImageField(
        upload_to="payments/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.id}"
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"    
class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)

    email = models.EmailField(blank=True)
    rating = models.PositiveSmallIntegerField(
        choices=[
            (1, "1 Star"),
            (2, "2 Stars"),
            (3, "3 Stars"),
            (4, "4 Stars"),
            (5, "5 Stars"),
        ]
    )

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.user:
            return f"{self.product.title} - {self.user.username} ({self.rating}⭐)"
        return f"{self.name} - {self.product.title}"

class CustomerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    pincode = models.CharField(
        max_length=10,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    wishlist_share_token = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        help_text="Generated the first time the user shares their wishlist."
    )

    def __str__(self):
        return self.user.username       

class NewsletterSubscriber(models.Model):

    email = models.EmailField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class PolicyPage(models.Model):
    """
    Admin-editable CMS pages (Shipping & Returns, Privacy Policy,
    Terms & Conditions, Refund Policy, About Us, Contact Information,
    FAQs, Support). Content is rich HTML produced by the admin's
    rich-text editor and rendered as-is on the frontend.
    """

    slug = models.SlugField(
        unique=True,
        help_text="Used in the page URL, e.g. 'privacy-policy'."
    )

    title = models.CharField(max_length=150)

    subtitle = models.CharField(
        max_length=250,
        blank=True,
        help_text="Optional short line shown under the page title."
    )

    content = models.TextField(
        blank=True,
        help_text="Rich text content, edited via the toolbar above."
    )

    updated_at = models.DateTimeField(auto_now=True)

    show_in_policy_footer = models.BooleanField(
        default=False,
        help_text="Show this page as a link under the footer's 'Our Policy' "
                   "column. Leave off for pages already linked elsewhere "
                   "(About Us, Contact, Shipping & Returns, etc.)."
    )

    footer_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first in the 'Our Policy' footer column."
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
