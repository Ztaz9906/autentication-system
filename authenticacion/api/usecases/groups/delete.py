from rest_framework import mixins


class DeleteGrupo(mixins.DestroyModelMixin):
    """Clase encargada de la eliminación de los grupos."""
