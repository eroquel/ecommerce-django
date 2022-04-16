from .models import Category


def menu_links(request):
    links = Category.objects.all()
    return dict(links = links) #dict es para retornar un diccionario con el valor de links