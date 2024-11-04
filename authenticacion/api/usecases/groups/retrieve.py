from rest_framework import mixins


class DetailGrupo(mixins.RetrieveModelMixin):
    """Clase encargada de la obtención los datos de un grupo."""