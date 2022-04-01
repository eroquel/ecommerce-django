import datetime
from django.http import JsonResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from ..carts.models import CartItem
from ..store.models import Product
from .forms import OrderForm
from .models import Order, OrderProduct, Payment, OrderProduct
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.

def payments(request):
    body = json.loads(request.body) #Aquí lo que recibo es un Json por POST. **json.loads()** me permite recibir e interpretar el Json para poder usarlo.
    order = Order.objects.get(user=request.user, is_ordered=False, order_number = body['orderID']) # aquí obtengo el **Order** exacto que corresponde al registro Payment que voy a crear. Nota orderID en realidad es **order.order_number**

    payment = Payment(
        user = request.user, #accedo al usuario acutal
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payment.save() #aquí hago el registro en la base de datos

    order.payment = payment #Aquí hago la vinculación entre Order y Payment, recordando que order tiene un atributo el cual es una llave foránea de Payment.
    order.is_ordered = True #cambio el estado de la orden que antes era False y ahora es True, para indicar que la orden fue realizada
    order.save()

    #Mover todos los items del carrito a la tabla OrderProduct:
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation) #al hacer esto, en el admin aparaeceran seleccionadas las variaciones que el comprador seleccionó
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    CartItem.objects.filter(user=request.user).delete()

    '''
    Enviar correo de confirmación de compra:
    '''
    mail_subject = 'Gracias por tu compra'
    body = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })

    to_email =request.user.email
    send_email = EmailMessage(mail_subject, body, to=[to_email])
    send_email.send()

    '''
    La función **pyament** no retorará una plantilla si no, un **JasonResponse** con un objeto lladamado **data**
    a la fucion de Paypal que procesa el pago utilizando, y recibirá a **data** gracias al objeto **then**:
    '''
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id
    }

    return JsonResponse(data)
    



def place_order(request, total = 0, quantity = 0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count() # para saber la cantidad de elementos que tienen el carrito de compras

    if cart_count <=0:
        return redirect('store')

    grant_total = 0
    tax = 0 

    for cart_item in cart_items:
        total +=(cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total)/100
    grant_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            print('***********************eentroooo****************')
            data = Order() #Order es la entidad/clase que esta en el models.py
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grant_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            '''
            Cada orden de compras debe tener un **order_number** único y este se creará usando la fecha de la orden y el **id** del registro/record de dicha orden.
            '''
            current_year = int(datetime.date.today().strftime('%Y'))
            current_month = int(datetime.date.today().strftime('%m'))
            current_day = int(datetime.date.today().strftime('%d'))
            current_date_row= datetime.date(current_year, current_month, current_day) #aqui genero la fecha actual, pero esta se crea con el slash "/": 2022/03/27
            current_date = current_date_row.strftime("%Y%m%d") #Quí le quito el "/", este es el formato final: 20220327
            '''
            #el valor id de una tabla/entidad se obtiene únicamente luego después de crear el record/registro en la base de datos, por esa razone esta últimas líneas de
            códigos se crearon luego del **data.save** así, se crea el record, por tanto el id y de esta manera accedo al id para concatenarlos con la fecha y
            crear el numero de orden. Al tener el número de orden precedo a hacer el registro de deste en la tabla. Ojo  **data** es la entidad/tabla/orden con la que estoy trabajando
            '''
            order_number = current_date + str(data.id) 
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number = order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grant_total,
            }

            return render(request,'orders/payments.html', context)

        else:
            print('******************problema con el form*********************')
    else:
        return redirect('checkout')

def order_completed(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order =Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price*i.quantity

        payment =Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_completed.html', context)
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
