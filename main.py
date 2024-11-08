#- type de trame | heure d'envoi | latitude Nord | longitude Ouest | positionnement | nombre de sat | horizontale   | Altitude | Hauteur du géoïde | Vide DGPS |  Somme de contrôle
#-  GPGGA,         075404.00,     4817.50121,N,    00201.26375,W,      1,            05,                2.85,         93.2,M,         48.1,M,                      ,*78

import matplotlib.pyplot as plt
from datetime import datetime
import math
import folium
import os

def lire_et_afficher_fichier(nom_fichier):
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            contenu = fichier.read()
            print(f"Nombre total de lignes dans le fichier : {len(contenu.splitlines())}") #--- Affiche dans la console le nombre de ligne
            print(f"Les 5 premières lignes du fichier '{nom_fichier}':") #-- Affiche dans la console :"Les 5 premières lignes du fichier" + le chemin du fichier et son nom
            print('\n'.join(contenu.splitlines()[:5])) #--- Affiche dans la console le contenue des 5premieres lignes
        return contenu
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{nom_fichier}' n'a pas été trouvé.") #--- Affiche dans la console cette phrase si le fichier n'est pas trouver ou n'est pas dans le repertoire de ce script
        return None
    except IOError:
        print(f"Erreur : Impossible de lire le fichier '{nom_fichier}'.") #--- Affiche dans la console cette phrase si le fichier est illisible
        return None

def parse_gga(line):
    fields = line.split(',')
    if len(fields) < 15:
        print(f"Ligne invalide (pas assez de champs): {line}") #--- Affiche dans la console cette phrase si il n'y a pas assez d'information lu dans le fichier 
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
    R = 6371  #- Rayon de la Terre en kilomètres
    
    dlat = math.radians(lat2 - lat1) #- Calculer la différence de latitude et convertir en radians
    dlon = math.radians(lon2 - lon1) #- Calculer la différence de longitude et convertir en radians
    
    a = (math.sin(dlat / 2)**2 +  #- Carré du sinus de la moitié de la différence de latitude
         math.cos(math.radians(lat1)) *  #- Cosinus de la latitude du premier point
         math.cos(math.radians(lat2)) *  #- Cosinus de la latitude du deuxième point
         math.sin(dlon / 2)**2)  #- Carré du sinus de la moitié de la différence de longitude
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))  #- Calculer l'angle central 'c' entre les deux points

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
        
        #- Calcul du temps écoulé en heures
        time_diff = (times[i] - times[i-1]).total_seconds() / 3600  #- en heures
        
        #- Calcul de la vitesse en km/h
        speed = dist / time_diff if time_diff > 0 else 0
        speeds.append(speed)

    #- Création des sous-graphiques pour vitesse, distance et accélération
    fig, axs = plt.subplots(3, 1, figsize=(12, 18))  #- Augmenter la taille de la figure

    #- Graphique de la vitesse
    axs[0].plot(distances[1:], speeds, color='blue')
    axs[0].set_title('Vitesse en fonction de la distance parcourue', fontsize=16)
    axs[0].set_xlabel('Distance (km)', fontsize=14)
    axs[0].set_ylabel('Vitesse (km/h)', fontsize=14)
    axs[0].grid(True)

    #- Graphique de la distance parcourue
    axs[1].plot(range(len(distances)), distances, color='green')
    axs[1].set_title('Distance parcourue au fil du temps', fontsize=16)
    axs[1].set_xlabel('Points GPS', fontsize=14)
    axs[1].set_ylabel('Distance (km)', fontsize=14)
    axs[1].grid(True)

    #- Calculer l'accélération à partir des vitesses
    accelerations = [0]  #- Initialiser avec zéro pour le premier point
    
    for i in range(1, len(speeds)):
        time_diff_seconds = (times[i] - times[i-1]).total_seconds()  #- en secondes
        acceleration = (speeds[i] - speeds[i-1]) / time_diff_seconds if time_diff_seconds > 0 else 0
        accelerations.append(acceleration)

    #- Graphique de l'accélération
    axs[2].plot(range(len(accelerations)), accelerations, color='red')
    axs[2].set_title('Accélération au fil du temps', fontsize=16)
    axs[2].set_xlabel('Points GPS', fontsize=14)
    axs[2].set_ylabel('Accélération (km/h²)', fontsize=14)
    axs[2].grid(True)

    plt.tight_layout(pad=4.0)  #- Ajuster les espacements entre les sous-graphiques
    plt.show()

