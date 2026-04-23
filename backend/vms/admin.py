from django.contrib import admin

from .models import VirtualMachine


@admin.register(VirtualMachine)
class VirtualMachineAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "host",
        "port",
        "protocol",
        "is_active",
        "current_user",
        "last_used_at",
    )
    list_filter = ("protocol", "is_active")
    search_fields = ("name", "host")
