import csv
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient

BATCH_SIZE = 1000


class Command(BaseCommand):
    """Команда для импорта ингредиентов из CSV-файла."""

    @transaction.atomic
    def handle(self, *args, **options):
        """Обработка выполнения команды
        и импорт ингредиентов из CSV-файла."""

        with open('data/ingredients.csv') as f:
            reader = csv.reader(f)

            ingredients = []
            row_num = 0
            for row in reader:
                name, unit = row
                ingredients.append(Ingredient(name=name,
                                              measurement_unit=unit))

                row_num += 1
                if row_num % BATCH_SIZE == 0:
                    self.stdout.write('Импорт пакета ингредиентов...')
                    Ingredient.objects.bulk_create(ingredients,
                                                   ignore_conflicts=True)
                    ingredients = []

            if ingredients:
                Ingredient.objects.bulk_create(ingredients,
                                               ignore_conflicts=True)

        self.stdout.write(
            self.style.SUCCESS(
                'Ингредиенты успешно импортированы!'
            )
        )
