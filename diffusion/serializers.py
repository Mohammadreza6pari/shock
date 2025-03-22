from rest_framework import serializers
from .models import Diffusion

class DiffusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diffusion
        fields = [
            "id",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at", "status"]