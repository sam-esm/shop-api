from django.urls import reverse

import factory

from shop.models import Product, Category, Brand


class CategoryFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Category model instances for testing.

    This factory generates unique 'name' and 'slug' fields for each instance
    and uses another CategoryFactory for the 'parent' field, allowing for
    the creation of a hierarchy of categories.
    """

    class Meta:
        model = Category  # Specifies the model to be created by the factory

    name = factory.Sequence(lambda n: "category_%d" % n)
    slug = factory.Sequence(lambda n: "category_%d" % n)
    parent = factory.SubFactory(
        "shop.tests.factories.CategoryFactory", parent=None
    )  # Uses another CategoryFactory for the 'parent' field


class BrandFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Category model instances for testing.

    This factory generates unique 'name' and 'slug' fields for each instance
    and uses another CategoryFactory for the 'parent' field, allowing for
    the creation of a hierarchy of categories.
    """

    class Meta:
        model = Brand  # Specifies the model to be created by the factory

    name = factory.Sequence(lambda n: "brand_%d" % n)


class ProductFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Product model instances for testing.

    This factory generates unique 'name' and 'slug' fields for each instance,
    uses a CategoryFactory for the 'category' field, and uses the Faker library
    to generate 'description', 'price', and 'available' fields.
    """

    class Meta:
        model = Product  # Specifies the model to be created by the factory

    category = None
    name = factory.Sequence(lambda n: "product_%d" % n)
    slug = factory.Sequence(lambda n: "product_%d" % n)
    description = factory.Faker("text")
    # price = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    available = factory.Faker("pybool")
    # main_image = None  # Assuming main_image is optional and can be blank

    @factory.post_generation
    def category(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            print(extracted)
            self.category = extracted
