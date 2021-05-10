from django.shortcuts import render
from .models import ProductCategory


def products(request):
    product_categories = ProductCategory.objects.all()[:4]

    context = {
        'title': 'Продукты',
        'links_menu': [
            {'href': 'mainapp:products', 'name': 'все'},
            {'href': 'mainapp:products', 'name': 'дом'},
            {'href': 'mainapp:products', 'name': 'офис'},
            {'href': 'mainapp:products', 'name': 'модерн'},
            {'href': 'mainapp:products', 'name': 'классика'},
         ],
        'categories': product_categories,
    }
    return render(request, 'products.html', context=context)


