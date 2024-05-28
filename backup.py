from pydriller import Repository
import logging
import pandas as pd
import warnings
import numpy as np

from src import Parse, Comment, ManageDataset, Class, ProgressionBar

logger = logging.getLogger(__name__)  # nome del modulo corrente (Api.py)

warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

def log(verbos):
    """ Setto i parametri per gestire il file di log (unici per modulo magari) """
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    if verbos:
            # StreamHandler: console
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
    # FileHandler: outputfile
    file_handler = logging.FileHandler('./log/Api.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def apiMining(variables, methods, repo, total_commits, verbose):
    # Setting log
    log(verbose)

    # Dizionario per memorizzare i DataFrame dei singoli file.java
    df_dict = {}

    # Core methods
    for commit in ProgressionBar.progressBar(Repository(path_to_repo=repo).traverse_commits(), total_commits,
                                             prefix='Progress:', suffix='Complete', length=50):
        # per ogni commit
        #print("# File modificati:", len(commit.modified_files))
        for file in commit.modified_files:
            # se è stato modificato un file .java
            if (file.change_type.name == "ADD" or file.change_type.name == "MODIFY" or file.change_type.name == "DELETE" or file.change_type.name == "RENAME") \
                    and file.filename[-5:] == ".java":

                # nome del file == classe?
                name = file.filename
                logger.info(f'FileName: {name}')  # name file
                change = file.change_type.name  # ADD - MODIFY ...
                logger.info(f'Change: {change}')  # tipo di modifica
                
                #print(name, change)
                # # LSHMinHash.java MODIFY
                #print(len(file.methods))
                #for method in file.methods:
                    #pass
                    #print(method.name, method.long_name, method.filename)
                    #print(method.parameters)
                    #print(method.length)
                
                # Se è un nuovo file modificato, crea un suo DataFrame
                if name not in df_dict:
                    # df_dict[name] = pd.DataFrame(columns=["Filename", "Change type", "Line number", "Code", "Tokens"], dtype=object)
                    df_dict[name] = pd.DataFrame(columns=["Filename", "Methods", "Change type", "Line number", "Code", "Tokens"], dtype=object)
                df = df_dict[name]

                # analisi fatta sul diff DELETE 
                if file.change_type.name == "DELETE":
                    #diff = file.diff_parsed
                    deleted_code = '\n'.join(line[1] for line in file.diff_parsed['deleted'])

                    #deleted_code = [line[1] + '\n' for line in file.diff_parsed['deleted']]
                    full_code = deleted_code
                else:
                    # o sull'intero codice sorgente dopo la modifica
                    full_code = file.source_code
                
                # can be _None_ if the file is deleted or only renamed
                if full_code is None:
                    continue

                # ogni riga aggiunta o cancellata nel file {'added': [(1, ''), (2, '// import java.util.*;'), (3,... 'delete': ...}
                #diff = file.diff_parsed
                #added = diff["added"]
                #if name == "LSHSuperBit.java": print(added)
                #deleted = diff["deleted"]
                #lines = added + deleted  # [(1, ''), (2, '// import java.util.*;'), (3,... puro codice solo modificato nel commit
                #cutOffPoint = len(added)
                # print("==================")

                # print(file.source_code)   # file.source_code = source code of the file (can be _None_ if the file is deleted or only renamed)
                # print(file.source_code_before)   # file.source_code_before = source code of the file before the change (can be _None_ if the file is added or only renamed)

                # lista (riga, classe) del codice corrente
                # classesInAdded = Class.lookForClasses(file.source_code)
                # lista (riga, classe) del codice come era prima
                #classesInDeleted = Class.lookForClasses(file.source_code_before)
                # status MultipleComment
                multicomments = False

                full_code = full_code.split('\n')
                for ind, row in enumerate(full_code):
                    # print(element[0], element[1])
                    
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
                        #if name == "LSHSuperBit.java": print("verifico", row)
                        
                        tokens = Parse.parseLine(row)
                        # eg invocazione di Metodo: Day arr[] = Day.values(); diventa
                        # [('Day', 'Class'), ('arr', 'Variable'), ('[', 'Separator'), (']', 'Separator'), ('=', 'Operator'),
                        # ('Day', 'Class'), ('.', 'Separator'), ('values', 'Method'), ('(', 'Separator'), (')', 'Separator'),
                        # (';', 'Separator')]
                        
                        # uso la str dei token utile per un confronto diretto se presente in pandas
                        tokens_str = str(tokens)
                        #if name == "LSHSuperBit.java": print("verifico", row)

                        # ricerca per tokens
                        if tokens_str in df['Tokens'].values:
                            # caso delete
                            if file.change_type.name == "DELETE":
                                df.loc[len(df.index)] = [name, methods, [change], [0], row, tokens_str]
                                continue
                            
                            # Se esiste una riga con quel valore di 'tokens', sovrascrivila: oppure skip
                            # Trova l'indice della riga dove 'Tokens' è uguale a 'tokens_str'
                            index = df[df['Tokens'] == tokens_str].index[0]
                            if ind not in df.at[index, "Line number"]:
                                df.at[index, "Line number"].append(ind)
                                # caso shift
                                if "SHIFT" not in df.at[index, "Change type"]:
                                    df.at[index, "Change type"].append("SHIFT")
                        
                        #existing_row = df[(df['Tokens'] == tokens_str) & (df['Change type'] == change)]
                        #existing_row = df[(df['Tokens'] == tokens_str)]
                        else:
                            methods = [token for token, token_type in tokens if token_type == 'Method']
                            if methods:
                                df.loc[len(df.index)] = [name, methods, [change], [ind], row, tokens_str]
                            else:
                                classe = [token for token, token_type in tokens if token_type == 'Class' or token_type == 'Function']
                                df.loc[len(df.index)] = [name, classe, [change], [ind], row, tokens_str]
                
                full_code = '' 
    return df_dict
                                                            