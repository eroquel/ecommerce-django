from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect

from .models import Product, ReviewRating
from ..category.models import Category
from myapps.carts.models import CartItem
from ..carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator #estas Clases son secesarioas para crear la páginación
from django.db.models import Q #Esta clase es para crear un buscador.
from .forms import ReviewForm
from ..orders.models import Order, OrderProduct #Para validar que quien hace un review, ya haya comprado el producto.

def store(request, category_slug = None):
    categories = None
    products = None

    if category_slug != None: #Si category_slug tiene un slug, es decir, si no es None ...
        categories = get_object_or_404(Category, slug = category_slug) # guarda en **categories** la categoria que tiene un slug igual al category_slug
        products = Product.objects.filter(category = categories, is_available = True)# Guarda en prodcuts todos los productos que tienen un **category** igual  **categories** y que esten disponibles.
        paginator = Paginator(products, 5) #Voy a paginar **products** con 5 productos cada página
        page = request.GET.get('page') #Aquí obtengo el parámetro **page** que colocaré en la URL y la guardo en **page**. En 'page' es que guardaré el número de la página a la cual accederé desde el navegador, ejemplo: ?/page=2, con esto accederé a la página 2
        paged_products = paginator.get_page(page)# pásale a **paginator** el parámetro 'page' y guárdalo en **paged_products**. En **paged_products** están los 5 productos.
        product_count = products.count() #Almacena en product_count la cantidad de productos guardados en **products**
    else: # category_slug no tiene nada
        products = Product.objects.all().filter(is_available = True) #guarda en **products** todos los productos disponibles.
        paginator = Paginator(products, 5) #Voy a paginar **products** con 5 productos cada página
        page = request.GET.get('page') #Aquí obtengo el parámetro **page** que colocaré en la URL y la guardo en **page**. En 'page' es que guardaré el número de la página a la cual accederé desde el navegador, ejemplo: ?/page=2, con esto accederé a la página 2
        paged_products = paginator.get_page(page)# pásale a **paginator** el parámetro 'page' y guárdalo en **paged_products**. En **paged_products** están los 5 productos.
        product_count = products.count() # Con la función count, estoy accediendo a la cantidad de productos en la base de datos.
    
    context = {
        'products': paged_products, #Antes se desplegaban todos los productos con **products** pero ahora se mostrará solo 5 con **paged_products**.
        'products_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug = category_slug, slug = product_slug) # aqui se están haciendo 2 condicionales
        """Entendiendo  **in_cart
        Esto no es para extraer algo de la BD, esto es solo para saber si el producto que estoy viendo en el detalle de prodcutos ya está agregado en el carrito,
        en otras palabras, quiero saber si el producto existe y la sesión existen en el CartItem. En in_cart, se almacenará un True o False, según sea el caso.
        **CartItem.objects.filter(cart__cart_id = _cart_id**, significa, busca dentro de CartItem, en el atributo cart, el cual es una llave foránea que te manda a la 
        tabla/entidad Cart y dentro de Cart busca un **id** igual a **_cart_id** 

        , product = single_product) también verifica si product si dentro de CartItem en el atributo **product** el cual es otra llave foránea, si existe un producto 
        Igual a single_product, si ambos son verdadero con el **exists()** devuelve un True.

        """
        in_cart =  CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:

        try:  #esto es para validar si el usuario compro o no el producto, y ni no lo compró no podrá hacer un review.
            orderedproduct = OrderProduct.objects.filter(user = request.user, product_id = single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderedproduct = None

    else:
        orderedproduct = None

    reviews = ReviewRating.objects.filter(product_id = single_product.id, status = True) #aquí estoy guardando en la variable **reviews** todos los reviews del producto actual.

    context ={
        'single_product': single_product,
        'in_cart': in_cart,
        'orderedproduct': orderedproduct,
        'reviews': reviews,
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

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER') #obtiene URL del navegador
    if request.method == 'POST':
        try: #Este Try es para acutalizar un review existen.
            reviews = ReviewRating.objects.get(user__id = request.user.id, product__id = product_id)# aquí se verifica si existe en **ReviewForm** un registro con un con el user_id  del usuario y un product_id del producto de donde se hace el review.
            form = ReviewForm(request.POST, instance=reviews)# Aquí se reemplaza el registro anterior por el nuevo que se manda por POST. Los campos del formulario que el usuario mandan al hacer un reviews, debe hacer un Match on lo descrito en ReviewForm, es decir, los nombres de los campos del formulario deben ser los mismos descritos den ReviewForm y de esta manera se captura la información y se almacena en la variable **form**
            form.save()
            messages.success(request, 'Gracias!, tu comentario ha sido actualizado')
            return redirect(url)
        except ReviewRating.DoesNotExist: #el except es para agregar un Review nuevo
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating() #Aquí se crea un nuevo objeto/instancia **ReviewRasting** **data* en la nueva instancia/objeto ReviewRating. Luego procedo agregarle los atributos para el nuevo registro.
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id =product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Muchas gracias, tu comentario ha sido enviado con éxito!')
                return redirect(url)


