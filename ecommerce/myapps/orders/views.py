import datetime
from django.shortcuts import redirect, render
from ..carts.models import CartItem
from .forms import OrderForm
from .models import Order

# Create your views here.

def payments(request):
    return render(request, 'orders/payments.html')

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
            #el valor id de una tabla/entidad se optiene unicamente luego despues de crear el record/registro en la base de datos, por esa razone sta utimas lineas de
            codigos se crearon luego del **data.save** así, se crea el record, por tanto el id y de esta manera accedo al id para concatenarlos con la fecha y
            crear el numero de orden. Al tener el numero de ordern precedo a hacer el registro de deste en la tabla. Ojo  **data** es la entidad/tabla/orden con la que estoy trabajando
            '''
            order_number = current_date + str(data.id) 
            data.order_number = order_number
            data.save()
            return redirect('checkout')
        else:
            print('******************problema con el form*********************')
    else:
        return redirect('checkout')