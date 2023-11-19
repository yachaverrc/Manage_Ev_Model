import os
from dotenv import load_dotenv
import googlemaps

# Carga las variables de entorno desde el archivo .env
load_dotenv()

def obtener_direcciones(api_key, origen, destino):
    gmaps = googlemaps.Client(key=api_key)
    directions_result = gmaps.directions(origen, destino, mode="driving", avoid="ferries", alternatives=True)
    return directions_result

def calcular_consumo_ajustado(ruta_info):
    eficiencia_vehiculo = 0.2
    factor_ajuste_ascendente = 0.1
    factor_ajuste_descendente = 0.05
    velocidad_media = 60

    distancia_km = ruta_info['legs'][0]['distance']['value'] / 1000
    tiempo_horas = ruta_info['legs'][0]['duration']['value'] / 3600

    ajuste_elevacion = sum(
        max(0, step.get('elevation', 0)) * factor_ajuste_ascendente +
        min(0, step.get('elevation', 0)) * factor_ajuste_descendente
        for step in ruta_info['legs'][0]['steps']
    )

    consumo_base = distancia_km * eficiencia_vehiculo
    consumo_ajustado = consumo_base + ajuste_elevacion * distancia_km

    ajuste_velocidad = distancia_km / tiempo_horas * (velocidad_media / 100)
    consumo_ajustado += ajuste_velocidad

    return consumo_ajustado

def encontrar_ruta_optima():
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    origen = 'Universidad Eafit'
    destino = 'MetroCable Santo Domingo'

    direcciones = obtener_direcciones(api_key, origen, destino)

    if not direcciones:
        print("No se pudieron obtener las direcciones para las rutas.")
        return

    porcentaje_bateria_actual = float(input("Ingrese el porcentaje de batería actual: "))
    porcentaje_bateria_total = 100  # Puedes ajustar esto según la capacidad total de tu batería

    mejor_consumo_ajustado = float('inf')
    mejor_ruta = None

    for i, ruta_info in enumerate(direcciones):
        consumo_ajustado = calcular_consumo_ajustado(ruta_info)

        porcentaje_bateria_necesario = max(0, (consumo_ajustado / porcentaje_bateria_total) * 100)

        print(f"\nValores para la Ruta {i + 1}:")
        print(f"Distancia: {ruta_info['legs'][0]['distance']['text']}")
        print(f"Duración: {ruta_info['legs'][0]['duration']['text']}")
        print(f"Consumo ajustado: {consumo_ajustado:.2f} kWh")
        print(f"Porcentaje de batería necesario: {porcentaje_bateria_necesario:.2f}%")

        if porcentaje_bateria_actual >= porcentaje_bateria_necesario:
            print(f"Con el porcentaje de batería actual, puedes llegar al destino.")
            print(f"Gastarías aproximadamente {consumo_ajustado:.2f} kWh de energía.")
        else:
            print("El porcentaje de batería actual no permite llegar al destino.")

            # Aquí podrías agregar alguna lógica adicional si es necesario, como sugerir recargar la batería.

        if consumo_ajustado < mejor_consumo_ajustado:
            mejor_consumo_ajustado = consumo_ajustado
            mejor_ruta = i + 1

    if mejor_ruta is not None:
        print(f"\nLa ruta más eficiente es la Ruta {mejor_ruta} con un consumo ajustado de {mejor_consumo_ajustado:.2f} kWh.")

# Ejemplo de uso
encontrar_ruta_optima()

