from django.shortcuts import get_object_or_404


class RecipeService:
    """
    Сервис для добавления и удаления объектов из модели связей с рецептом.
    """
    @staticmethod
    def add(request, recipe, model):
        """
        Добавление объекта в модель связей с рецептом.
        """
        obj, created = model.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        return created

    @staticmethod
    def remove(request, recipe, model):
        """
        Удаление объекта из модели связей с рецептом.
        """
        obj = get_object_or_404(model, user=request.user, recipe=recipe)
        obj.delete()
