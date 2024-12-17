from rest_framework import mixins


class DetailUsuario(mixins.RetrieveModelMixin):
    """Clase encargada de la obtención de los datos de un usuario."""