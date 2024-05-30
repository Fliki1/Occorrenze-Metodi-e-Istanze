from pydriller import Repository
import pandas as pd
import numpy as np
import javalang

from src import Parse, Comment, ProgressionBar


# Dizionario per memorizzare tutte le istanze presenti nel progetto
dict_ist = {}

"""
dict_ist = {
    "file1.java": {
        "instance1": "Class1",
        "instance2": "Class2"
    },
    "file2.java": {
        "instance3": "Class3"
    }
}
"""
""" ricerca di tutte le istanze presenti all'interno di tutte le classi (file.java) """
def istanceMining(repo, total_commits):
    for commit in ProgressionBar.progressBar(Repository(path_to_repo=repo).traverse_commits(), total_commits,
                                             prefix='Istance list:', suffix='Complete', length=50):
        for file in commit.modified_files:
            if file.filename[-5:] == ".java":
                name = file.filename                
                # nuova classe
                if name not in dict_ist:
                    dict_ist[name] = {}

                full_code = file.source_code
                # can be _None_ if the file is deleted or only renamed
                if full_code is None:
                    continue

                tree = javalang.parse.parse(full_code)
                for path, node in tree:
                    if isinstance(node, javalang.tree.VariableDeclarator) and isinstance(node.initializer, javalang.tree.ClassCreator):
                        if node.name not in dict_ist[name]:
                            dict_ist[name][node.name] = node.initializer.type.name
    #print(dict_ist)


dict_method = {}
"""
{
    'file1.py': ['metodo1', 'metodo2', 'metodo3'],
    'file2.py': ['metodoA', 'metodoB'],
    'file3.py': ['metodoX', 'metodoY', 'metodoZ'],
    ...
}
"""

""" ricerca di tutti i metodi presenti all'interno di una classe """
def methodMining(repo, total_commits):
    
    for commit in ProgressionBar.progressBar(Repository(path_to_repo=repo).traverse_commits(), total_commits,
                                             prefix='Method list:', suffix='Complete', length=50):
        
        for file in commit.modified_files:
            if file.filename[-5:] == ".java":
                name = file.filename                
                # Se è un nuovo file modificato, crea un suo DataFrame
                if name not in dict_method:
                    dict_method[name] = []

                for method in file.changed_methods:
                    if method.name not in dict_method[name]:
                        dict_method[name].append(method.name)

    #methodScanning(repo=repo, total_commits=total_commits)

"""
ricerca ESTERNA
"""
# Dizionario per memorizzare lista modifiche dei singoli file.java
dict_mod = {}

def methodScanning(repo, total_commits):
    # dati le classi del progetto (nomi file.java)
    for classe in dict_method:
        for commit in ProgressionBar.progressBar(Repository(path_to_repo=repo).traverse_commits(), total_commits,
                                             prefix=classe+' scan:', suffix='Complete', length=50):
            # ricerco l'uso dei suoi metodi tra le modifiche effettuate
            for file in commit.modified_files:
                # modifica avvenuta su file diverso dalla classe di studio
                if file.filename[-5:] == ".java" and file.filename != classe:
                    name= file.filename
                    change= file.change_type.name # ADD - MODIFY - DELETE - RENAME

                    # analisi fatta sul diff DELETE 
                    if change == "DELETE":
                        deleted_code = '\n'.join(line[1] for line in file.diff_parsed['deleted'])
                        full_code = deleted_code
                    else:
                        # o sull'intero codice sorgente dopo la modifica: per gestire i merge change
                        full_code = file.source_code

                    # can be _None_ if the file is deleted or only renamed
                    if full_code is None:
                        continue
                    
                    # studio dell'intero codice
                    tree = javalang.parse.parse(full_code)
                    code_in_lines = full_code.split('\n')
                    for path, node in tree:
                        # modifica di una invocazione
                        if isinstance(node, javalang.tree.MethodInvocation):
                            if node.qualifier:
                                line_number = node.position[0]  # La posizione è una tupla (linea, colonna)
                                line = code_in_lines[line_number - 1]  # -1 perché gli indici delle liste iniziano da 0
                                print(f"Ist: {node.qualifier}, Method: {node.member}, Code: {line}")
                                
                
def methodScanningBrutto(repo, total_commits, ciao):
    # Core methods
    for commit in ProgressionBar.progressBar(Repository(path_to_repo=repo).traverse_commits(), total_commits,
                                             prefix='Method scan:', suffix='Complete', length=50):
        # per ogni commit
        for file in commit.modified_files:
            # se è stato modificato un file .java
            if file.filename[-5:] == ".java":

                name = file.filename
                change = file.change_type.name  # ADD - MODIFY - DELETE - RENAME
                
                if name not in dict_mod:
                    dict_mod[name] = []
                
                # analisi fatta sul diff DELETE 
                if file.change_type.name == "DELETE":
                    deleted_code = '\n'.join(line[1] for line in file.diff_parsed['deleted'])
                    full_code = deleted_code
                else:
                    # o sull'intero codice sorgente dopo la modifica
                    full_code = file.source_code

                # can be _None_ if the file is deleted or only renamed
                if full_code is None:
                    continue

                # status MultipleComment
                multicomments = False

                full_code = full_code.split('\n')
                for ind, row in enumerate(full_code):                    
                    # ricerca nella linea la presenza di commento o pluri-commento: and skip it
                    if Comment.isStartMultipleComment(row):  # è l'inizio di un commento multiplo?
                        multicomments = True
                    if Comment.isEndMultipleComment(row):    # è la fine di un commento multiplo?
                        multicomments = False
                    if multicomments:   # skip fino a quando non si arriva alla fine di un commento multiplo
                        continue
                    if Comment.isSingleComment(row):
                        continue

                    matchMethodCall = Comment.reMethodCall.search(row)
                    matchInstAss = Comment.reInstAss.search(row)

                    if matchMethodCall or matchInstAss:                        
                        tokens = Parse.parseLine(row)
                
                # Tipo di modifica e metodi modificati
                for metodo in file.changed_methods:
                    # print(file.change_type.name, metodo.name)
                    #df = df.append({"Filename": name, "Methods": metodo.name, "Change type": file.change_type.name}, ignore_index=True)

                    if metodo.name in df['Methods'].values:
                        index = df[df['Methods'] == metodo.name].index[0]
                    else:

                        # new method
                        if file.change_type.name == "ADD":
                            df.loc[len(df.index)] = switch_newMethod(file.change_type.name, name, metodo.name)[name, metodo.name, 1, 0, 0]
                        if file.change_type.name == "DELETE":
                            df.loc[len(df.index)] = [name, metodo.name, 0, 0, 1]
                        


    return df_dict