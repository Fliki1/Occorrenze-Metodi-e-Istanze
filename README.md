# Occorrenze-Metodi-e-Istanze
L'obiettivo del progetto è uno script Python che,
dato un URL di un progetto GitHub in Java, analizzi
il codice .java presente in ogni commit.

Per ogni riga del codice presente in ogni commit si studiano:
* numero di modifiche relative all'istanziazione di un oggetto
* numero di chiamate dei metodi delle classi

Le librerie Python utilizzate:
* Pydriller: per effettuare il mining dei repository
* Pandas: per organizzare i dati
* re: per filtrare le righe di codice utilizzando espressioni regolari
* javalang: per effettuare il parsing delle righe di codice già filtrate

Tutti le dipendenze richieste sono presenti in ./requirements.txt