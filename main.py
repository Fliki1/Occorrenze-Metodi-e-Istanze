from pydriller import Repository
import pandas as pd

from src import Parse, Comment


def addVariables(table, tokens, filename):
    """
    Update Dataset variables contenente le instanze trovate nel progetto
    :param table: variables dataset
    :param tokens: code tokens line
    :param filename: java file
    :return: table updated
    """
    for i in range(len(tokens)):
        if tokens[i][1] == "Variable" and tokens[i - 1][1] == "Class":
            # se è una instanza di classe
            # table = table.append({"Filename":filename, "Varname":tokens[i][0],\
            #                       "Vartype":tokens[i-1][0]}, ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i - 1][0]]
            table.drop_duplicates(inplace=True)     # evitiamo di tenere in memoria copie della stessa instanza
        elif tokens[i][1] == "Variable" and tokens[i - 1][0] == ">":
            # type safety java case eg: List<MyObj> pippo = new List<MyObj>();
            j = tokens.index(("<", "Operator"))
            # table = table.append({"Filename":filename, "Varname":tokens[i][0],\
            #                       "Vartype":tokens[j-1][0]}, ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[j - 1][0]]
            table.drop_duplicates(inplace=True)     # evitiamo di tenere in memoria copie della stessa instanza
    return table


def addMethods(table, variables, tokens, filename, line_num, activeClass):
    for i in range(len(tokens)):
        if tokens[i][1] == "Method" and tokens[i - 2][1] == "Variable":
            vartype = checkVariableClass(variables, filename, tokens[i - 2][0])
            if vartype:
                # table = table.append({"Filename":filename, "MethodName":tokens[i][0],\
                #                       "Class":vartype, "Line number":line_num},\
                #                      ignore_index = True)
                table.loc[len(table.index)] = [filename, tokens[i][0], vartype, \
                                               activeClass, line_num]
        elif tokens[i][1] == "Method" and tokens[i - 2][1] == "Class":
            # table = table.append({"Filename":filename, "MethodName":tokens[i][0],\
            #                       "Class":tokens[i-2][0], "Line number":line_num},\
            #                      ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i - 2][0], \
                                           activeClass, line_num]
        elif tokens[i][1] == "Method" and tokens[i - 4][1] == "Class":
            # table = table.append({"Filename":filename, "MethodName":tokens[i][0],\
            #                       "Class":tokens[i-4][0], "Line number":line_num},\
            #                      ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i - 4][0], \
                                           activeClass, line_num]
    return table


def checkVariableClass(table, filename, varname):
    auxset = table[table["Filename"] == filename]
    auxset = auxset[auxset["Varname"] == varname]
    if auxset.shape[0] > 1:
        #print("Multiple variables with the same name detected in the same file.")
        return
    elif auxset.shape[0] == 0:
        #print("Variable declaration not previously found")
        return
    else:
        return auxset.iat[0, 2]


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
    :return: Classe associata a quella riga secondo lookFroClasses eseguito in precedenza, None se non presente
    """
    activeClass = None
    #print("classes", classes)
    #print("line_num", line_num)
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
#https://github.com/tdebatty/java-LSH
for commit in Repository('https://github.com/niharika2k00/Java').traverse_commits():
    #per ogni commit
    for file in commit.modified_files:
        # se è stato modificato un file .java
        if (file.change_type.name == "ADD" or file.change_type.name == "MODIFY" \
            or file.change_type.name == "DELETE") and file.filename[-5:] == ".java":

            # nome classe
            name = file.filename
            change = file.change_type.name  # ADD - MODIFY ...

            # ogni riga aggiunta o cancellata nel file {'added': [(1, ''), (2, '// import java.util.*;'), (3,... 'delete': ...}
            diff = file.diff_parsed
            added = diff["added"]
            deleted = diff["deleted"]
            lines = deleted + added     # [(1, ''), (2, '// import java.util.*;'), (3,... puro codice solo modificato nel commit
            cutOffPoint = len(added)

            # print(file.source_code)   # file.source_code = source code of the file (can be _None_ if the file is deleted or only renamed)
            # print(file.source_code_before)   # file.source_code_before = source code of the file before the change (can be _None_ if the file is added or only renamed)

            # lista (riga, classe) del codice corrente
            classesInAdded = lookForClasses(file.source_code)
            # lista (riga, classe) del codice come era prima
            classesInDeleted = lookForClasses(file.source_code_before)  # perché?

            for i, element in zip(range(len(lines)), lines):
                ##############print("deleted + added ", i , element)
                # ricerca nella linea la presenza di invocazione metodo - new instanza - commento
                matchMethodCall = Comment.reMethodCall.search(element[1])
                matchInstAss = Comment.reInstAss.search(element[1])
                if Comment.isComment(Comment.reIsComment, element[1]):
                    continue    # skip to next line

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
                            print("counted the wrong number of indices")
                            print("DEBUG ",dataset.loc[(dataset["Filename"] == name) & (dataset["Line number"] == element[0])])
                        ind = ind[0]
                        # update
                        dataset.at[ind, "Change type"].append(change)   # lista cambiamenti [ADD,DELETE,DELETE...
                        dataset.at[ind, "Code"].append(element[1])      # new code
                        dataset.at[ind, "Tokens"].append(tokens)        # token new code
                        dataset.at[ind, "NumEdit"] = dataset.at[ind, "NumEdit"] + 1     # numero modifiche subite
                # Update Variabili Instanze Set
                if matchInstAss:
                    variables = addVariables(variables, tokens, name)
                # Update Methodi Set
                if matchMethodCall:
                    if i < cutOffPoint:
                        activeClass = getActiveClass(classesInAdded, element[0])
                    else:
                        activeClass = getActiveClass(classesInDeleted, element[0])
                    methods = addMethods(methods, variables, tokens, name, element[0], activeClass)

dataset.set_index(["Filename", "Line number"], inplace=True)
dataset.sort_index(inplace=True)
# dataset.to_csv("commitTable.csv")
# dataset.to_excel("commitTable.xlsx")

method_count = methods.value_counts(["MethodName", "Class", ])
method_count.rename("Count", inplace=True)
classes = pd.Series(data=[[] for ind in range(len(method_count))], index=method_count.index)
for i in method_count.index:
    temp = methods.loc[methods["MethodName"] == i[0]]
    for j in temp.index:
        if temp.loc[j]["CallingClass"] not in classes[i]:
            classes[i].append(temp.loc[j]["CallingClass"])
classes.rename("CallingClasses", inplace=True)
method_count = pd.DataFrame(method_count)
method_count = pd.concat([method_count, classes], axis=1)
method_count.reset_index(inplace=True)
method_count.to_csv("methodTable.csv", index=False)
method_count.to_excel("methodTable.xlsx", index=False)
