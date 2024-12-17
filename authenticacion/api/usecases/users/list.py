from rest_framework import mixins


class ListUsuario(mixins.ListModelMixin):
    """Clase encargada de la obtención de los datos de los usuarios."""