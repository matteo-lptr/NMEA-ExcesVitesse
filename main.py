# type de trame | heure d'envoi | latitude Nord | longitude Ouest | positionnement | nombre de sat | horizontale   | Altitude | Hauteur du géoïde | Vide DGPS |  Somme de contrôle
#  GPGGA,         075404.00,     4817.50121,N,    00201.26375,W,      1,            05,                2.85,         93.2,M,         48.1,M,                      ,*78

import matplotlib.pyplot as plt
from datetime import datetime
import math
import folium
import os

def lire_et_afficher_fichier(nom_fichier):
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            contenu = fichier.read()
            print(f"Nombre total de lignes dans le fichier : {len(contenu.splitlines())}")
            print(f"Les 5 premières lignes du fichier '{nom_fichier}':")
            print('\n'.join(contenu.splitlines()[:5]))
        return contenu
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{nom_fichier}' n'a pas été trouvé.")
        return None
    except IOError:
        print(f"Erreur : Impossible de lire le fichier '{nom_fichier}'.")
        return None

def parse_gga(line):
    fields = line.split(',')
    if len(fields) < 15:
        print(f"Ligne invalide (pas assez de champs): {line}")
        return None
    try:
        time = datetime.strptime(fields[1][:6], '%H%M%S')
        lat = float(fields[2][:2]) + float(fields[2][2:]) / 60
        lon = float(fields[4][:3]) + float(fields[4][3:]) / 60
        if fields[3] == 'S':
            lat = -lat
        if fields[5] == 'W':
            lon = -lon
        return time, lat, lon
    except (ValueError, IndexError):
        print(f"Erreur de parsing pour la ligne: {line}")
        return None

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Rayon de la Terre en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def creer_graphique_vitesse(contenu):
    lines = contenu.split('\n')
    times, lats, lons = [], [], []
    
    for line in lines:
        if line.startswith('GPGGA') or line.startswith('PGGA'):
            parsed = parse_gga(line)
            if parsed:
                time, lat, lon = parsed
                times.append(time)
                lats.append(lat)
                lons.append(lon)

    if len(times) < 2:
        print("Pas assez de données pour créer un graphique.")
        return

    distances = [0]
    speeds = []
    
    for i in range(1, len(times)):
        dist = calculate_distance(lats[i-1], lons[i-1], lats[i], lons[i])
        distances.append(distances[-1] + dist)
        time_diff = (times[i] - times[i-1]).total_seconds() / 3600  # en heures
        speed = dist / time_diff if time_diff > 0 else 0
        speeds.append(speed)

    plt.figure(figsize=(10, 6))
    plt.plot(distances[1:], speeds)
    plt.title('Vitesse en fonction de la distance parcourue')
    plt.xlabel('Distance (km)')
    plt.ylabel('Vitesse (km/h)')
    plt.grid(True)
    plt.show()

def create_map(data, html_file_path):
    if not data:
        print("Aucune donnée GPS valide pour créer la carte.")
        return

    m = folium.Map(location=[data[0]['lat'], data[0]['lon']], zoom_start=13)

    for point in data:
        folium.CircleMarker(
            location=[point['lat'], point['lon']],
            radius=5,
            popup=f"Vitesse: {point['speed']:.2f} km/h",
            tooltip=f"Vitesse: {point['speed']:.2f} km/h",
            color="#3186cc",
            fill=True,
            fillColor="#3186cc"
        ).add_to(m)

    folium.PolyLine(locations=[[point['lat'], point['lon']] for point in data], color="red", weight=2.5, opacity=1).add_to(m)

    try:
        m.save(html_file_path)
        print(f"Carte sauvegardée avec succès à : {html_file_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la carte : {e}")

def process_gps_data(filename):
    data = []
    prev_time = prev_lat = prev_lon = None

    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('GPGGA') or line.startswith('PGGA'):
                parsed = parse_gga(line)
                if parsed:
                    time, lat, lon = parsed
                    if prev_time is not None:
                        dist = calculate_distance(prev_lat, prev_lon, lat, lon)
                        time_diff = (time - prev_time).total_seconds() / 3600  # en heures
                        speed = dist / time_diff if time_diff > 0 else 0
                        data.append({'lat': prev_lat, 'lon': prev_lon, 'speed': speed * 3600})  # vitesse en km/h
                    prev_time, prev_lat, prev_lon = time, lat, lon

    if prev_lat is not None and prev_lon is not None:
        data.append({'lat': prev_lat, 'lon': prev_lon, 'speed': 0})

    return data

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    nom_fichier = os.path.join(script_dir, '2024-09-18_17-59-47.txt')
    html_file_path = os.path.join(script_dir, "gps_map.html")

    contenu = lire_et_afficher_fichier(nom_fichier)
    
    if contenu:
        creer_graphique_vitesse(contenu)
        
        gps_data = process_gps_data(nom_fichier)
        
        create_map(gps_data, html_file_path)

if __name__ == "__main__":
    main()