def create_map(data, html_file_path):
    #- Vérifier si les données GPS sont valides
    if not data:
        print("Aucune donnée GPS valide pour créer la carte.")
        return  #- Sortir de la fonction si aucune donnée n'est disponible

    #- Créer une carte Folium centrée sur le premier point GPS
    m = folium.Map(location=[data[0]['lat'], data[0]['lon']], zoom_start=13)

    #- Ajouter un marqueur pour chaque point GPS dans les données
    for point in data:
        folium.CircleMarker(
            location=[point['lat'], point['lon']],  #- Position du marqueur
            radius=5,  #- Taille du marqueur
            popup=f"Vitesse: {point['speed']:.2f} km/h",  #- Afficher la vitesse dans une fenêtre contextuelle
            tooltip=f"Vitesse: {point['speed']:.2f} km/h",  #- Afficher la vitesse au survol du marqueur
            color="#3186cc",  #--- Couleur du contour du marqueur
            fill=True,  #--- Remplir le marqueur
            fillColor="#3186cc"  # Couleur de remplissage du marqueur
        ).add_to(m)  # Ajouter le marqueur à la carte

    # Ajouter une ligne reliant tous les points GPS pour montrer le trajet
    folium.PolyLine(
        locations=[[point['lat'], point['lon']] for point in data],  # Coordonnées des points à relier
        color="red",  # Couleur de la ligne
        weight=2.5,  #--- Épaisseur de la ligne
        opacity=1  #--- Opacité de la ligne
    ).add_to(m)  #--- Ajouter la ligne à la carte

    try:
        m.save(html_file_path)  #--- Sauvegarder la carte dans un fichier HTML
        print(f"Carte sauvegardée avec succès à : {html_file_path}")  #--- Message de confirmation
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la carte : {e}")  #--- Gérer les erreurs de sauvegarde


def process_gps_data(filename):
    data = []
    prev_time = prev_lat = prev_lon = None

    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('GPGGA') or line.startswith('PGGA'):
                parsed = parse_gga(line)
                if parsed:
                    time, lat, lon = parsed
                    if prev_time is not None and prev_lat is not None and prev_lon is not None:
                        dist = calculate_distance(prev_lat, prev_lon, lat, lon)
                        time_diff_hours = (time --- prev_time).total_seconds() / 3600  #--- en heures

                        #--- Calculer la vitesse seulement si le temps écoulé est positif et non nul
                        if time_diff_hours > 0:
                            speed = dist / time_diff_hours  #--- vitesse en km/h
                            data.append({'lat': prev_lat, 'lon': prev_lon, 'speed': speed})
                        else:
                            data.append({'lat': prev_lat, 'lon': prev_lon, 'speed': 0})  #--- vitesse nulle si pas de temps écoulé
                    
                    prev_time, prev_lat, prev_lon = time, lat, lon

    #--- Ajouter le dernier point avec une vitesse nulle si nécessaire
    if prev_lat is not None and prev_lon is not None and len(data) > 0:
        data.append({'lat': prev_lat, 'lon': prev_lon, 'speed': 0})

    return data

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    nom_fichier = os.path.join(script_dir, '2024-09-18_17-59-47.txt') #--- Modifier le nom du fichier selon le fichier qui contient vos données
    html_file_path = os.path.join(script_dir, "gps_map.html") #--- Ajout du fichier.html qui affiche la carte et les points dans le repertoire du script si il n'existe pas

    contenu = lire_et_afficher_fichier(nom_fichier)
    
    if contenu:
        creer_graphique_vitesse(contenu) #--- Creer le graphique de la vitesse
        
        gps_data = process_gps_data(nom_fichier) 
        
        create_map(gps_data, html_file_path) 

if __name__ == "__main__":
    main()