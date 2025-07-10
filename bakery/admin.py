from django.contrib import admin
from .models import Category, BakeryItem, Order, OrderItem, Topping, Size, UserProfile


class BakeryItemInline(admin.TabularInline): 
    model = BakeryItem
    extra = 1  


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')
    inlines = [BakeryItemInline] 


@admin.register(BakeryItem)
class BakeryItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'category', 'formatted_price', 'available')
    list_filter = ('category', 'available')
    search_fields = ('name', 'description', 'ingredients')
    ordering = ('-price', 'name')  

    def formatted_price(self, obj):
        return f"Kshs {obj.price:.2f}"
    formatted_price.short_description = 'Price'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_total_price', 'status', 'created_at') 
    readonly_fields = ('get_total_price',)  
    inlines = [OrderItemInline]  

    def get_total_price(self, obj):
        return sum(item.total_price for item in obj.order_items.all())
    get_total_price.short_description = 'Total Price'  

admin.site.register(Order, OrderAdmin)

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_adjustment', 'serves')
    search_fields = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'phone_number')
    search_fields = ('user__username', 'phone_number')

@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_adjustment')
    search_fields = ('name',)