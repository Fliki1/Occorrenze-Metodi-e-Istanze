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
* numero di righe di codice modificate prossimi e possibilmente correlati a una chiamata API

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
python main.py [-v]
Enter Gits Repositories: https://github.com/tdebatty/java-LSH, https://github.com/...
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
* [Api](./src/Api.py) core della metrica per rilevare le chiamate API e istanziazione di oggetti
* [Class](./src/Class.py) filtra le classi presenti nel repository corrente
* [Print](./src/Print.py) salva i DataFrame ottenuti in [results](./results)
* [ProgressionBar](./src/ProgressionBar.py) print status progression sul terminale
* [Analisicommit](Analisicommit.py) Script di partenza e ispirazione
* [Near](Near.py) permette di determinare la presenza di righe modificate
precedentemente le chiamate API per capire se queste siano correlate alle
chiamate in questione


## Esiti
Esempio caso di: [java-LSH](https://github.com/tdebatty/java-LSH)
#### Variables
DataFrame table che tiene traccia di quali istanze sono presenti nel 
progetto e del tipo a essi associati

| Filename         | Varname        | Vartype        |
|------------------|----------------|----------------|
| InitialSeed.java | mh             | MinHash        |
| InitialSeed.java | mh2            | MinHash        |
| InitialSeed.java | r              | Random         |
| KShingling.java  | ks             | KShingling     |
| LSH.java         | bufferedReader | BufferedReader |
| LSH.java         | fileReader     | FileReader     |
| LSH.java         | ks             | KShingling     |
| LSH.java         | lines          | List           |
| LSH.java         | lsh            | LSH            |
| LSH.java         | mh             | MinHash        |
| ...              | ...            | ...            |

#### Methods
DataFrame table che tiene traccia dei metodi invocati, la classe di appartenenza
dei metodi, e la rispettiva riga e classe nei quali sono state invocate

| Filename         | MethodName  | Class      | CallingClass | Line number |
|------------------|-------------|------------|--------------|-------------|
| InitialSeed.java | nextBoolean | Random     | InitialSeed  | 53          |
| InitialSeed.java | signature   | MinHash    | InitialSeed  | 57          |
| InitialSeed.java | signature   | MinHash    | InitialSeed  | 58          |
| KShingling.java  | add         | KShingling | KShingling   | 40          |
| KShingling.java  | add         | KShingling | KShingling   | 40          |
| KShingling.java  | parse       | KShingling | KShingling   | 26          |
| KShingling.java  | parse       | KShingling | KShingling   | 27          |
| ...              | ...         | ...        | ...          | ...         |

#### Dataset commit table
| Filename         | Line number | Change type | Code                                                                                  | Tokens                                                                                                                                                                                                                                                                                                           | NumEdit |
|------------------|-------------|-------------|---------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| InitialSeed.java | 46          | ['ADD']     | ['        MinHash mh = new MinHash(signature_size, dictionary_size, initial_seed)	']  | [[('MinHash', 'Class'), ('mh', 'Variable'), ('=', 'Operator'), ('new', 'Keyword'), ('MinHash', 'Function'), ('(', 'Separator'), ('signature_size', 'Variable'), (',', 'Separator'), ('dictionary_size', 'Variable'), (',', 'Separator'), ('initial_seed', 'Variable'), (')', 'Separator'), ('	', 'Separator')]]  | 0	      |
| InitialSeed.java | 47          | ['ADD']     | ['        MinHash mh2 = new MinHash(signature_size, dictionary_size, initial_seed)	'] | [[('MinHash', 'Class'), ('mh2', 'Variable'), ('=', 'Operator'), ('new', 'Keyword'), ('MinHash', 'Function'), ('(', 'Separator'), ('signature_size', 'Variable'), (',', 'Separator'), ('dictionary_size', 'Variable'), (',', 'Separator'), ('initial_seed', 'Variable'), (')', 'Separator'), ('	', 'Separator')]] | 0	      |
| InitialSeed.java | 50          | ['ADD']     | ['        Random r = new Random()	']                                                  | [[('Random', 'Class'), ('r', 'Variable'), ('=', 'Operator'), ('new', 'Keyword'), ('Random', 'Function'), ('(', 'Separator'), (')', 'Separator'), ('	', 'Separator')]]                                                                                                                                            | 0	      |
| InitialSeed.java | 53          | ['ADD']     | ['            vector[i] = r.nextBoolean()	']                                          | [[('vector', 'Variable'), ('[', 'Separator'), ('i', 'Variable'), (']', 'Separator'), ('=', 'Operator'), ('r', 'Variable'), ('.', 'Separator'), ('nextBoolean', 'Method'), ('(', 'Separator'), (')', 'Separator'), ('	', 'Separator')]]                                                                           | 0	      |
| InitialSeed.java | 57          | ['ADD']     | ['        println(mh.signature(vector))	']                                            | [[('println', 'Function'), ('(', 'Separator'), ('mh', 'Variable'), ('.', 'Separator'), ('signature', 'Method'), ('(', 'Separator'), ('vector', 'Variable'), (')', 'Separator'), (')', 'Separator'), ('	', 'Separator')]]                                                                                         | 0	      |
| ...              | ...         | ...         | ...                                                                                   | ...                                                                                                                                                                                                                                                                                                              | ...	    |


#### Final Methods
DataFrame table che tiene traccia dei metodi presenti nel 
progetto, la classe di appartenenza, quante volte sono state invocate
e quali classi ne invocano l'utilizzo

| MethodName | Class    | Count | CallingClasses                                                                                                                                        |
|------------|----------|-------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| nextInt    | Random   | 47    | ['MinHash', 'SuperBit', 'LSHMinHashExample', 'SuperBitExample', 'SuperBitSparseExample', 'MinHashTest']                                               |
| signature  | SuperBit | 25    | ['SuperBit', 'LSHMinHash', 'LSHSuperBit', 'MinHashExample', 'SuperBitExample', 'SuperBitSparseExample', 'MinHashTest', 'SuperBitTest', 'InitialSeed'] |
| min        | Math     | 12    | ['LSH']                                                                                                                                               |
| nextDouble | Random   | 9     | ['LSHMinHashExample', 'SuperBitSparseExample', 'SimpleLSHMinHashExample', 'SerializeExample', 'LSHMinHash.', 'SuperBitTest']                          |
| add        | TreeSet  | 9     | ['KShingling', 'LSH', 'MinHash', 'MinHashExample', 'MinHashTest']                                                                                     |
| similarity | SuperBit | 9     | ['MinHash', 'SuperBit', 'MinHashExample', 'SuperBitExample', 'SuperBitSparseExample']                                                                 |
| ...        | ...      | ...   | [...]                                                                                                                                                 |

Possibili chiamate e istanze non conteggiate sono riportate nei file di log.
Questo accade quando non si trovano le dichiarazioni di queste istanze, vedi 
passati come parametri o casting, o invocazione di metodi di librerie importate
(System.out.print(...))

#### Near
DataFrame table che tiene traccia di possibili link tra le chiamate API presenti
in un repository con le precedenti istruzioni eseguite dettate da una finestra
settabile. La metrica cerca di rilevare come la difficoltà dell'uso di chiamate
API siano relative anche a istruzioni precedenti, a parametri richiesti dalla 
chiamata e a modifiche di queste per determinare l'esito voluto. Per sperimentare
questa metrica si è deciso di suddividerla in tre asset diversi al fine di fornire
tre livelli di granualità dettate dalle loro distinte combinazioni.
* **ConsecutiveModifyLine**: righe modificate consecutivamente prima della chiamata API
* **APIModify**: modifica della chiamata API direttamente
* **CorrelationModify**: presenza di riferimenti alla chiamata API nelle righe modificate poco prima 
La tabella riporta:

| Filename         | Time       | HashCommit | Method                                                                                                                                                                                                                                                                                                                                | Class       | ConsecutiveModifyLine | APIModify | CorrelationModify |
|------------------|------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|-----------------------|-----------|-------------------|
| InitialSeed.java | 10/08/2016 | 8,8E+034   | [('vector', 'Variable'), ('[', 'Separator'), ('i', 'Variable'), (']', 'Separator'), ('=', 'Operator'), ('r', 'Variable'), ('.', 'Separator'), ('nextBoolean', 'Method'), ('(', 'Separator'), (')', 'Separator'), (';', 'Separator')]                                                                                                  | InitialSeed | 5	                    | True      | 9                 |                                                                                                                                              |
| KShingling.java  | 28/01/2015 | c464c      | [('System', 'Class'), ('.', 'Separator'), ('out', 'Variable'), ('.', 'Separator'), ('println', 'Method'), ('(', 'Separator'), ('ks', 'Variable'), ('.', 'Separator'), ('toString', 'Method'), ('(', 'Separator'), (')', 'Separator'), (')', 'Separator'), (';', 'Separator')]                                                         | KShingling  | 5	                    | True      | 3                 |                                                                                                                                              |
| LSH.java         | 07/08/2015 | 03ac7      | [('int', 'BasicType'), ('stage', 'Variable'), ('=', 'Operator'), ('Math', 'Class'), ('.', 'Separator'), ('min', 'Method'), ('(', 'Separator'), ('i', 'Variable'), ('/', 'Operator'), ('rows', 'Variable'), (',', 'Separator'), ('s', 'Variable'), ('-', 'Operator'), ('1', 'DecimalInteger'), (')', 'Separator'), (';', 'Separator')] | LSH         | 0	                    | False     | 4                 |                                                                                                                                              |
| ...              | ...        | ...        | ...                                                                                                                                                                                                                                                                                                                                   | ...         | ...                   | ...       | ...               |                                                                                                                                              |

Possono capitare falsi positivi su **ConsecutiveModifyLine** grandi quanto la finestra di righe stabilita sui primissimi
commit. Vengono interpretati come tutte modifiche nuove proprio perché il file compare per la prima volta nel git.

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