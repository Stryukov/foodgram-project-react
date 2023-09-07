import json
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON файла.'

    def add_arguments(self, parser):
        parser.add_argument('--file_path')

    def handle(self, *args, **options):
        file_path = options['file_path']
        if not file_path:
            raise CommandError("Укажите путь к JSON файлу")

        self.import_ingredients_from_json(file_path)

    def import_ingredients_from_json(self, file_path):
        with open(file_path, 'r') as file:
            ingredients_data = json.load(file)

        ingredients = [
            Ingredient(
                name=data['name'], measurement_unit=data['measurement_unit']
            )
            for data in ingredients_data
        ]

        Ingredient.objects.bulk_create(ingredients)
