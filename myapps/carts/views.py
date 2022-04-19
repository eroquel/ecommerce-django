from django.shortcuts import get_object_or_404, redirect, render
from ..store.models import Product, Variation
from ..carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

"""¿Cómo funciona?: **_cart_id: Crear y verificar sesiones de usuarios no registradoss**
 Esta función es solo para validar si existe un sesion (cookie) "creada en el explorador" y si no existe creará una nueva
 para el usario. Esta session/cookie es para identificar a los usuario no logeados o no registrados.
 "_"Se pone un underScore primero en el nombre para indicar que es una funcion privada, por tanto sólo se puedrá
 acceder a esta desde este archivo, es decir, desde el archivo donde es declarada."""
def _cart_id(request): 
    cart = request.session.session_key #Verifica si existe una session/cookie/sessionID
    if not cart: #si no
        cart = request.session.create() # Crea una session/cookie/sessionID en el navegador para identificar al usuario
    return cart


"""**add_cart**: Agregar un producto a la sesión del usuario/carrito de compras
Esta función se disparará cuando el usuario hace click al boton **Agregar Prodcuto** o al darle click al boton de **+** 
para aumentar la cantidad desde la sección cart. Esto  desencanenarará todo lo que se muestra en este archivo. Tambien
Con esta función se creará el carrito(session/cookie) para cada usuario.
"""
def add_cart(request, product_id): 
    """Sobre el parametro **product_id** 
    por el Parametro product_id llegarán los **id** que se envien a esta función, ejemplo: {% url 'add_cart' cart_item.product.id %}
    Nota: lo que recibe prodcut_id como parametro es: ***cart_item.product.id*** es decir el id del producto. Al recibir el id del product y verificarse en 
    el try que existe junto con el cart (session/cookie), lo unico que hará la función es aumentar por **1** el quantity y al aumentar
    el quantity se recarculan los totales. Si no existiera un product id relacionado con un cart/session/cookie, agregaría el producto al cart, ejemplo, si el producto 
    no ha sido acregado y se agrega desde el detalle del producto: {% url 'add_cart' single_product.id %}
    """
    product = Product.objects.get(id = product_id) #Busca dentro de Prodcuto un producto con el id  que se recibe por parametro por el ***product_id***

    current_user = request.user

    if current_user.is_authenticated:

        product_variation = [] #solo para inicializar/declarar.

        if request.method == 'POST':#Para sabner si me estan mandando los parametros por el metodo POST
            for item in request.POST:
                key = item #item representea el nombre del variation dentro de POST.
                value = request.POST[key] #**value** el el valor que tiene cada **key** (variation en este caso).

                try: #verificar si este variation existen dentro de la colección dentro de la base de datos
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
      
        is_cart_item_exists = CartItem.objects.filter(product = product, user=current_user).exists()

        if is_cart_item_exists: # Este if (antes era un try) es para agrear un elemento al aun carrito existente carrito , es decir, Crear un **cart_item** a un **cart** existente, como se muestra a continuación.
            cart_item = CartItem.objects.filter(product = product, user = current_user) #busca en **CartItem** un cartItem que cumpla con los parametros recibidos y guardalo en **cart_item**.
            
            ex_var_list = [] #aqui se almacenaran todos los variations ejemplo: [<Variation: color:rojo>, <Variation: talla:large>], [<Variation: color:negro>, <Variation: talla:Medium>] estas son 2 listas porque son de un mismo productos pero con Variatoins diferentes.
            id = []
            for item in cart_item:
                existing_variation = item.variations.all() 
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            # my_object = ex_var_list
            # return render (request, 'store/cart.html', {'my_object': my_object,})
            
            if product_variation in ex_var_list: #este if es para verificar si el product variation que mandé por POST existe en **ex_var_list**ex_var_list (la base de datos)
                index = ex_var_list.index(product_variation) #dentro de **ex_var_list** busca el index que tenga el contenido que hay en **product_variation**
                item_id = id[index]
                item = CartItem.objects.get(product = product, id = item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product = product, quantity = 1, user = current_user)
                if len(product_variation) > 0: # si la cantidad de elementos en **product_variation** es mayor a 0, es decir, si tiene algun valor...
                        item.variations.clear()#Limpia todos los variations que puedan exister dentro del cart_item, para que a continuación agrege los que estan agregando el usuario.
                        item.variations.add(*product_variation)
                item.save
            
        else: # Si producto no existe, el cart_id registra ese producto en CartItem con ese cart_id y a quantity ponele 1.

            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0: # si la cantidad de elementos en **product_variation** es mayor a 0, es decir, si tiene algun valor...
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save() #Guarda el producto, cantidad y el cart.

        return redirect('cart') #al finalizar, redirecciona a página cart

    
    else:
        product_variation = [] #solo para inicializar/declarar.

        if request.method == 'POST':#Para sabner si me estan mandando los parametros por el metodo POST
            for item in request.POST:
                key = item #item representea el nombre del variation dentro de POST.
                value = request.POST[key] #**value** el el valor que tiene cada **key** (variation en este caso).

                try: #verificar si este variation existen dentro de la colección dentro de la base de datos
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        try: #Este try es para crear un cart, pero primiero verifica si ya existe un card_id/session, si no, en el except se creara uno nuevo con un cart_id nuevo.
            cart = Cart.objects.get(cart_id = _cart_id(request)) # ¿existe en este cart_id en **Cart**?, es decir ¿en la tabla Cart hay una session/cookie igual instalada en el navegador del usuairo, es decir **_cart_id**?
        except Cart.DoesNotExist: #si lo anterior no es verdadero, crea un nuevo record con el _cart_id y guardalo en el abtributo de la tabla Cart, es decir en ***cart_id***
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save() #guardar el nuevo cart_id, es decir, la nueva session/cookie en Cart.cart_id


        
        is_cart_item_exists = CartItem.objects.filter(product = product, cart = cart).exists()

        if is_cart_item_exists: # Este if (antes era un try) es para agrear un elemento al aun carrito existente carrito , es decir, Crear un **cart_item** a un **cart** existente, como se muestra a continuación.
            cart_item = CartItem.objects.filter(product = product, cart = cart) #busca en **CartItem** un cartItem que cumpla con los parametros recibidos y guardalo en **cart_item**.
            
            ex_var_list = [] #aqui se almacenaran todos los variations ejemplo: [<Variation: color:rojo>, <Variation: talla:large>], [<Variation: color:negro>, <Variation: talla:Medium>] estas son 2 listas porque son de un mismo productos pero con Variatoins diferentes.
            id = []
            for item in cart_item:
                existing_variation = item.variations.all() 
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            # my_object = ex_var_list
            # return render (request, 'store/cart.html', {'my_object': my_object,})
            
            if product_variation in ex_var_list: #este if es para verificar si el product variation que mandé por POST existe en **ex_var_list**ex_var_list (la base de datos)
                index = ex_var_list.index(product_variation) #dentro de **ex_var_list** busca el index que tenga el contenido que hay en **product_variation**
                item_id = id[index]
                item = CartItem.objects.get(product = product, id = item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product = product, quantity = 1, cart = cart)
                if len(product_variation) > 0: # si la cantidad de elementos en **product_variation** es mayor a 0, es decir, si tiene algun valor...
                        item.variations.clear()#Limpia todos los variations que puedan exister dentro del cart_item, para que a continuación agrege los que estan agregando el usuario.
                        item.variations.add(*product_variation)
                item.save
            
        else: # Si producto no existe, el cart_id registra ese producto en CartItem con ese cart_id y a quantity ponele 1.

            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0: # si la cantidad de elementos en **product_variation** es mayor a 0, es decir, si tiene algun valor...
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save() #Guarda el producto, cantidad y el cart.

        return redirect('cart') #al finalizar, redirecciona a página cart
    

