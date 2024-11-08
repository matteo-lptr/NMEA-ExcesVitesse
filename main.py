# type de trame | heure d'envoi | latitude Nord | longitude Ouest | positionnement | nombre de sat | horizontale   | Altitude | Hauteur du géoïde | Vide DGPS |  Somme de contrôle
#  GPGGA,         075404.00,     4817.50121,N,    00201.26375,W,      1,            05,                2.85,         93.2,M,         48.1,M,                      ,*78

import matplotlib.pyplot as plt

def lire_fichier(nom_fichier):
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            contenu = fichier.read()
        return contenu
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{nom_fichier}' n'a pas été trouvé.")
        return None
    except IOError:
        print(f"Erreur : Impossible de lire le fichier '{nom_fichier}'.")
        return None

def main():
    nom_fichier = '2024-09-18_17-59-47.txt'
    contenu = lire_fichier(nom_fichier)
    
    if contenu is not None:
        print("Contenu du fichier :")
        print(contenu)
    else:
        print("Le programme n'a pas pu lire le contenu du fichier.")

if __name__ == "__main__":
    main()