
from django.contrib import admin
from .models import ClothingCategory, ClothingItem, Outfit

@admin.register(ClothingCategory)
class ClothingCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ClothingItem)
class ClothingItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'color', 'brand', 'date_added', 'last_modified')
    list_filter = ('user', 'category', 'brand', 'color')
    search_fields = ('name', 'user__username', 'brand', 'notes')
    autocomplete_fields = ['user', 'category'] # Giúp tìm kiếm user và category dễ hơn

@admin.register(Outfit)
class OutfitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'updated_at')
    list_filter = ('user',)
    search_fields = ('name', 'user__username', 'description')
    filter_horizontal = ('clothing_items',) # Giao diện tốt hơn cho ManyToManyField
    autocomplete_fields = ['user']