from pydriller import Repository
import pandas as pd

from src import Parse, Comment, ManageDataset, Print

#TODO: gestione casi di casting: LSHMinHash saved_lsh = (LSHMinHash) ois.readObject();


def lookForClasses(file):
    """
    Dato l'intero codice di un file si cerca la presenza di tutte le classi e corrispondente riga
    :param file: intero codice di un file
    :return: lista contenenti (riga, classe) presenti nel singolo file
    """
    if file == None:
        return
    classes = []
    lines = file.split("\n")        # split per \n l'intero codice
    # print(lines)                  # ['', '// import java.util.*;  ', 'import java.util.Scanner; // Import the Scanner class', '', 'class Main {',
    for i in range(len(lines)):
        tokens = lines[i].split(" ")                # split per " " codice già splittato da \n
        # print("tokens", tokens)                   # [''] - ['//', 'import', 'java.util.*;', '', ''] - [
        if "class" in tokens:
            if tokens.index("class") + 1 < len(tokens):     # se esiste un riferimento dopo 'class'
                classes.append((i, tokens[tokens.index("class") + 1]))
    # print(classes) [(1, 'ConstructorOverloading'), (20, 'House')] [(4, 'Main')] [(4, 'Main')] []
    return classes


def getActiveClass(classes, line_num):
    """
    Riconoscere la classe analizzata based on lookForClasses precedentemente eseguito (riga, classe)
    :param classes: lista di classi a conoscenza [(1, 'test'), (22, 'ParentTest'), (33, 'test')]
    :param line_num: riga analizzata
    :return: Classe associata a quella riga secondo lookForClasses eseguito in precedenza, None se non presente
    """
    activeClass = None
    for aux in classes:
        if line_num >= aux[0]:
            activeClass = aux[1]
    return activeClass

"""
    DataFrame di supporto per la gestione e analisi dei dati:
        dataset = tutte le linee di codice
        variables = associa ogni istanza alle sue classi di appartenenza
        methods = associa ogni metodo alla sua classe (in relazione all'istanza di appartenenza)
"""
dataset = pd.DataFrame(columns=["Filename", "Change type", "Line number", "Code", "Tokens", "NumEdit"], index=[])
variables = pd.DataFrame(columns=["Filename", "Varname", "Vartype"], index=[])
methods = pd.DataFrame(columns=["Filename", "MethodName", "Class", "CallingClass", "Line number"], index=[])

# Core methods
#https://github.com/niharika2k00/Java
for commit in Repository('https://github.com/tdebatty/java-LSH').traverse_commits():
    #per ogni commit
    for file in commit.modified_files:
        # se è stato modificato un file .java
        if (file.change_type.name == "ADD" or file.change_type.name == "MODIFY" \
            or file.change_type.name == "DELETE") and file.filename[-5:] == ".java":

            # nome classe
            name = file.filename
            #print(name)
            change = file.change_type.name  # ADD - MODIFY ...

            # ogni riga aggiunta o cancellata nel file {'added': [(1, ''), (2, '// import java.util.*;'), (3,... 'delete': ...}
            diff = file.diff_parsed
            added = diff["added"]
            deleted = diff["deleted"]
            lines = added + deleted     # [(1, ''), (2, '// import java.util.*;'), (3,... puro codice solo modificato nel commit
            cutOffPoint = len(added)
            #print("==================")

            # print(file.source_code)   # file.source_code = source code of the file (can be _None_ if the file is deleted or only renamed)
            # print(file.source_code_before)   # file.source_code_before = source code of the file before the change (can be _None_ if the file is added or only renamed)

            # lista (riga, classe) del codice corrente
            classesInAdded = lookForClasses(file.source_code)
            # lista (riga, classe) del codice come era prima
            classesInDeleted = lookForClasses(file.source_code_before)
            # status MultipleComment
            multicomments = False

            for i, element in zip(range(len(lines)), lines):
                #print("added + deleted ", i, element)

                # ricerca nella linea la presenza di pluri-commento
                if Comment.isStartMultipleComment(element[1]):
                    multicomments = True
                if Comment.isEndMultipleComment(element[1]):
                    multicomments = False
                if multicomments:
                    continue

                # ricerca nella linea la presenza di invocazione singolo-commento - metodo - new instanza
                if Comment.isSingleComment(element[1]):
                    # converto la tupla element in lista per poterla modificare e togliere il commento di troppo
                    my_element = list(element)
                    my_element[1] = Comment.removeComment(my_element[1])
                    element = tuple(my_element)
                    # print("added + deleted ", i, element)
                    # print("NO COMMENTO", element[1])
                matchMethodCall = Comment.reMethodCall.search(element[1])
                matchInstAss = Comment.reInstAss.search(element[1])


                if matchMethodCall or matchInstAss:
                    tokens = Parse.parseLine(element[1])
                    # eg invocazione di Metodo: Day arr[] = Day.values(); diventa
                    # [('Day', 'Class'), ('arr', 'Variable'), ('[', 'Separator'), (']', 'Separator'), ('=', 'Operator'),
                    # ('Day', 'Class'), ('.', 'Separator'), ('values', 'Method'), ('(', 'Separator'), (')', 'Separator'),
                    # (';', 'Separator')]

                    # Update Dataset
                    if dataset.loc[(dataset["Filename"] == name) & (dataset["Line number"] == element[0])].empty:
                        # new entry nel dataset
                        dataset.loc[len(dataset.index)] = [name, [change], element[0], [element[1]], [tokens], 0]
                    else:
                        # old entry nel dataset
                        ind = dataset.loc[(dataset["Filename"] == name) & (dataset["Line number"] == element[0])].index
                        if len(ind) != 1:
                            # ind = lista di indici di dataset in cui è presente lo stesso riferimento cercato: ERRORE
                            print("Warning: counted the wrong number of indices")
                            print("DEBUG ",dataset.loc[(dataset["Filename"] == name) & (dataset["Line number"] == element[0])])
                        ind = ind[0]
                        # update
                        dataset.at[ind, "Change type"].append(change)   # lista cambiamenti [ADD,DELETE,DELETE...
                        dataset.at[ind, "Code"].append(element[1])      # new code
                        dataset.at[ind, "Tokens"].append(tokens)        # token new code
                        dataset.at[ind, "NumEdit"] = dataset.at[ind, "NumEdit"] + 1     # numero modifiche subite

                # Update Variabili Instanze Set
                if matchInstAss:
                    #print("VARIABILE: ", element[1])
                    variables = ManageDataset.addVariables(variables, tokens, name)
                # Update Metodi Set
                if matchMethodCall:
                    #print("METODO: ", element[1])
                    if i < cutOffPoint:
                        activeClass = getActiveClass(classesInAdded, element[0])
                    else:
                        activeClass = getActiveClass(classesInDeleted, element[0])
                    methods = ManageDataset.addMethods(methods, variables, tokens, name, element[0], activeClass)

Print.printData(dataset, variables, methods)
