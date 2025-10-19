from django.urls import path

from .views import DatasetDownloadView, DatasetListView, DatasetMetaView, CreateDatasetFromDiffusionView

urlpatterns = [
    path("", DatasetListView.as_view(), name="dataset-list"),
    path(
        "download/<identifier>/", DatasetDownloadView.as_view(), name="dataset-download"
    ),
    path("meta/<identifier>/", DatasetMetaView.as_view(), name="dataset-meta"),
    path("from-diffusion/<int:diffusion_id>/", CreateDatasetFromDiffusionView.as_view(), name="create-dataset-from-diffusion"),
]
