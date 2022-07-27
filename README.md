# Metrica sull'utilizzo delle API

## Details
L'obiettivo del progetto è uno script Python che analizzi
il codice di un repository al fine di quantificare la correlazione 
fra le modifiche sul codice e le API da esso usate.

## Process
Dato un URL di un progetto GitHub Java, si analizzano i file .java
modificati in ciascun commit del repository.

Per ogni riga del codice modificato si studiano:
* numero di modifiche relative all'istanziazione di un oggetto
* numero di modifiche a chiamate di metodi di classi o librerie

### Requires
* Python 3.8
* Git
* [PyDriller](https://github.com/ishepard/pydriller): per effettuare il mining dei repository
* Pandas: per organizzare i dati
* re: per filtrare le righe di codice utilizzando espressioni regolari
* javalang: per effettuare il parsing delle righe di codice già filtrate

#### Requirements:
Tutte le dipendenze richieste sono presenti in
[requirements.txt](requirements.txt) 
che comprende la lista delle third party packages 
con i relativi version numbers

## Quick usage:
Git clone
````commandline
git clone https://github.com/Fliki1/Occorrenze-Metodi-e-Istanze.git
````
Creare un nuovo ambiente venv nella directory desiderata
````commandline
python3 -m venv venv/
````
Installare le dipendeze del progetto dentro una virtual enviroment attiva
````commandline
source venv/bin/active
pip install -r requirements.txt
````
Start script
````commandline
python main.py
````

## Structure
Nella cartella _src_ sono presenti le componenti:
* [Comment](./src/Comment.py) che gestisce la presenza di commenti nei file .java
modificati da analizzare. Questi verranno filtrati adeguatamente,
rimuovendo solo le parti di non interesse.
* [ManageDataset](./src/ManageDataset.py) contiene i metodi per la gestione e aggiornamento dei
dataset di supporto (dataset/variables/methods)
* [Parse](./src/Parse.py) permette di suddividere in tokens ogni riga del codice modificato
per le successive analisi e ricerca di keywords opportune tramite l'uso
di espressioni regolari regex.

## Esiti
todo

#### TODO:

1. Vedere se funziona:
````commandline
python3 -m venv venv
source venv/bin/activate
````
E poi installare i requirements:
````commandline
pip install -r requirements.txt
````
2. Espandere la metrica: modifiche a linee di codice vicine forse da
considerare come linkate alla chiamata API poco dopo successiva
3. Esiti
4. modificare la chiamata a più url
5. salvare gli esiti da qualche altra parte