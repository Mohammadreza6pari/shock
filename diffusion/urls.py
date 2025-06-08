from django.urls import path
from .views import DiffusionSetupView, DiffusionDownloadView

urlpatterns = [
    path(
        '',
        DiffusionSetupView.as_view(), 
        name='diffusion-list-create'
    ),
    path(
        '<int:diffusion_id>/', 
        DiffusionSetupView.as_view(), 
        name='diffusion-detail'
    ),
    path(
        'download/<int:diffusion_id>/', 
        DiffusionDownloadView.as_view(), 
        name='diffusion-download'
    ),
]