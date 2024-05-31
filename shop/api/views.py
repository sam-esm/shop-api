# Stdlib imports

# Core Django imports
from django.db import connection
from django.db.models import Prefetch

# Third-party app imports
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import SqlLexer
from sqlparse import format

from shop.models import Category, Product, ProductImage, ProductLine
from shop.api.serializers import CategorySerializer, ProductCategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing categories.

    This viewset provides CRUD (Create, Retrieve, Update, Delete) operations
    for the Category model. It uses the CategorySerializer for data serialization.

    Usage:
    - GET /api/categories/ : Retrieve a list of all categories.
    - POST /api/categories/ : Create a new category.
    - GET /api/categories/{id}/ : Retrieve details of a specific category.
    - PUT /api/categories/{id}/ : Update details of a specific category.
    - DELETE /api/categories/{id}/ : Delete a specific category.

    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ModelViewSet):

    """
        A viewset for viewing and manipulating product instances.
    """
    queryset = Product.objects.all().isactive()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    @extend_schema(
        description="More descriptive text",
    )
    def retrieve(self, request, slug=None) -> Response:  # type: ignore
        """
        Retrieve a product by its slug.

        This endpoint returns a product instance matching the provided slug.
        It also prefetches related data for performance optimization.

        Args:
            request (Request): The request object.
            slug (str, optional): The slug of the product.

        Returns:
            Response: The response object containing product data.
        """
        # Filter the queryset by slug and prefetch related data
        queryset = (
            self.queryset.filter(slug=slug)
            .select_related("category")
            .prefetch_related(Prefetch("product_line__images"))
            .prefetch_related(Prefetch("product_line__attribute_value__product_attribute"))
        )
        # Serialize the queryset
        serializer = self.serializer_class(queryset, many=True)
        data = Response(serializer.data)
        q = list(connection.queries)
        print(len(q))
        for qs in q:
            sqlformatted = format(str(qs["sql"]), reindent=True)
            print(highlight(sqlformatted, SqlLexer(), TerminalFormatter()))
        return data

    # @action(
    #     methods=["get"],
    #     url_path=r"category/(?P<slug>[\w-]+)/all",
    #     url_name="all",
    #     detail=False,
    # )
    # def list_all_category_products(self, request, slug=None):
    #     """
    #     An endpoint to return products by category slug
    #     """
    #     queryset = self.queryset.filter(category__slug=slug)
    #     serializer = self.serializer_class(queryset, many=True)
    #     return Response(serializer.data)

    @action(
        methods=["get"],
        detail=False,
        url_path=r"category/(?P<slug>[\w-]+)",
    )
    def list_product_by_category_slug(self, request, slug=None):
        """
        An endpoint to return products by category
        """
        serializer = ProductCategorySerializer(
            self.queryset.filter(category__slug=slug)
            .prefetch_related(
                Prefetch("product_line", queryset=ProductLine.objects.order_by("order"))
            )
            .prefetch_related(
                Prefetch(
                    "product_line__images",
                    queryset=ProductImage.objects.filter(order=1),
                )
            ),
            many=True,
        )
        return Response(serializer.data)
