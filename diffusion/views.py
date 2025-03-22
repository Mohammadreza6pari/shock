from rest_framework import views
from . import models, serializers
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import views, status

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
        
        diffusions = models.Diffusion.objects.all()
        serializer = self.serializer_class(diffusions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, diffusion_id):
        """Delete a specific diffusion record."""
        diffusion = get_object_or_404(models.Diffusion, id=diffusion_id)
        diffusion.delete()
        return Response({"message": "Diffusion deleted"}, status=status.HTTP_200_OK)
