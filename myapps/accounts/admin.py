from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile
from django.utils.html import format_html

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_link = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<div style="border-radius:50%; width:30px; height: 30px; overflow:hidden;" ><img src={} width="100%" ></div>'.format(object.profile_picture.url))
    
    thumbnail.short_description = 'Imagen de Perfil'
    list_display = ('thumbnail', 'user', 'state', 'country')

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
