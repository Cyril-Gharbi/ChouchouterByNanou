import psycopg2
from werkzeug.security import generate_password_hash

# Connexion à ta base PostgreSQL
conn = psycopg2.connect(
    dbname="chouchouter_db",
    user="cyg_gh",
    password="Assia_2010",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Sélectionner tous les utilisateurs avec mot de passe en clair
cursor.execute('SELECT id, "password" FROM "user"')
users = cursor.fetchall()

# Pour chaque utilisateur, générer un hash et mettre à jour
for user_id, plain_password in users:
    if not plain_password.startswith("pbkdf2:"):  # évite de rehacher un hash déjà fait
        hashed = generate_password_hash(plain_password)
        cursor.execute('UPDATE "user" SET "password" = %s WHERE id = %s', (hashed, user_id))

# Sauvegarder et fermer
conn.commit()
cursor.close()
conn.close()

print("✅ Tous les mots de passe ont été hashés.")
