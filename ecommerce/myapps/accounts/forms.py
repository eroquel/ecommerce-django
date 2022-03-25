from django import forms
from .models import Account #El modelo que creé para los diferentes usuarios, lo usaré en el form Registration

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingrese Password',
        'class': 'form-control',
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirmar Password',
        'class': 'form-control',
    }))

    class Meta:
        model = Account #Aquí es selecciono el modelo en el cual se basará el formulario, el cual será mi class Account, en la cual estan los campos que yo definí que necesitan todos los usuario
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password'] # aquí selecciono los campos que usará el Formulario de Registro para registrar nuevos usuarios.

    '''__init__
    Esta función es unicamente para trabajar con atributos el HTML, espesificamente, para agregar clases (estilos css) y placeholders. aquí se agregará la clase **form-control** 
    a cada campo generado por la clase RegistrationForm, el cual se recibe por contexto en el HTML como **form**. Tambien a cada campo se le agregará un Placeholder unico para cadoa uno.
    '''
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Ingrese su nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Ingrese su apellidos'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Ingrese su teléono'
        self.fields['email'].widget.attrs['placeholder'] = 'Ingrese su email'
        for field in self.fields:
            self. fields[field].widget.attrs['class'] = 'form-control'


    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean() #La funcion clean() se usa para validar campos de formularios. y creo cleaned para acceder a los campos del formulario, pero en este caso solo me interesa el campo password
        password = cleaned_data.get('password')# aquí accedo al campo password
        confirm_password = cleaned_data.get('confirm_password')# aquí accedo al campo confirm_password

        if password != confirm_password:
            raise forms.ValidationError(
                "El password no coincide!"
            )