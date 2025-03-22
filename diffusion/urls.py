from django.urls import path
from .views import DiffusionSetupView

urlpatterns = [
    path(
        'diffusions/',
        DiffusionSetupView.as_view(), 
        name='diffusion-list-create'
    ),
    path(
        'diffusions/<int:diffusion_id>/', 
        DiffusionSetupView.as_view(), 
        name='diffusion-detail'
    ),
]