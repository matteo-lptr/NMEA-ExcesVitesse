# NMEA-ExcesVitesse

## Mode d'emploi
### Configuration
- Modifier le nom du fichier qui contient les données GPGGA (ligne 191)
- Modifier le nom du fichier html qui affichera le trajet affectuer sur une carte (ligne 192)
- Modifier la couleur des points sur la carte du fichier '.html' (ligne 139)
- Modifier la couleur de la ligne entre chaque point sur la carte du fichier '.html' (ligne 147)

### Calcule
- Calcul le nombres de ligne du fichier + Affiche console
- Calcul les 5 premieres lignes + Affiche console leur contenue
- Calcul du temps écoulé en heures 
- Calcul de la vitesse en km/h
- Calcul de l'acceleration

### Graphique
- Graphique de la vitesse en fonction de la distance parcourue
- Graphique de la distance parcourue au fil du temps
- Graphique de l'acceleration au fil du temps

### Cartographie
- Creation du fichier '.html'
- Créer un carte centrée sur le premier point GPS
- Ajoute un point à chaque donnée GPGGA retourner
- Ajoute à chaque point la vitesse actuel
- Ajout une ligne reliant les points
- Sauvegarde la carte dans le fichier '.html'

### Librairies
- La visualisation de données (avec Matplotlib). | https://matplotlib.org/
- La manipulation et l'analyse de dates et d'heures (avec datetime). | https://docs.python.org/3/library/datetime.html
- Les calculs mathématiques (avec math). | https://docs.python.org/3/library/math.html
- La création de cartes interactives (avec Folium). | https://python-visualization.github.io/folium/latest/
- L'interaction avec le système de fichiers (avec os). | https://docs.python.org/3/library/os.html