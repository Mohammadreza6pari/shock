from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Dataset
from .serializers import DatasetSerializer


class DatasetListView(APIView):
    def get(self, request):
        datasets = Dataset.objects.all()
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)


class DatasetMetaView(APIView):
    def get(self, request, identifier):
        dataset = (
            Dataset.objects.filter(id=identifier).first()
            or Dataset.objects.filter(name=identifier).first()
        )
        if not dataset:
            return Response({"error": "Dataset not found"}, status=404)

        meta = dataset.extract_countries_and_industries()
        return Response(meta)


class DatasetDownloadView(APIView):
    def get(self, request, identifier):
        dataset = (
            Dataset.objects.filter(id=identifier).first()
            or Dataset.objects.filter(name=identifier).first()
        )
        if not dataset:
            return Response({"error": "Dataset not found"}, status=404)
        return FileResponse(
            dataset.file.open("rb"), as_attachment=True, filename=dataset.name
        )
