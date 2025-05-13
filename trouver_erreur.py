# Ouvrir le fichier en mode lecture avec l'encodage UTF-8 et ignorer les erreurs d'encodage
with open('templates/connexion.html', 'r', encoding='utf-8', errors='ignore') as f:
    contenu = f.read()

# Afficher le caractère à la position 78 (l'index en Python commence à 0, donc position 78 = index 77)
print(f"Le caractère à la position 78 est : {contenu[77]}")

# Afficher un extrait autour de la position 78
start = max(0, 78 - 10)  # 10 caractères avant la position 78
end = min(len(contenu), 78 + 10)  # 10 caractères après la position 78
print(f"Extrait autour de la position 78 : {contenu[start:end]}")
