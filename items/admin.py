from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Discount, Item, Order, Tax, Count


class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'description', 'price_in_usd', 'stripes_id'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'get_items', 'discount')

    def get_items(self, obj):
        return ', '.join([item.name for item in obj.items.all()])


class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'percentage', 'stripes_id')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'stripes_id')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class CountAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity')


admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Tax, TaxAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Count, CountAdmin)
admin.site.unregister(Group)
