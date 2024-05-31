from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe


from .models import (
    Category,
    Product,
    ProductLine,
    ProductImage,
    AttributeValue,
    ProductAttribute,
    ProductType,

)


class CategoryAdmin(admin.ModelAdmin):
    pass


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue.product_line_attribute_value.through


@admin.register(ProductLine)
class ProductLineAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, AttributeValueInline]


class EditLinkInline(object):
    def edit(self, instance):
        url = reverse(
            f"admin:{instance._meta.app_label}_{instance._meta.model_name}_change",
            args=[instance.pk],
        )
        if instance.pk:
            link = mark_safe('<a href="{u}">edit</a>'.format(u=url))
            return link
        else:
            return ""


class ProductLineInline(EditLinkInline,admin.TabularInline):
    model = ProductLine
    readonly_fields = ["edit"]


class AttributeValueProductInline(admin.TabularInline):
    model = AttributeValue.product_attr_value.through


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductLineInline, AttributeValueProductInline]


class BrandAdmin(admin.ModelAdmin):
    pass


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute.product_type_attribute.through


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        ProductAttributeInline
    ]


admin.site.register(Category, CategoryAdmin)


admin.site.register(ProductAttribute)
admin.site.register(AttributeValue)
