# Stdlib imports

# Core Django imports
from shop.models import Category, Product


# Third-party app imports
import pytest

# Imports from your apps
from shop.api.serializers import CategorySerializer

class TestBrandModel:

    def test_str_method(self, brand):
        # Arrange
        # Act
        # Assert
        assert brand.__str__() == "brand_0"
    def test_str_method2(self, brand):
        # Arrange
        # Act
        # Assert
        assert brand.__str__() == "brand_0"



def test_category_str(db: None, category: Category):
    c1 = category
    assert str(c1) == "category_0"


def test_category_parent(db: None, category: Category, category_1: Category):
    c1 = category
    c2 = category_1
    assert c2.parent == c1


def test_category_with_out_parent(db: None, category: Category, category_1: Category):
    c1 = category
    print(c1)
    assert c1.parent == None


def test_category_serializer(db: None, category: Category, category_1: Category):
    c1 = category
    serializer = CategorySerializer(c1)
    print(serializer.data)

    assert serializer.data


def test_product_str(db: None, product: Product):
    product1 = product
    assert str(product1) == "product_0"


def test_category_product(db: None, product: Product, category:Category):
    product1 = product

    assert product1.category == category
