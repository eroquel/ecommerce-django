from django.shortcuts import get_object_or_404, render

from .models import Product
from ..category.models import Category
from myapps.carts.models import CartItem
from ..carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator #estas Clases son secesarioas para crear la páginación
from django.db.models import Q #esta clase es para crear un buscador.

def store(request, category_slug = None):
    categories = None
    products = None

    if category_slug != None: #Si category_slug tiene un slug ...
        categories = get_object_or_404(Category, slug = category_slug) # guarda en **categories** la categoria que tiene un slug igual al category_slug
        products = Product.objects.filter(category = categories, is_available = True)# Guarda en prodcuts todos los productos que tienen un **category** igual  **categories** y que esten disponibles.
        paginator = Paginator(products, 5) #Voy a paginar **products** con 5 productos cada página
        page = request.GET.get('page') #Aqui obtengo el parametro **page** que colocaré en la URL y la guardo en **page**. en 'page' es que guardaré el numero de la página a la cual accederé desde el navegador, ejemplo: ?/page=2, con esto accederé a la página 2
        paged_products = paginator.get_page(page)# pasale a **paginator** el parametro 'page' y guardalo en **paged_products**. En **paged_products** están los 5 productos.
        product_count = products.count() #Almacena en product_count la cantidad de productos guardados en **products**
    else: # category_slug no tiene nada
        products = Product.objects.all().filter(is_available = True) #guarda en **products** todos los productos disponibles.
        paginator = Paginator(products, 5) #Voy a paginar **products** con 5 productos cada página
        page = request.GET.get('page') #Aqui obtengo el parametro **page** que colocaré en la URL y la guardo en **page**. en 'page' es que guardaré el numero de la página a la cual accederé desde el navegador, ejemplo: ?/page=2, con esto accederé a la página 2
        paged_products = paginator.get_page(page)# pasale a **paginator** el parametro 'page' y guardalo en **paged_products**. En **paged_products** están los 5 productos.
        product_count = products.count() # Con la función count, estoy accediendo a la cantidad de productos en la base de datos.
    
    context = {
        'products': paged_products, #antes se desplegaban todos los productos con **products** pero ahora se mostrará solo 5 con **paged_products**.
        'products_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug = category_slug, slug = product_slug) # aqui se están haciendo 2 condicionales
        """Entendiendo  **in_cart
        Esto no es para extraer algo de la BD, esto es solo para saber si el producto que estoy viendo en el detalle de prodcutos ya está agregado en el carrito,
        en otras palabras, quiero saber si el producto existe y la sesion existen en el CartItem. En in_cart, se almacenará un True o False, segun sea el caso.
        **CartItem.objects.filter(cart__cart_id = _cart_id**, significa, busca dentro de CartItem, en el atributo cart, el cual es una llave foranea que te manda a la 
        tabla/entidad Cart y dentro de Cart busca un **id** igual a **_cart_id** 

        , product = single_product) tambien verifica si product si dentro de CartItem en el atributo **product** el cual es otra llave foranea, si existe un producto 
        igual a single_product, si ambos son verdadero con el **exists()** devuelve un True.

        """
        in_cart =  CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
    except Exception as e:
        raise e
    
    context ={
        'single_product': single_product,
        'in_cart': in_cart,
    }

    return render(request, 'store/product_datail.html', context)

def search(request):
    products = 0
    products_count = 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains = keyword) | Q(product_name__icontains = keyword)) #Busca dentro de la tabla/entidad **Products** uno o más productos(elementos) que tengan en su propiedad/columna **description** y/o **product_name** la palabra clave en **keyword** y guárdalos en **products**.
            products_count = products.count()
    context = {
        'products': products,
        'products_count': products_count,
    }
    return render(request, 'store/store.html', context)