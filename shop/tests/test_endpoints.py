import json
from shop.models import Category
from shop.tests.factories import CategoryFactory

class TestCategoryEndpoints:

    endpoint = "/api/categories/"

    def test_category_get(self,db,client):
        print(Category.objects.all())
        # Arrange
        CategoryFactory.create_batch(4, parent=None)
        print(Category.objects.all())
        # Act
        response = client.get(self.endpoint)
        # Assert
        assert response.status_code == 200
        print(json.loads(response.content))
        assert len(json.loads(response.content)) == 4
