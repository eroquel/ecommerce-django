from django.db import models
from django.utils import timezone
from myapps.accounts.models import Account
from ..store.models import Product, Variation

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True) #en este atributo se almacenaran las sesiones/cookies
    date_added = models.DateField(auto_now_add = True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True) #**variations** almacenará un colección de data, en este caso un conjunto de variations de la entidad **Variation**, y para esto es que usamos la clase: **ManyToManyField**ManyToManyField**
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
   #created_at = models.DateTimeField(auto_now_add=True, default=timezone.now) al crear un created_at en una entidad que ya había sido creada, a todos sus registors anteriores hay que ponerles una fecha por defecto, en este caso es la feha acutal, es decir, que un campo creado la semana pasasa dirá que fué creado hoy, ya que created_at lo agregúe hoy.

    def sub_total(self): #aqui creo este atributo el cual surge de la multipicación otros dos atributos
        return self.product.price * self.quantity

    """
    En este caso uso __unicode__ porque usar __str__ probocaba un error en la administración, devolviendo un Objecte en vez de un string.
    esto elimina el error, pero deja de mostrar el nombre de cada objeto/registro, pero esto se resuelve al agregar el **list_display** en el
    archivo admin.py e indicuando que quiero mostrar es a **product**.
    """
    def __unicode__(self): 
        return self.product
