from rest_framework import mixins
from authenticacion.utils.permisions import IsSuperUser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
class DeleteUsuario(mixins.DestroyModelMixin):
    """Clase encargada de la actualización de los usuarios."""
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_200_OK, data={"message": "Usuario desactivado correctamente."})