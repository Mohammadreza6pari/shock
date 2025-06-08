from django.urls import path
from .views import DatasetListView, DatasetDownloadView

urlpatterns = [
    path('', DatasetListView.as_view(), name='dataset-list'),
    path('download/<identifier>/', DatasetDownloadView.as_view(), name='dataset-download'),
]