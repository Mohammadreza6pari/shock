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


import csv
import io
import pandas as pd
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user.permissions import IsApprovedUser


class DatasetGroupingView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedUser]

    def post(self, request):
        data = request.data
        dataset_id = data.get("dataset_id")
        country_groups = data.get("country_groups", [])
        group_all_industries = data.get("group_all_industries", False)

        if not dataset_id:
            return Response({"error": "dataset_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        dataset = get_object_or_404(Dataset, id=dataset_id)

        # Load the dataset CSV
        with dataset.file.open("rb") as f:
            text_file = io.TextIOWrapper(f, encoding="utf-8")
            df = pd.read_csv(text_file)

        # Apply country grouping
        if country_groups:
            group_map = {}
            for group in country_groups:
                if isinstance(group, dict):
                    group_name = group["name"]
                    members = group["members"]
                else:
                    members = group
                    group_name = "_".join(sorted(members))  # fallback
                for country in members:
                    group_map[country] = group_name

            # Update column names for countries
            new_columns = {}
            for col in df.columns:
                if "_" in col:
                    country, industry = col.split("_", 1)
                    new_country = group_map.get(country, country)
                    new_columns[col] = f"{new_country}_{industry}"
                else:
                    new_columns[col] = col
            df.rename(columns=new_columns, inplace=True)

            # Group columns by summing
            grouped_df = df.groupby(level=0, axis=1).sum()
            df = grouped_df

        # Apply industry grouping if group_all_industries is True
        if group_all_industries:
            # Sum all columns except the first one (assuming first is index or something)
            # Actually, since columns are country_industry, we need to group by country
            industry_groups = {}
            for col in df.columns:
                if "_" in col:
                    country, industry = col.split("_", 1)
                    if country not in industry_groups:
                        industry_groups[country] = []
                    industry_groups[country].append(col)

            new_df = pd.DataFrame()
            for country, cols in industry_groups.items():
                new_df[f"{country}_ALL"] = df[cols].sum(axis=1)
            df = new_df

        # Create a new dataset with the grouped data
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        # Create a new Dataset instance
        new_dataset_name = f"{dataset.name}_grouped"
        new_dataset = Dataset(name=new_dataset_name)
        new_dataset.file.save(f"{new_dataset_name}.csv", io.BytesIO(output.getvalue().encode('utf-8')))
        new_dataset.save()

        serializer = DatasetSerializer(new_dataset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
