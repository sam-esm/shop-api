# Stdlib imports

# Core Django imports
from rest_framework import serializers

# Third-party app imports

# Imports from apps
from ..models import  Category, Product, ProductImage, ProductLine, AttributeValue , ProductAttribute


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """
    class Meta:
        model = Category  # Specifies the model to be serialized
        fields = ["name", "slug", "parent"]  # Fields to be included in the serialization


class ProductImageSerailizer(serializers.ModelSerializer):
    """
    Serializer for Image model.

    """

    class Meta:
        model = ProductImage  # Specifies the model to be serialized
        exclude = ("id","product_line") # Fields to be excluded in the serialization


class ProductAttributeSerializer(serializers.ModelSerializer):
    """
    Serializer for Product Attribute

    """
    class Meta:
        model = ProductAttribute  # Specifies the model to be serialized
        fields = ["name","id"]  # Fields to be included in the serialization


class AttributeValueSerializer(serializers.ModelSerializer):
    """
    Serializer for Product Attribute

    """
    product_attribute = ProductAttributeSerializer(many=False)

    class Meta:
        model = AttributeValue  # Specifies the model to be serialized
        fields = [
            "value",
            "product_attribute",
        ]  # Fields to be included in the serialization


class ProductLineSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductLine model.
    """
    images = ProductImageSerailizer(many=True)
    attribute_value = AttributeValueSerializer(many=True)
    class Meta:
        model = ProductLine  # Specifies the model to be serialized

        fields = (
            "price",
            "sku",
            "stock_qty",
            "order",
            "images",
            "attribute_value",
        )  # Fields to be included in the serialization

    def to_representation(self, instance):
        """
        Change data representation 
        """
        data = super().to_representation(instance)

        av_data = data.pop("attribute_value")
        attr_values = {}
        for key in av_data:
            print(key)
            attr_values.update({key["product_attribute"]["id"]: key["value"]})
        data.update({"specification": attr_values})

        return data


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    """

    category_name = serializers.CharField(source="category.name")
    product_line = ProductLineSerializer(many=True)
    attributes = serializers.SerializerMethodField()
    class Meta:
        model = Product  # Specifies the model to be serialized
        fields = (
            "name",
            "slug",
            "description",
            "category_name",
            "product_line",
            "attributes"
        )

    def get_attributes(self, obj):
        """
        get the attributes of the product.
        """
        # TODO: check of attribute exist
        attributes = obj.product_type.attribute.all()
        return ProductAttributeSerializer(attributes, many=True).data

    def to_representation(self, instance):
        """
            Change data representation 
        """
        data = super().to_representation(instance)
        av_data = data.pop("attributes")
        attr_values = {}
        for key in av_data:
            attr_values.update({key["id"]: key["name"]})
        data.update({"type specification": attr_values})

        return data


class ProductLineCategorySerializer(serializers.ModelSerializer):

    """
    This class is a serializer for the ProductLine model.
    It specifies the fields to be included in the serialization of a ProductLine object.
    """

    images = ProductImageSerailizer(many=True)

    class Meta:
        model = ProductLine
        fields = (
            "price",
            "images",
        )


class ProductCategorySerializer(serializers.ModelSerializer):

    """
    This class is a serializer for the Product model.
    It specifies the fields to be included in the serialization of a Product object.
    """
    product_line = ProductLineCategorySerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "name",
            "slug",
            "uuid",
            "created",
            "product_line",
        )

    def to_representation(self, instance):
        """
            Change data representation 
        """
        data = super().to_representation(instance)
        x = data.pop("product_line")

        if x:
            price = x[0]["price"]
            image = x[0]["images"]
            data.update({"price": price})
            data.update({"image": image})

        return data
