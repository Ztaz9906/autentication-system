from rest_framework import mixins

from rest_framework.exceptions import PermissionDenied

class UpdateUsuario(mixins.UpdateModelMixin):
    """Clase encargada de la actualización de los usuarios."""
    

    def update(self, request, *args, **kwargs):
        user = request.user
        pk = int(kwargs['pk'])  # Convierte pk a entero
        if not user.is_superuser and user.id != pk:
            raise PermissionDenied("No tienes permiso para editar este usuario.")
        return super().update(request, *args, **kwargs)
        