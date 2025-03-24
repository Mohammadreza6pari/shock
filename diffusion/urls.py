from django.urls import path
from .views import DiffusionSetupView, DiffusionDownloadView

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
    path(
        'diffusions/download/<int:diffusion_id>/', 
        DiffusionDownloadView.as_view(), 
        name='diffusion-download'
    ),
]