"""¿Cómo funciona?: **remove_cart** Reducir la cantidad de productos repetidos agregados en el carrito.
esta funcion disminuye la cantidad de los productos agreagados al carrito. Para que esto funcione debo recordar
que tanto **add_cart** como **remove_cart** deben ser registrados den el el archivo url.py ya que la solicitud
para la ejecucion de estas funciones llegan por la URL
"""
def remove_cart(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id = product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = product, user = request.user, id = cart_item_id)
        else:
            cart = Cart.objects.get(cart_id  = _cart_id(request))
            cart_item =  CartItem.objects.get(product = product, cart = cart, id = cart_item_id)

        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return  redirect('cart')
"""remove_cart_item: Eliminar elementos del cartito/base dedatos"""
def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id = product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product = product, user = request.user, id = cart_item_id)
    else:
        cart =  Cart.objects.get(cart_id = _cart_id(request))    
        cart_item = CartItem.objects.get(product = product, cart = cart, id = cart_item_id)
    cart_item.delete()
    return redirect('cart')


"""Nota informativa:
Siempre es recomendable hacer un **try** para verificar que lo que se recive es correcto y usar un except para una alternativa.
"""
def cart(request, total = 0, quantity = 0, cart_items = None): #Esta funcion se dispara cuando en la url aparece mitienda.com/cart.
    tax = 0
    grand_total = 0
    try:#Intenta comprobar si todo en este try devuelve True
        if request.user.is_authenticated: #Si el usuario está atenticado, es decir, si el usuario inició sesión...
            cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request)) #Extrae dentro de Cart un Cart_id igual al comprobado en la función _cart_id().
            cart_items = CartItem.objects.filter(cart = cart, is_active = True) #Busca dentro de CartItem un cart igual al **cart comprobado en la linea anterior** y que esté activo.

        
        for cart_item in cart_items: #Este bucle es para conseguir los totales del costo de todos los prodcutos y de la cantidad total de productos en el carrito
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100 #suponiendo que el impuesto es de un 2%.
        grand_total = total + tax #grand_total es el total final.
    except ObjectDoesNotExist: # si no existe, solo ignorara la excepción.
        pass 

    context = { #aquí creo el contexto para paserle a la plantilla todos los valores obtenidos de la BD
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,

    }

    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total = 0, quantity = 0, cart_items = None):
    tax = 0
    grand_total = 0
    try:#Intenta comprobar si todo en este try devuelve True
        if request.user.is_authenticated: #Si el usuario está atenticado, es decir, si el usuario inició sesión...
            cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request)) #Extrae dentro de Cart un Cart_id igual al comprobado en la función _cart_id().
            cart_items = CartItem.objects.filter(cart = cart, is_active = True) #Busca dentro de CartItem un cart igual al **cart comprobado en la linea anterior** y que esté activo.
        
        for cart_item in cart_items: #Este bucle es para conseguir los totales del costo de todos los prodcutos y de la cantidad total de productos en el carrito
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100 #suponiendo que el impuesto es de un 2%.
        grand_total = total + tax #grand_total es el total final.
    except ObjectDoesNotExist: # si no existe, solo ignorara la excepción.
        pass 

    context = { #aquí creo el contexto para paserle a la plantilla todos los valores obtenidos de la BD
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,

    }

    return render(request, 'store/checkout.html', context)
