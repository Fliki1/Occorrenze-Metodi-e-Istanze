from pydriller import Repository
import pandas as pd
import pprint

from src import ProgressionBar


dict_method = {}
"""
{
    'file1.java': ['metodo1', 'metodo2', 'metodo3'],
    'file2.java': ['metodoA', 'metodoB'],
    'file3.java': ['metodoX', 'metodoY', 'metodoZ'],
    ...
}
"""

""" ricerca di tutti i metodi presenti all'interno di una classe, tiene il conteggio delle classi presenti """
def methodMining(repo, total_commits):
    
    for commit in ProgressionBar.progressBar(Repository(path_to_repo=repo).traverse_commits(), total_commits,
                                             prefix='Method list:', suffix='Complete', length=50):
        
        for file in commit.modified_files:
            if file.filename[-5:] == ".java":
                name = file.filename
                # Se è un nuovo file modificato
                if name not in dict_method:
                    dict_method[name] = []

                for method in file.changed_methods:
                    if method.name not in dict_method[name]:
                        separation = method.name.split('::')
                        dict_method[name].append(separation[1])

    #print(dict_method)

"""
ricerca cambiamenti dell'interfaccia di una classe:
    aggiunta/rimozione di parametri in ingresso ad un metodo,
    aggiunta di metodi
    rimozione di metodi
annotare per ogni classe i cambiamenti ai suoi metodi diretti
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

def methodParamScanning(repo, total_commits):

    # dati le classi del progetto (nomi file.java)
    #for classe in dict_method: TODO
    it = iter(dict_method)
    next(it)
    classe = next(it)    # todo remove

    # setup: crea la classe se non esiste già
    if classe not in dict_mod:
        dict_mod[classe] = {}

    for commit in ProgressionBar.progressBar(Repository(path_to_repo=repo).traverse_commits(), total_commits,
                                            prefix=classe+' scan:', suffix='Complete', length=50):
        # ricerco l'uso dei suoi metodi tra le modifiche effettuate
        for file in commit.modified_files:
            # studio le modifiche della classe sotto studio
            if file.filename == classe:

                # controllo metodi con il precedente commit: ricerca di metodi eliminati
                lista_metodi_commit_precedente = [met.long_name for met in file.methods_before]
                #print("PRIMA:", lista_metodi_commit_precedente)
                lista_metodi_cur_commit = [met.long_name for met in file.methods]
                #print("DOPO:", lista_metodi_cur_commit)
                # old meth to delete
                bef_met_long_name_missing = [method for method in lista_metodi_commit_precedente if method not in lista_metodi_cur_commit]
                # old meth to add (new ADD same method recreated)
                aft_met_long_name_add = [method for method in lista_metodi_cur_commit if method not in lista_metodi_commit_precedente]

                #print("DEL ",bef_met_long_name_missing)
                if len(bef_met_long_name_missing) > 0:  # confronto lo faccio su long_name uso parametri per gestire metodi omonimi 
                    for method_miss in bef_met_long_name_missing:
                        method_mod_param = method_miss.split('::')
                        method_name = method_mod_param[1].split('(')
                        dict_mod[classe][method_name[0]].append((method_mod_param[1].strip(), 0, [], "DEL")) # del
                #print("MODIFICATI-ALL:", [m.long_name for m in file.changed_methods])
                #print("MODIFICATI-DEL:", [m.long_name for m in file.changed_methods if m.long_name not in bef_met_long_name_missing])
                #print("===============")
                for method_mod in file.changed_methods:
                    if method_mod.long_name not in bef_met_long_name_missing:   # i delete method sono considerati come mod method
                        # new entry
                        method_mod_name = method_mod.name.split('::')
                        method_mod_param = method_mod.long_name.split('::')
                        if method_mod_name[1] not in dict_mod[classe]:
                            #print("nuovo metodo ADD: ", method_mod_param[1].strip(), "not in DEL ", bef_met_long_name_missing)
                            dict_mod[classe][method_mod_name[1]] = []
                            dict_mod[classe][method_mod_name[1]].append((method_mod_param[1].strip(), method_mod.nloc, method_mod.parameters, "ADD")) # new
                        else:
                            # case: metodo già presente, verifico se diverso costrutto e params confrontando direttamente long_name (evito shift o metodi nloc modificati) # mod
                            if dict_mod[classe][method_mod_name[1]][0][0] != method_mod_param[1].strip():
                                dict_mod[classe][method_mod_name[1]].append((method_mod_param[1].strip(), method_mod.nloc, method_mod.parameters, "MOD")) # mod
                                continue
                            
                            # i metodi nuovi da ADD (già visti in passato). controllo forse evitabile e append direttamente TODO
                            if method_mod.long_name in aft_met_long_name_add:
                                dict_mod[classe][method_mod_name[1]].append((method_mod_param[1].strip(), method_mod.nloc, method_mod.parameters, "ADD")) # add


                
    
    # ordino per riga
    for classe, metodi in dict_mod.items():
        for metodo, tuple in metodi.items():
            # Ordina le tuple
            tuple.sort()
    #pprint.pprint(dict_mod, indent=4)
    
    return dict_mod