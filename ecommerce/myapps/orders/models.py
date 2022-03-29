from django.db import models

from ..accounts.models import Account
from ..carts.models import Product
from ..store.models import Variation


# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE) #Esto crea una referencia netre la tabla Payment y Account y si eliminio una cuenta, es decir un usuario, se eliminará el payment.
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    creat_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (  #esto es un diccionario totalmente personalizado que he creado para ofrecer multiples opciones al atributo **status** en esta misma tabla
        ('New', 'Nuevo'),
        ('Accepted', 'Aceptado'),
        ('Completed', 'Completado'),
        ('Cancelled', 'Cancelado')

    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null = True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank = True, null = True)
    order_number =  models.CharField(max_length=20)
    first_name =  models.CharField(max_length=50)
    last_name =  models.CharField(max_length=50)
    phone =  models.CharField(max_length=50)
    email =  models.CharField(max_length=50)
    address_line_1 =  models.CharField(max_length=100)
    address_line_2 =  models.CharField(max_length=100)
    state =  models.CharField(max_length=50)
    city =  models.CharField(max_length=50)
    country =  models.CharField(max_length=50)
    order_note =  models.CharField(max_length=100, blank = True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=50, choices= STATUS, default='new')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null = True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    size = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
