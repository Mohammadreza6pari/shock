from django.contrib import admin
from . models import Diffusion
from .tasks import run_diffusion

class DiffusionAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at', 'updated_at')

    def run_diffusion_action(self, request, queryset):
        for diffusion in queryset:
            run_diffusion(diffusion.id)

    actions = [run_diffusion_action]

admin.site.register(Diffusion, DiffusionAdmin)
