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
They will be properly filtered, removing only the parts of no interest
* [ManageDataset](./src/ManageDataset.py) contains methods for managing and updating
support datasets (dataset/variables/methods)
* [Parse](./src/Parse.py) splits each line of modified code into tokens
for subsequent analysis and research of appropriate keywords through regex regular expressions.
* [Api](./src/Api.py) metric core to detect API calls and object instance
* [Class](./src/Class.py) filters the classes present in the current repository
* [Print](./src/Print.py) save the obtained DataFrames in [results](./results)
* [ProgressionBar](./src/ProgressionBar.py) print status progression on prompt
* [Analisicommit](Analisicommit.py) demo
* [Near](Near.py) determine possible correlations between the API calls and its 
previus modified rows



## Results
Use case: [java-LSH](https://github.com/tdebatty/java-LSH)
#### Variables
DataFrame table that keeps track of which instances are 
present in the project and the type associated

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
DataFrame table that keeps track of the invoked methods, 
the class to which the methods belong, 
and the respective row and class in which they have been invoked

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
DataFrame table that keeps track of the methods present in the project, 
the class to which they belong, 
how many times they have been invoked and which classes invoke their use

| MethodName | Class    | Count | CallingClasses                                                                                                                                        |
|------------|----------|-------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| nextInt    | Random   | 47    | ['MinHash', 'SuperBit', 'LSHMinHashExample', 'SuperBitExample', 'SuperBitSparseExample', 'MinHashTest']                                               |
| signature  | SuperBit | 25    | ['SuperBit', 'LSHMinHash', 'LSHSuperBit', 'MinHashExample', 'SuperBitExample', 'SuperBitSparseExample', 'MinHashTest', 'SuperBitTest', 'InitialSeed'] |
| min        | Math     | 12    | ['LSH']                                                                                                                                               |
| nextDouble | Random   | 9     | ['LSHMinHashExample', 'SuperBitSparseExample', 'SimpleLSHMinHashExample', 'SerializeExample', 'LSHMinHash.', 'SuperBitTest']                          |
| add        | TreeSet  | 9     | ['KShingling', 'LSH', 'MinHash', 'MinHashExample', 'MinHashTest']                                                                                     |
| similarity | SuperBit | 9     | ['MinHash', 'SuperBit', 'MinHashExample', 'SuperBitExample', 'SuperBitSparseExample']                                                                 |
| ...        | ...      | ...   | [...]                                                                                                                                                 |

Possible calls and instances not counted are reported in the log files. 
This happens when the declarations of these instances are not found (see methods' parameters or casting) 
or invocation of methods from imported libraries (ex. System.out.print(…))

#### Near
The metric tries to detect how the difficulty of using API calls is also related to previous instructions. 
Any changes on parameters required by API call.
To experiment this metric was decided to divide it into three different assets in order to provide
three levels of grain dictated by their distinct combinations.
Based on the presence of these it is possible to weigh
differently the result of the metric and therefore the amount of effort which was
required for its appropriate use.

* **ConsecutiveModifyLine**: represents the lines consecutively changed before
the API call. If the lines just before an API invocation were changed,
it could be a change that will affect to the next API call. Once set the
size of the sliding window row (five by default) what is calculated is the
consecutive count lines modified before each invocation of API method
present in the code.
* **APIModify**: modifica della chiamata API direttamente
* **CorrelationModify**: presenza di riferimenti alla chiamata API nelle righe modificate poco prima 

| Filename         | Time       | HashCommit | Method                                                                                                                                                                                                                                                                                                                                | Class       | ConsecutiveModifyLine | APIModify | CorrelationModify |
|------------------|------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|-----------------------|-----------|-------------------|
| InitialSeed.java | 10/08/2016 | 8,8E+034   | [('vector', 'Variable'), ('[', 'Separator'), ('i', 'Variable'), (']', 'Separator'), ('=', 'Operator'), ('r', 'Variable'), ('.', 'Separator'), ('nextBoolean', 'Method'), ('(', 'Separator'), (')', 'Separator'), (';', 'Separator')]                                                                                                  | InitialSeed | 5	                    | True      | 9                 |                                                                                                                                              |
| KShingling.java  | 28/01/2015 | c464c      | [('System', 'Class'), ('.', 'Separator'), ('out', 'Variable'), ('.', 'Separator'), ('println', 'Method'), ('(', 'Separator'), ('ks', 'Variable'), ('.', 'Separator'), ('toString', 'Method'), ('(', 'Separator'), (')', 'Separator'), (')', 'Separator'), (';', 'Separator')]                                                         | KShingling  | 5	                    | True      | 3                 |                                                                                                                                              |
| LSH.java         | 07/08/2015 | 03ac7      | [('int', 'BasicType'), ('stage', 'Variable'), ('=', 'Operator'), ('Math', 'Class'), ('.', 'Separator'), ('min', 'Method'), ('(', 'Separator'), ('i', 'Variable'), ('/', 'Operator'), ('rows', 'Variable'), (',', 'Separator'), ('s', 'Variable'), ('-', 'Operator'), ('1', 'DecimalInteger'), (')', 'Separator'), (';', 'Separator')] | LSH         | 0	                    | False     | 4                 |                                                                                                                                              |
| ...              | ...        | ...        | ...                                                                                                                                                                                                                                                                                                                                   | ...         | ...                   | ...       | ...               |                                                                                                                                              |
