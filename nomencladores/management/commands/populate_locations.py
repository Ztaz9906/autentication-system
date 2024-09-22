from django.core.management.base import BaseCommand
from nomencladores.models import Provincia, Municipio


class Command(BaseCommand):
    help = 'Popula la base de datos con provincias y municipios de Cuba'

    def handle(self, *args, **kwargs):
        provincias_data = {
            'La Habana': ['Playa', 'Plaza de la Revolución', 'Centro Habana', 'La Habana Vieja', 'Regla',
                          'La Habana del Este', 'Guanabacoa', 'San Miguel del Padrón', 'Diez de Octubre', 'Cerro',
                          'Marianao', 'La Lisa', 'Boyeros', 'Arroyo Naranjo', 'Cotorro'],
            'Artemisa': ['Artemisa', 'Alquízar', 'Bauta', 'Caimito', 'Guanajay', 'Güira de Melena', 'Mariel',
                         'San Antonio de los Baños', 'Bahía Honda', 'Candelaria', 'San Cristóbal'],
            'Mayabeque': ['San José de las Lajas', 'Bejucal', 'Jaruco', 'Santa Cruz del Norte', 'Madruga', 'Nueva Paz',
                          'Güines', 'Melena del Sur', 'Batabanó', 'Quivicán', 'San Nicolás'],
            'Matanzas': ['Matanzas', 'Cárdenas', 'Martí', 'Colón', 'Perico', 'Jovellanos', 'Pedro Betancourt',
                         'Limonar', 'Unión de Reyes', 'Ciénaga de Zapata', 'Jagüey Grande', 'Calimete', 'Los Arabos']
        }

        for provincia_name, municipios in provincias_data.items():
            provincia, created = Provincia.objects.get_or_create(name=provincia_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Provincia creada: {provincia_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Provincia ya existe: {provincia_name}'))

            for municipio_name in municipios:
                municipio, created = Municipio.objects.get_or_create(name=municipio_name, provincia=provincia)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Municipio creado: {municipio_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Municipio ya existe: {municipio_name} en {provincia_name}'))

        self.stdout.write(self.style.SUCCESS('Población de datos completada con éxito'))