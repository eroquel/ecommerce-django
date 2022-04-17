from django.contrib import admin
from .models import Product, Variation, ReviewRating


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

class Variationadmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category','variation_value', 'is_active',)
    list_editable = ('is_active', 'variation_category', 'variation_value',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active',)

class ReviewRatingadmin(admin.ModelAdmin):
     list_display = ('product', 'user','rating', 'crated_at', 'updated_at')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, Variationadmin)
admin.site.register(ReviewRating, ReviewRatingadmin)
