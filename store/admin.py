from django.contrib import admin
from .models import Category, Product, Order, OrderItem, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price', 'get_cost']

    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Cost'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available']
    list_filter = ['available', 'category']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'paid', 'created', 'get_total_cost']
    list_filter = ['status', 'paid', 'created']
    list_editable = ['status', 'paid']
    inlines = [OrderItemInline]
    readonly_fields = ['created', 'updated']

    def get_total_cost(self, obj):
        return f'₹{obj.get_total_cost()}'
    get_total_cost.short_description = 'Total'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city']
