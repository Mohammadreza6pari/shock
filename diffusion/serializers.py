from rest_framework import serializers
from dataset.models import Dataset
from .models import Diffusion

class DiffusionSerializer(serializers.ModelSerializer):
    integration = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Dataset.objects.all()
    )
    class Meta:
        model = Diffusion
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
            "status",
            "number_of_iterations",
            "integration",
            "sources",
            "destinations",
            "shock_types",
            "shock_amounts",
            "threshold_one",
            "threshold_two",
            "threshold_three",
            "logs",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "status", "logs"]