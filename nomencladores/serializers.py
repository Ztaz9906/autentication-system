from rest_framework import serializers
from .models import Provincia, Municipio, Categoria


class MunicipioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = ['id', 'name']

class ProvinciaDestinatarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = ['name']

class ProvinciaSerializer(serializers.ModelSerializer):
    municipios = MunicipioSerializer(many=True, read_only=True)

    class Meta:
        model = Provincia
        fields = ['id', 'name', 'municipios']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'name']