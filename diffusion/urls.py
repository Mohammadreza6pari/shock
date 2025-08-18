from django.urls import path
from .views import DiffusionSetupView, DiffusionDownloadView, DiffusionIterationDetailView

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
    path(
        '<int:diffusion_id>/iterations/', 
        DiffusionIterationDetailView.as_view(), 
        name='diffusion-iteration-detail'
    ),
]