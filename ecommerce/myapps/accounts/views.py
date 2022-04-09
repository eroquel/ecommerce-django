from django.shortcuts import get_object_or_404, redirect, render

from ..accounts.forms import RegistrationForm, UserForm, UserProfileForm
from django.contrib import messages, auth #**messages** para poder usar el maquete que me permite imprimier mensajes y alertas en el frontend
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage

from .models import Account, UserProfile # **Acount** es el modelo/entidad donde insertaré (base de datos) la información recopilada en el formulario **from**
from ..orders.models import Order
from ..carts.views import _cart_id, cart
from ..carts.models import Cart, CartItem
import requests

def register(request):
    form = RegistrationForm() #esto es para inicializar el formulario y evitar un error en caso de que la validación del POST devuelva False.
    #print(request.POST)
    if request.method == 'POST': #Si la información del formulario **register** es enviada por el método POST (dentro del objeto request) y por eso, lo primero que debo hacer es validar si mi views/function **register** estoy recibiendo algo por POST
        form = RegistrationForm(request.POST) #Instanciar un objeto llamado form (creado por mi) usando la clase RegistrationForm la cual recibe por parámetro la información del formulario enviada por POST.
        if form.is_valid(): #Si el formulario es válido captura los datos que envía el cliente. **is_valid()** Esta es una función reservada de del objeto **form** importada from django import forms** en el forms.py. Se usa para para validar formularios que devuelve un booleano, es decir, True o False.
            print('pasó la validación')
            first_name = form.cleaned_data['first_name']#cleaned_data[] tambien propia del objeto form (de Django al igual que is_valid()) se usa para normalizar la data recibida en un campo determinado, ayuda a evitar errores
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0] #como está definido en el mi clase Account/entidad, todo usuario debe tener un nombre de usuario, pero este campo no está en mi formulario register, en esta ocasión auto generaré dicho campo y usaré el correo. Primero dividiré el correo en según el @ y solo tomaré lo que está antes del @ usando la función de Python **split**.
            user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, password = password, username = username ) #   Generando/no creando, un nuevo usuario
            user.phone_number = phone_number # como este la propiedad/campo phone_number no fue agregada el mi función **create_user** al crear mi modelo/entidad Account, pero si es una propiedad de me Account, debo agregarlo de esta manera. 
            user.save() #esta es la función que guarda este nuevo record/usuario en la base de datos. Ojo, esto sucederá luego de la validación hecha por **is_valid()** la cual devuelve True, es decir, si es válido.
            
            profile = UserProfile() #Aquí estoy instanciando un nuevo objeto UserProfile() y luego le agrego al atributo **user** el user.id del usuario que acabo de registra. Así enlazo la cuenta (Account) con su perfil (UserProfile)
            profile.user_id = user.id
            profile.profile_picture = 'default/default-image-profile-user.jpg' #imagen por defecto para todos los nuevos usuarios
            profile.save()
            
            '''Enviar correo para la activación
            El siguiente es el código para enviar el correo de activación para el nuevo usuario
            '''
            current_site = get_current_site(request) #obtén la url de la página acutal.
            mail_subject = 'Por favor activa tu cuenta de PapiShop'# este será el subject del email.
            body =  render_to_string('accounts/account_verification_email.html', { # este será el cuerpo del correo
                'user': user, #envio el objeto user para poder acceder el nombre, y otras informaciones del usuario.
                'domain': current_site, #la página actual.
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), #necesito mandar el user id en el correo, pero por temas de seguiriad debo codificarlo .
                'token': default_token_generator.make_token(user),# generará un token que represente al mensaje (correo) y se basará en el objeto **user** user es el usuario que estoy creando
            })
            to_email = email #Es el correo del nuevo usuario al cual le manaré el correo de verificación.
            send_email =  EmailMessage(mail_subject, body, to=[to_email]) #este es el objeto que procesara el correo.
            send_email.send() #envía el correo
            
                        
            #messages.success(request, 'El usuario ha sido registrado con éxito')# este mensaje es el que se mostrará en la página de registro
            return redirect('/accounts/login/?command=verification&email='+email)# cuando login reciba estos parámetros, ocultará el formulario y mostrará un mensaje de revisa tu creo para activar tu cuenta
          
 
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    #print(request.POST)
    if request.method == 'POST': # si la función login recibe un request por el método POST has lo siguiente
        
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email = email, password = password) #Aquí es que se verifica si existe un usuario en la base de datos con el mismo email y la contraseña que se manda por el formulario de login, usando la función **authenticate**

        if user is not None: #si user no es nulo, ha lo siguiente
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists() #esto lo que almacena es un boleano.
                if is_cart_item_exists:
                    '''
                    Comparando las variaciones de los productos agregados si haber hecho inicio de sesion y las variaciones luego de haber hesho sesion, para hacer un merge de los prodcutos
                    cuyas variacioens son las mismas y en vez de crear un CartItem, solo se le sume el varlo 1 para aumentar la cantidad.
                    '''
                    cart_item = CartItem.objects.filter(cart = cart) #en cart_item se almacena un arreglo con todos los cart items disponibles
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation)) #aquí almacenará todos las variaciones de los productos agregados sin haberse autenticado

                    cart_item = CartItem.objects.filter(user = user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation= item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list: #si hay alguna coincidencia entre las variaciones de product_variation y exists_variation_lis
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else: #si no hay coincidencias
                            cart_item = CartItem.objects.filter(cart = cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            #http://127.0.0.1:8000/accounts/login/?next=/cart/checkout/
            auth.login(request, user) #has el login con la información que está en user
            messages.success(request, 'Has iniciado sesión exitosamente')

            url = request.META.get('HTTP_REFERER') #obtiene URL del navegador
            #print(url)
            try:
                query = requests.utils.urlparse(url).query #aquí capturo todos los parámetros de la URL, todos los que vienen después del signo **?**, en este caso solo tengo el parametro **netx**
                #?next=/cart/checkout/
                print(query)
                params = dict(x.split('=') for x in query.split('&')) # lo que guardará params es: {'next': '/cart/checkout/'}
                #print(params)
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')

            return redirect('dashboard')# redirecciona al usuario al home
        else:
            messages.error(request, 'El nombre de usuario o la contraseña es incorrecta')

    return render(request, 'accounts/login.html')

@login_required(login_url = 'login') #esto es para que la función logout solo funciones si primero se hizo login. Hay que este decorador.
def logout(request):
    auth.logout(request)
    messages.success(request, 'Has cerrrado la sesión')
    return redirect('login')

def activate(request, uidb64, token): #activa la cuenta del usuario vía correo
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Tu cuenta fue activada con éxito.')
        return redirect('login')
    else:
        messages.error(request, 'La activación fue invalida')
        return redirect('register')


@login_required(login_url=login)
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered = True) #Almacena en la variable **order** todos los registros de las ordenes realizadas por el usuario
    orders_count = orders.count() #almacena en **orders_count** el numero total de las ordenes realizadas
    context = {
        'orders_count': orders_count,
    }
    return render(request, 'accounts/dashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        
        if Account.objects.filter(email = email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Resetear Password'
            body = render_to_string('accounts/reset_password_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()

            messages.success(request,'Un email fue enviado a tu bandeja de entrada para resetear tu contrasena')
            return redirect('login')
        else: 
            messages.error(request, 'La cuenta de usuario no existe')
    
    return render(request, 'accounts/forgotPassword.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Por favor resetea tu contraseña')
        return redirect('reset_password')
    else:
        messages.error(request, 'El link ha expirado')
        return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk = uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'La contraseña fue reseteada correctamente')
            return redirect('login')
        else:
            messages.error(request, 'La contraseña no concuerda')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')


def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url=login)
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST': #Este **if** es para agregar o modificar la información del perfil, el **Else** es para desplegar la información ya registrada.
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Su información fue guarada con éxito")
            return redirect('edit_profile')
    
    else: #Si no recibo el formulario por POST al disparar **edit_profile()** solicita la data registrada en **UserForm** y **UserProfileForm** para luego mandarla por un contexto y mostrarla en el template
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
    }

    return render(request, 'accounts/edit_profile.html', context)
