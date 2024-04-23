from django.contrib import admin

# Register your models here.
from registry.models import Operator, Region, Range


class OperatorAdmin(admin.ModelAdmin):
    search_fields = ("name", "inn")
    list_display = ["name", "inn"]


class RegionAdmin(admin.ModelAdmin):
    search_fields = ("name",)


class RangeAdmin(admin.ModelAdmin):
    autocomplete_fields = [
        "operator",
        "region",
    ]
    search_fields = ("abc_def", "sn_from", "sn_to", "operator__name", "region__name")

    list_display = ["abc_def", "sn_from", "sn_to", "operator", "region"]
    save_on_top = True


admin.site.register(Operator, OperatorAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Range, RangeAdmin)
