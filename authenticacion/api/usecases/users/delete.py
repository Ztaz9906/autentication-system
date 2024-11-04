from rest_framework import mixins


class DeleteUsuario(mixins.DestroyModelMixin):
    """Clase encargada de la actualización de los usuarios."""