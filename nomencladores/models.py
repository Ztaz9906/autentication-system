from django.db import models

# Create your models here.


class Provincia(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Municipio(models.Model):
    name = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, related_name='municipios', on_delete=models.CASCADE)


class Categoria(models.Model):
    name = models.CharField(max_length=100, unique=True)