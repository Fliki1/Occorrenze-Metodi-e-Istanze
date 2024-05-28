import csv
import os
import sys
from collections import defaultdict

# Prendi il percorso della cartella da riga di comando
folder_path = sys.argv[1]

# Inizializza un dizionario per memorizzare i conteggi
counts = defaultdict(lambda: defaultdict(lambda: {'ADD Count': 0, 'MODIFY Count': 0, 'DEL Count': 0}))

csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

print(f'Numero di file CSV da analizzare: {len(csv_files)}')

# Percorri tutti i file nella cartella
for filename in csv_files:
    # Apri il file CSV
    with open(os.path.join(folder_path, filename), 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Salta l'intestazione

        for row in reader:
            class_name, methods, change_types, _, _, _ = row

            # Rimuovi i caratteri non necessari e converti in lista
            methods = methods.strip("[]").replace("'", "").split(", ")
            change_types = change_types.strip("[]").replace("'", "").split(", ")

            # Conta tutte le occorrenze dei metodi e tieni traccia dei tipi di cambiamento
            for method in methods:
                if 'ADD' in change_types:
                    counts[class_name][method]['ADD Count'] += 1
                elif 'DELETE' in change_types:
                    counts[class_name][method]['DEL Count'] += 1
                elif 'ADD' not in change_types:
                    counts[class_name][method]['MODIFY Count'] += 1

# Scrivi i risultati in un nuovo file CSV
with open('output.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Class', 'Method', 'ADD Count', 'MODIFY Count', 'DEL Count'])

    for class_name, methods in counts.items():
        for method, change_types in methods.items():
            writer.writerow([class_name, method, change_types['ADD Count'], change_types['MODIFY Count'], change_types['DEL Count']])
