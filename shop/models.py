# Stdlib imports
import uuid

# Core Django imports
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Third-party app imports
from mptt.models import MPTTModel, TreeForeignKey

# Imports from apps
from sam_store.utils.models_mixins import TimeStampedModel
from shop.fields import OrderField


class ActiveQueryset(models.QuerySet):
    """
        Custom queryset for filtering active objects based on the 'active' field.
    """
    def isactive(self):
        """
            Returns a queryset containing only active objects (where 'active' is True).
        """
        return self.filter(active=True)


class Category(TimeStampedModel, MPTTModel):
    """
    Category class model.

    Represents a hierarchical category of products in the online store.
    Inherits from TimeStampedModel and MPTTModel to provide creation and 
    modification timestamps and tree structure.
    """

    name = models.CharField(max_length=220, unique=True)
    slug = models.SlugField(max_length=235, unique=True)
    parent = TreeForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    active = models.BooleanField(default=False)
    objects = ActiveQueryset().as_manager()
    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        """
            Returns the string representation of the category, which is its name.
        """
        return self.name

    def get_absolute_url(self):
        """
            Returns the absolute URL for the category list view filtered by this category.
        """
        return reverse("shop:product_list_by_category", args=[self.slug])


class ProductImage(TimeStampedModel):
    """
    Product Image class model.

    Represents an image of a product in the online store.
    Inherits from TimeStampedModel to provide creation and modification timestamps.


    Attributes:
        image_url (ImageField): The URL of the product image. Images are uploaded to a directory structure by date.
        alt_text (CharField): Alternative text for the image for accessibility purposes.
        product_line (ForeignKey): A foreign key reference to the related ProductLine model.

    """

    image_url = models.ImageField(upload_to="products/%Y/%m/%d",blank=True)
    alt_text = models.CharField(max_length=100,blank=True)
    product_line = models.ForeignKey(
        "ProductLine", related_name="images", on_delete=models.CASCADE
    )
    order = OrderField(unique_for_field="product_line",blank=True)

    def clean(self):
        """
        Custom clean method to validate uniqueness of 'order' field within a product line.

        Raises:
            ValidationError: If the 'order' value is not unique within a product line.
        """
        qs = ProductImage.objects.filter(product_line=self.product_line)
        for obj in qs:
            if self.id != obj.id and self.order == obj.order:
                raise ValidationError("Duplicate value.")

    def save(self, *args, **kwargs):
        """
        Overrides the save method to call full_clean before saving.

        This ensures that the custom clean method is called before saving.
        """

        self.full_clean()
        return super(ProductImage, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.order)


class Product(TimeStampedModel):
    """
    Product class model.

    Represents a product in the online store.
    Inherits from TimeStampedModel to provide creation and modification timestamps.
    """
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    category = TreeForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    product_type = models.ForeignKey(
        "ProductType", related_name="products", on_delete=models.PROTECT,null=True
    )
    attribute_value = models.ManyToManyField(
        "AttributeValue",
        through="ProductAttributeValue",
        related_name="product_attr_value",
    )
    objects = ActiveQueryset.as_manager()
    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["uuid"]),
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        """
        Returns the string representation of the product, which is its name.
        """
        return self.name

    def get_absolute_url(self):
        """
        Returns the absolute URL for the product detail view.
        """
        return reverse("shop:product_detail", args=[self.id, self.slug])


class ProductAttributeValue(models.Model):
    attribute_value = models.ForeignKey(
        "AttributeValue",
        on_delete=models.CASCADE,
        related_name="product_value_av",
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="producte_value_pl",
    )

    class Meta:
        unique_together = ("attribute_value", "product")


class ProductLine(TimeStampedModel):
    """
    Product Line class model.

    Represents a product Line in the online store.
    Inherits from TimeStampedModel to provide creation and modification timestamps.
    """
    price = models.DecimalField(decimal_places=2, max_digits=30)
    sku = models.CharField(max_length=100) #stock keeping unit
    stock_qty = models.IntegerField() #stock quntity
    product = models.ForeignKey(Product, related_name="product_line", on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    order = OrderField(unique_for_field="product", blank=True)
    weight = models.FloatField(null=True)
    product_type = models.ForeignKey(
        "ProductType", on_delete=models.PROTECT, related_name="product_lines",null=True
    )
    attribute_value = models.ManyToManyField(
        "AttributeValue",
        through="ProductLineAttributeValue",
        related_name="product_line_attribute_value",
    )  # type: ignore
    objects = ActiveQueryset.as_manager()

    def clean(self):
        qs = ProductLine.objects.filter(product=self.product)
        for obj in qs:
            if self.id != obj.id and self.order == obj.order:
                raise ValidationError("Duplicate value.")
    class Meta:
        ordering = ["stock_qty"]
        indexes = [
            models.Index(fields=["sku", "active"]),
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        """
        Returns the string representation of the productLine, which is its name.
        """
        return self.sku

    def get_absolute_url(self):
        """
        Returns the absolute URL for the productLine detail view.
        """
        return 

class ProductAttribute(TimeStampedModel):

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AttributeValue(TimeStampedModel):
    value = models.CharField(max_length=100)
    product_attribute = models.ForeignKey(
        "ProductAttribute", on_delete=models.CASCADE, related_name="attribute_value"
    )

    def __str__(self):
        return f"{self.product_attribute.name}-{self.value}"


class ProductLineAttributeValue(models.Model):
    """
        nameing convention: SourceModel+sourceTragetmodel
    """
    product_line = models.ForeignKey(
        'ProductLine', 
        related_name='through_pl_av', 
        on_delete=models.CASCADE,
        )
    attribute_value = models.ForeignKey(
        "AttributeValue",
        related_name="through_pl_av",
        on_delete=models.CASCADE,
    )
    class Meta:
        unique_together = ("attribute_value", "product_line")

    def clean(self):
        qs = (
            ProductLineAttributeValue.objects.filter(
                attribute_value=self.attribute_value
            )
            .filter(product_line=self.product_line)
            .exists()
        )

        if not qs:
            iqs = ProductAttribute.objects.filter(
                attribute_value__product_line_attribute_value=self.product_line
            ).values_list("pk", flat=True)

            if self.attribute_value.product_attribute.id in list(iqs):
                raise ValidationError("Duplicate attribute exists")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProductLineAttributeValue, self).save(*args, **kwargs)


class ProductType(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    attribute = models.ManyToManyField(
        ProductAttribute,
        through="ProductTypeAttribute",
        related_name="product_type_attribute",
    )# type: ignore 

    def __str__(self):
        return str(self.name)


class ProductTypeAttribute(models.Model):

    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        related_name="product_type_attribute_pt",
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name="product_type_attribute_a",
    )

    class Meta:
        unique_together = ("product_type", "attribute")
