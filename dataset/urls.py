from django.urls import path

from .views import DatasetDownloadView, DatasetListView, DatasetMetaView

urlpatterns = [
    path("", DatasetListView.as_view(), name="dataset-list"),
    path(
        "download/<identifier>/", DatasetDownloadView.as_view(), name="dataset-download"
    ),
    path("meta/<identifier>/", DatasetMetaView.as_view(), name="dataset-meta"),
]
