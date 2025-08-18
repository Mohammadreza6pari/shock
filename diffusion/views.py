from rest_framework import views
from . import models, serializers
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import views, status
import shutil
from django.http import HttpResponse
from .utils import create_zip_file_of_folder
import os
import csv

class DiffusionSetupView(views.APIView):
    serializer_class = serializers.DiffusionSerializer


    def post(self, request):
        """Create a new diffusion record."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        diffusion = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, diffusion_id=None):
        """Retrieve a single diffusion record or list all diffusions."""
        if diffusion_id:
            diffusion = get_object_or_404(models.Diffusion, id=diffusion_id)
            serializer = self.serializer_class(diffusion)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        diffusions = models.Diffusion.objects.exclude(status="deleted")
        serializer = self.serializer_class(diffusions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, diffusion_id):
        diffusion = get_object_or_404(models.Diffusion, id=diffusion_id)

        if diffusion.status not in ["failed", "finished"]:
            return Response(
                {"error": "Diffusion can only be deleted if it has failed or finished."},
                status=status.HTTP_400_BAD_REQUEST
            )

        output_path = diffusion.output_folder_path
        shutil.rmtree(output_path, ignore_errors=True)
  
        diffusion.status = "deleted"
        diffusion.save()
  
        return Response({"message": "Diffusion deleted"}, status=status.HTTP_200_OK)
    

class DiffusionDownloadView(views.APIView):
    def get(self, request, diffusion_id):
        """Generate a ZIP file of diffusion output and return it as a download"""
        diffusion = get_object_or_404(models.Diffusion, id=diffusion_id)
        create_zip_file_of_folder(diffusion.output_zip_file_path, diffusion.output_zip_file_name)

        zip_path = diffusion.output_zip_file_name

        with open(zip_path, "rb") as zip_file:
            response = HttpResponse(zip_file.read(), content_type="application/zip")
            response["Content-Disposition"] = f'attachment; filename="{zip_path}"'
        
        os.remove(zip_path)
        
        return response


class DiffusionIterationDetailView(views.APIView):
    def post(self, request, diffusion_id):
        data = request.data

        country_groups = data.get('country_groups', [])
        group_all_industries = data.get('group_all_industries', False)
        filters = data.get('filters', {})

        industries = filters.get('industries', [])
        countries = filters.get('countries', [])
        grouped_countries = filters.get('grouped_countries', [])
        limit_largest_shocks = filters.get('limit_largest_shocks', 5)

        diffusion = get_object_or_404(models.Diffusion, id=diffusion_id)

        is_ok, result = diffusion.process_logs(
            limit_largest_shocks=limit_largest_shocks,
            country_groups=country_groups,
            countries=countries,
            grouped_countries=grouped_countries
        )

        if not is_ok:
            return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "diffusion_id": diffusion_id,
            "graphs": result,
            "country_groups": country_groups,
            "group_all_industries": group_all_industries,
            "filters": {
                "industries": industries,
                "countries": countries,
                "grouped_countries": grouped_countries,
                "limit_largest_shocks": limit_largest_shocks,
            }
        }, status=status.HTTP_200_OK)

    def get(self, request, diffusion_id):
        sort_by = request.query_params.get('sort_by', 'Row')
        sort_order = request.query_params.get('sort_order', 'asc')

        if not sort_by:
            return Response({"error": "Missing 'sort_by' query parameter."}, status=status.HTTP_400_BAD_REQUEST)

        diffusion = get_object_or_404(models.Diffusion, id=diffusion_id)

        is_ok, result = diffusion.get_sorted_log_data(sort_by=sort_by, sort_order=sort_order)

        if not is_ok:
            return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)

