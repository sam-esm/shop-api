import pytest
# from pytest_factoryboy import register

from shop.models import Category, Product,Brand
from shop.tests.factories import CategoryFactory,ProductFactory, BrandFactory


@pytest.fixture()
def category(db) -> Category:
    return CategoryFactory(name="category_0",parent=None)


@pytest.fixture(scope="session")
def brand(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        return BrandFactory(name="brand_0")


# @pytest.fixture()
# def brand(db) -> Brand:
#     return 


@pytest.fixture()
def category_1(db,category) -> Category:
    return CategoryFactory(parent=category)


@pytest.fixture()
def product(db, category) -> Product:
    return ProductFactory(category=category)
