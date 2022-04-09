from distutils.command.upload import upload
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class MyAccountManager(BaseUserManager): #Esta clase es la que creará un nuevo nuevo usario y un "Super Admin Usuarios" y lo almacenará en la base de datos en la tabla creada por el Modelo(clase) Account. Esta Clase MyAccountManager será instanciada desde la clase **Account**.
    def create_user(self, first_name, last_name, email, username, password = None): #este metodo es para crear un usuario básico
        if not email:
            raise ValueError('El usuario debe tener un email')
        
        if not username:
            raise ValueError('El usuario debe tener un username')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password = None): #Este Metodo es para crear un super usuario.
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using = self._db)
        return user


class Account(AbstractBaseUser): # en esta clase (modelo) se definen los campos para la tabla usuarios, los campos necesarios para crear un usuario nuevo:
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)

    #cambos que Ddjango necesita por defecto, estos son obligatorios:
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email' #aquí le digo a Django que el nombre de usuario será el correo
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name'] #Estos deben ser campos obligatorios al momento de crear un superuser desde la consola.

    objects = MyAccountManager() #Objects, será una instancia de MyAccountManager. Agrego a aquí este Objcts para crear nuevos usuario, ya que así, se almacenarán en la tabla Account creado por el modelo Account.

    def full_name(self):
        return f'{self.first_name} {self.last_name}'


    def __str__(self):
        return self.email

    def has_perm(self, permission, obj=None): # Este metodo/función interna de Django y es para indicar si el usario tiene o no permiso de Administrador, retornará segun lo almacenado en "is_admin, lo cual puede ser True o False."
        return self.is_admin
    
    def has_module_perms(self, add_label):# Este metodo/función interna de Django y es para indicar que si tiene permiso de administrador, puede acceder a todos los modulos. Ojo, 
        return True

class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    profile_picture = models.ImageField(blank = True, upload_to='user_profile')
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'