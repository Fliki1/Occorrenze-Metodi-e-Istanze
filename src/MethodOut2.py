from pydriller import Repository
import pandas as pd
import javalang

from src import ProgressionBar


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

                try:
                    tree = javalang.parse.parse(full_code)
                    for path, node in tree:
                        if isinstance(node, javalang.tree.VariableDeclarator) and isinstance(node.initializer, javalang.tree.ClassCreator):
                            if node.name not in dict_ist[name]:
                                dict_ist[name][node.name] = node.initializer.type.name
                except javalang.parser.JavaSyntaxError:
                    print(f"\nErrore di sintassi del file {name} di commit '{commit.hash}'")
    #print(dict_ist)


dict_method = {}
"""
{
    'file1.java': ['metodo1', 'metodo2', 'metodo3'],
    'file2.java': ['metodoA', 'metodoB'],
    'file3.java': ['metodoX', 'metodoY', 'metodoZ'],
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
                        separation = method.name.split('::')
                        if len(separation) > 1:
                            dict_method[name].append(separation[1])
                        else:
                            dict_method[name].append(separation[0])

    #print(dict_method)
    #methodScanning(repo=repo, total_commits=total_commits)

"""
ricerca ESTERNA
"""
# Dizionario per memorizzare lista modifiche dei singoli file.java
dict_mod = {}

"""
dict_mod = {
    "classefocus1.java": {
        'metodo1': [
            ('riga di codice 1', 'tag per riga di codice 1'),
            ('riga di codice 2', 'tag per riga di codice 2'),
            # ... altre tuple di (codice, tag) ...
        ],
        # ... altri metodi ...
    },
    # ... altre classi ...
}
"""

def methodScanning(repo, total_commits):

    # dati le classi del progetto (nomi file.java)
    for ind, classe in enumerate(dict_method):

        # setup: crea la classe se non esiste già
        if classe not in dict_mod:
            dict_mod[classe] = {}

        for commit in ProgressionBar.progressBar(Repository(path_to_repo=repo).traverse_commits(), total_commits,
                                             prefix=str(ind)+"/"+str(len(dict_method))+" "+classe+' scan:', suffix='Complete', length=50):
            # ricerco l'uso dei suoi metodi tra le modifiche effettuate
            for file in commit.modified_files:
                # modifica avvenuta su file diverso dalla classe di studio
                if file.filename[-5:] == ".java" and file.filename != classe:
                    name= file.filename
                    change= file.change_type.name # ADD - MODIFY - DELETE - RENAME

                    # analisi fatta sul diff DELETE: è una sola cancellazione di codice
                    if change == "DELETE":
                        deleted_code = '\n'.join(line[1] for line in file.diff_parsed['deleted'])
                        full_code = deleted_code
                    else:
                        # o sull'intero codice sorgente dopo la modifica: per gestire i merge change
                        full_code = file.source_code

                    # can be _None_ if the file is deleted or only renamed
                    if full_code is None:
                        continue
                    
                    try:
                        # studio dell'intero codice
                        tree = javalang.parse.parse(full_code)
                        code_in_lines = full_code.split('\n')
                        for path, node in tree:
                            # modifica di una invocazione
                            if isinstance(node, javalang.tree.MethodInvocation):
                                if node.qualifier:
                                    line_number = node.position[0]  # La posizione è una tupla (linea, colonna)
                                    line = code_in_lines[line_number - 1].strip()  # -1 perché gli indici delle liste iniziano da 0
                                    #print(f"Ist: {node.qualifier}, Method: {node.member}, Code: {line}")
                                    # verifico che l'istanza è della classe di turno e che il metodo sia della classe di studio
                                    #if node.qualifier in dict_ist[name]
                                    # che il metodo sia della classe di studio
                                    # if node.member in dict_method[classe]:
                                    # verifico se la classe dell'istanza è la stessa sotto analisi
                                    # if classe[:-5] == dict_ist[name][node.qualifier]:
                                    #if classe[:-5] == dict_ist[name][node.qualifier] and node.member in dict_method[classe]:
                                    #    print(f"File: {classe}/{name} Ist: {node.qualifier}, Method: {node.member}, di {dict_ist[name][node.qualifier]} Code: {line}")

                                    if node.qualifier in dict_ist[name] and node.member in dict_method[classe] and classe[:-5] == dict_ist[name][node.qualifier]:
                                        #print(f"File: {classe}/{name} Ist: {node.qualifier}, Method: {node.member}, di {dict_ist[name][node.qualifier]} Code: {line}")

                                        #setup: metodo della classe di studio
                                        if node.member not in dict_mod[classe]:
                                            dict_mod[classe][node.member] = []


                                        # SE DELETE inserisco come new entry sempre
                                        if change == "DELETE":
                                            dict_mod[classe][node.member].append((line, change))
                                            continue
                                        
                                        # controllo se non è già presente: lo crea (evito shift case)
                                        if not any(row_in_table == line for row_in_table, tag in dict_mod[classe][node.member]):
                                            dict_mod[classe][node.member].append((line, change))
                    
                    except javalang.parser.JavaSyntaxError:
                        print(f"\nErrore di sintassi del file {name} di commit '{commit.hash}'")


    #print(dict_mod)
    # ordino per riga
    for classe, metodi in dict_mod.items():
        for metodo, tuple in metodi.items():
            # Ordina le tuple
            tuple.sort()

    return dict_mod