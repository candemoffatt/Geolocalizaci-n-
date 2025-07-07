from flask import Flask, render_template, renrequest
import requests
import os
import re

app = Flask(__name__)

# Cargamos la clave desde los secrets
GOOGLE_MAPS_API_KEY = os.environ["GOOGLE_MAPS_API_KEY"]
direccion_municipalidad = "Manuel Castro 220, Lomas de Zamora"


def geolocalizar(direccion):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": f"{direccion}, Lomas de Zamora, Buenos Aires, Argentina",
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "OK":
        resultado = data["results"][0]
        direccion_estandar = resultado["formatted_address"]
        lat = resultado["geometry"]["location"]["lat"]
        lng = resultado["geometry"]["location"]["lng"]
        return direccion_estandar, lat, lng
    else:
        return "NO ENCONTRADA", "", ""
def resaltar_direccion(direccion):
    match = re.match(r"(.+?\d+)(.*)", direccion)
    if match:
        return match.group(1), match.group(2)
    else:
        return direccion, ""

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = []
    if request.method == 'POST':
        # 1. Agregar primero la dirección fija
        direccion_estandar, lat, lng = geolocalizar(direccion_municipalidad)
        resaltado, resto = resaltar_direccion(direccion_estandar)

        resultados.append({
            "original": "Municipalidad",
            "corregida": direccion_estandar,
            "resaltado": resaltado,
            "resto": resto,
            "lat": lat,
            "lng": lng
        })

        # 2. Procesar las que pegás
        texto = request.form.get('direcciones', '')
        direcciones = [
            line.strip() for line in texto.strip().split('\n') if line.strip()
        ]
        for d in direcciones:
            direccion_estandar, lat, lng = geolocalizar(d)
            resaltado, resto = resaltar_direccion(direccion_estandar)
            resultados.append({
                "original": d,
                "corregida": direccion_estandar,
                "resaltado": resaltado,
                "resto": resto,
                "lat": lat,
                "lng": lng
            })
    return render_template('index.html', resultados=resultados)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))
  
