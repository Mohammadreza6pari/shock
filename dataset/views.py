import os
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.files import File
from django.db import models

from user.permissions import IsApprovedUser


from .models import Dataset
from .serializers import DatasetSerializer
from diffusion.models import Diffusion
from django.conf import settings


class DatasetListView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedUser]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        datasets = Dataset.objects.filter(models.Q(user=user) | models.Q(user__isnull=True))
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)


class DatasetMetaView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedUser]

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
    permission_classes = [IsAuthenticated, IsApprovedUser]

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

class CreateDatasetFromDiffusionView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedUser]

    def post(self, request, diffusion_id):
        diffusion = Diffusion.objects.filter(id=diffusion_id, user=request.user).first()
        if not diffusion:
            return Response(
                {"error": "Diffusion not found or not owned by user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        io_csv_path = os.path.join(diffusion.output_folder_path, "io_table.csv")
        if not os.path.exists(io_csv_path):
            return Response(
                {"error": f"io_table.csv not found at {io_csv_path}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        dataset_name = f"diffusion_{diffusion.name}_{diffusion.id}"

        if Dataset.objects.filter(name=dataset_name, user=request.user).exists():
            return Response(
                {"error": "Dataset already exists for this diffusion."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        relative_path = os.path.relpath(io_csv_path, settings.MEDIA_ROOT)

        dataset = Dataset.objects.create(
            name=dataset_name,
            file=relative_path,
            user=request.user,
        )

        serializer = DatasetSerializer(dataset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)