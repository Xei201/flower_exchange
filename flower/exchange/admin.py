from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Order, OrderItem, Flower, Lot, CustomUser


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Role user',  # group heading of your choice; set to None for a blank space instead of a header
            {
                'fields': (
                    'role',
                ),
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem


class LotItemInline(admin.TabularInline):
    model = Lot


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ("name", "shade")
    list_filter = ("name", "shade")
    inlines = [LotItemInline]


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ("salesman", "title", "slug", "amount", "unit_price", "hide")
    list_filter = ("salesman", "amount", "created", "hide")
    inlines = [OrderItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("buyer", "created", "description", "paid")
    list_filter = ("buyer", "created", "paid")
    inlines = [OrderItemInline]
