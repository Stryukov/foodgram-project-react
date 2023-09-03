import csv
from django.http import HttpResponse


def queryset_to_csv(ingredients_list):
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename="shoping_list.csv"'
        },
    )
    writer = csv.writer(response)
    writer.writerow(['Название', 'Количество', 'Ед. изм.'])
    writer.writerows(ingredients_list)
    return response
