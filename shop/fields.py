from django.core import checks
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class OrderField(models.PositiveIntegerField):
    """
    An ordering field based on a unique field.

    Args:
        unique_for_field (str): The name of the field for which the ordering is unique.

    Attributes:
        description (str): A description of the field.

    Example:
        class MyModel(models.Model):
            order = OrderField(unique_for_field='category')

    """
    description = "Ordering field on a unique field"

    def __init__(self, unique_for_field=None, *args, **kwargs):
        """
        Initialize the OrderField.

        Args:
            unique_for_field (str): The name of the field for which the ordering is unique.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        self.unique_for_field = unique_for_field
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        """
        Perform checks on the OrderField.

        Returns:
            list: A list of check messages.

        """
        return [
            *super().check(**kwargs),
            *self._check_for_field_attribute(**kwargs),
        ]

    def _check_for_field_attribute(self, **kwargs):
        """
        Check if the 'unique_for_field' attribute is defined and valid.

        Returns:
            list: A list of check messages.

        """
        if self.unique_for_field is None:
            return [
                checks.Error("OrderField must define a 'unique_for_field' attribute")
            ]
        elif self.unique_for_field not in [
            f.name for f in self.model._meta.get_fields()
        ]:
            return [
                checks.Error(
                    "OrderField entered does not match an existing model field"
                )
            ]
        return []

    def pre_save(self, model_instance, add):
        """
            Calculate the value of field based on previous values
        
        """

        if getattr(model_instance, self.attname) is None:
            qs = self.model.objects.all() #type: ignore
            try:
                query = {
                    self.unique_for_field: getattr(
                        model_instance, self.unique_for_field
                    )
                }
                qs = qs.filter(**query)
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 1
            return value
        else:

            return super().pre_save(model_instance, add)






