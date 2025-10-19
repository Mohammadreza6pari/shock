from django.urls import path

from .views import DatasetDownloadView, DatasetGroupingView, DatasetListView, DatasetMetaView, CreateDatasetFromDiffusionView, DatasetDetailView

urlpatterns = [
    path("", DatasetListView.as_view(), name="dataset-list"),
    path("<int:pk>/", DatasetDetailView.as_view(), name="dataset-detail"),
    path(
        "download/<identifier>/", DatasetDownloadView.as_view(), name="dataset-download"
    ),
    path("meta/<identifier>/", DatasetMetaView.as_view(), name="dataset-meta"),
    path("group/", DatasetGroupingView.as_view(), name="dataset-group"),
    path("from-diffusion/<int:diffusion_id>/", CreateDatasetFromDiffusionView.as_view(), name="create-dataset-from-diffusion"),
]
