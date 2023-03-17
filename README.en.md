# Effort Metrics on Java API use
[![it](https://img.shields.io/badge/lang-it-blue)](README.md)

## Purpose
The implemented metrics attempt to detect how complex
it is to use Java libraries. The goal of the project is a Python script that analyzes the code 
of a repository in order to quantify the effort on the use of Java APIs 
based on changes made to the code.

## Process
Given the URL GitHub Java, an in-depth analysis is conducted on each repository so specified. 
In each project commit only the modified java files are analyzed. 
A file is considered to be modified if it has undergone a change (MOD), 
a code line addition (ADD) or a code line removal (DEL).

To define the effort of API use, for each modify
source lines of code the implemented script focus on:
* number of changes related to objects instantiated from classes constructor;
* number of changes of method invocations from class or API library;
* what kinds of methods are most frequently cited;
* which APIs have given more trouble to use.

#### Requirements:
All required dependencies are present in [requirements.txt](requirements.txt)  which includes the list of third party packages
with the relative version numbers
* Python 3.8
* Git
* [PyDriller](https://github.com/ishepard/pydriller): to mine the repository
* Pandas: to organize the data
* re: to filter lines of code using regular expressions
* javalang: to parse the already filtered lines of code


## Quick usage:
````commandline
git clone https://github.com/Fliki1/Occorrenze-Metodi-e-Istanze.git
python3 -m venv venv/
source venv/bin/active
pip install -r requirements.txt
````
Start script
````commandline
python main.py [-v]
Enter Gits Repositories: https://github.com/tdebatty/java-LSH, https://github.com/...
````

## Structure
The _src_ folder includes:
* [Comment](./src/Comment.py) detect the presence of comments in modified .java files. 
These will be properly filtered, removing only the parts of no interest
* [ManageDataset](./src/ManageDataset.py) contains methods for managing and updating
support datasets (dataset/variables/methods)
* [Parse](./src/Parse.py) splits each line of modified code into tokens
for subsequent analysis and research of appropriate keywords through regex regular expressions.
* [Api](./src/Api.py) metric core to detect API calls and object instance
* [Class](./src/Class.py) filters the classes present in the current repository
* [Print](./src/Print.py) save the obtained DataFrames in [results](./results)
* [ProgressionBar](./src/ProgressionBar.py) print status progression on prompt
* [Analisicommit](Analisicommit.py) Starting demo script
* [Near](Near.py) determine the presence of modified rows
previously the API calls to understand possible correlations


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
