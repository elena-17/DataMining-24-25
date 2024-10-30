""" Module with utility functions for webscraping. """

from geopy.geocoders import Nominatim


def obtain_CA_and_Province(lat, lon):
    geolocator = Nominatim(user_agent="abc@email.com")

    # Convertir las coordenadas en una ubicación
    location = geolocator.reverse((lat, lon), language="es")
    if location and location.raw:
        # Obtener los datos de la ubicación
        address = location.raw.get("address", {})

        # Extraer comunidad autónoma y provincia si están disponibles
        comunidad_autonoma = address.get("state", "Comunidad autónoma no encontrada")
        provincia = address.get("province", "Provincia no encontrada")

        return comunidad_autonoma, provincia
    else:
        return None, None
