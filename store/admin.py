from django.contrib import admin
from django import forms
from .models import (
    Product,
    Category,
    SubCategory,
    ProductTag,
    Banner,
    SiteSettings,
    ProductVariant,
    ProductVariantImage,
    ProductImage,
    Order,
    ShopLook,
    Colour,
    SizeCategory,
    SizeOption,
    Review,
    Cart,
    Wishlist,
    PolicyPage,
)
from .widgets import RichTextEditorWidget
class ProductVariantInline(admin.TabularInline):

    model = ProductVariant

    extra = 1


class ProductVariantImageInline(admin.TabularInline):

    model = ProductVariantImage

    extra = 2


class ProductImageInline(admin.TabularInline):
    """Unlimited gallery images for the base product — admin can add,
    reorder (edit the 'order' number) and delete rows here directly."""

    model = ProductImage

    extra = 3

    fields = ("image", "order")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    inlines = [ProductImageInline]

    list_display = (
        "title",
        "category",
        "subcategory",
        "price",
        "is_trending",
        "is_best_seller",
        "featured",
        "in_stock",
        "stock_quantity",
    )

    list_editable = (
        "stock_quantity",
    )

    list_filter = (
        "category",
        "subcategory",
        "is_trending",
        "is_best_seller",
        "featured",
        "in_stock",
    )

    search_fields = (
        "title",
        "category__name",
        "subcategory__name",
        "tags__name",
        "material",
        "purpose",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    filter_horizontal = ("tags", "sizes")

    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "slug", "description", "price", "old_price", "image", "image_back", "video")
        }),
        ("Classification", {
            "fields": ("category", "subcategory", "tags")
        }),
        ("Product Attributes", {
            "fields": ("material", "purpose")
        }),
        ("Size System", {
            "fields": ("size_category", "sizes")
        }),
        ("Flags", {
            "fields": ("is_best_seller", "is_trending", "featured", "in_stock")
        }),
    )

    inlines = [ProductVariantInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "show_on_home",
        "home_sort_order",
    )

    list_editable = (
        "show_on_home",
        "home_sort_order",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "slug",
    )

    list_filter = (
        "category",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "active",
        "order",
        "video",
    )
    list_editable = (
        "order",
        "active",
    )
    fields = (
        "title",
        "subtitle",
        "description",
        "button_text",
        "image",
        "video",
        "active",
        "order",
    )

@admin.register(ShopLook)
class ShopLookAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "active",
        "product_count",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    filter_horizontal = (
        "products",
    )

    fieldsets = (
        ("Look", {
            "fields": ("title", "slug", "subtitle", "description", "image", "active", "layout_size"),
        }),
        ("Call To Action", {
            "fields": ("cta_text", "cta_url"),
            "description": "Leave the CTA link blank to send shoppers to this look's own product list instead of an external URL.",
        }),
        ("Products", {
            "fields": ("products",),
        }),
    )
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "brand_name",
        "phone",
        "email",
        "gst_number",
    )
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    inlines = [ProductVariantImageInline]

    list_display = (
        "product",
        "colour",
        "stock",
        "active",
    )

    list_filter = (
        "active",
        "product",
    )

    search_fields = (
        "product__title",
        "colour__name",
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer_name",
        "phone",
        "total_amount",
        "shipping_option",
        "is_gift",
        "status",
        "created_at",
    )

    list_editable = (
        "status",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "phone",
        "upi_transaction_id",
    )

    readonly_fields = (
        "created_at",
    )

@admin.register(Colour)
class ColourAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code")
    search_fields = ("name",)


@admin.register(SizeCategory)
class SizeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(SizeOption)
class SizeOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "approved",
        "created_at",
    )

    list_filter = (
        "rating",
        "approved",
    )

    search_fields = (
        "name",
        "email",
        "product__title",
    )
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "variant", "quantity", "note", "created_at")

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")


class PolicyPageForm(forms.ModelForm):
    class Meta:
        model = PolicyPage
        fields = "__all__"
        widgets = {
            "content": RichTextEditorWidget(attrs={"rows": 20}),
        }


@admin.register(PolicyPage)
class PolicyPageAdmin(admin.ModelAdmin):
    form = PolicyPageForm
    list_display = (
        "title", "slug", "show_in_policy_footer", "footer_order",
        "updated_at", "view_on_site_link",
    )
    list_editable = ("show_in_policy_footer", "footer_order")
    list_filter = ("show_in_policy_footer",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")

    def view_on_site_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse, NoReverseMatch
        try:
            url = reverse("policy_page", args=[obj.slug])
            return format_html('<a href="{}" target="_blank">View page ↗</a>', url)
        except NoReverseMatch:
            return "-"
    view_on_site_link.short_description = "Live page"