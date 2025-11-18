import os
import zipfile
import pandas as pd

# --- Configuration des chemins ---
zip_path = '/mnt/data/gestion-vente-master.zip'
extract_dir = '/mnt/data/gestion-vente-master'
csv_output = '/mnt/data/file_list.csv'

# --- 1. Dézipper le fichier ---
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)
print(f"✅ Projet décompressé dans : {extract_dir}")

# --- 2. Parcourir l'arborescence et lister les fichiers ---
file_data = []
preview_extensions = ('.py', '.txt', '.md', '.html', '.css', '.js', '.json', '.csv')

for root, dirs, files in os.walk(extract_dir):
    for file in files:
        file_path = os.path.join(root, file)
        rel_path = os.path.relpath(file_path, extract_dir)
        file_size = os.path.getsize(file_path)
        preview = ''
        if file.lower().endswith(preview_extensions):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    preview = f.read(1200)  # premiers ~1200 caractères
            except Exception as e:
                preview = f"<Impossible de lire le fichier : {e}>"
        file_data.append({
            'relative_path': rel_path,
            'full_path': file_path,
            'size_bytes': file_size,
            'preview': preview
        })

# --- 3. Compter le nombre total de fichiers ---
total_files = len(file_data)
print(f"📂 Nombre total de fichiers : {total_files}")

# --- 4. Sauvegarder le résumé CSV ---
df = pd.DataFrame(file_data)
df.to_csv(csv_output, index=False)
print(f"💾 Liste des fichiers sauvegardée dans : {csv_output}")

# --- Optionnel : afficher les 10 premiers fichiers pour vérification ---
print("\nAperçu des 10 premiers fichiers :")
print(df[['relative_path', 'size_bytes']].head(10))
