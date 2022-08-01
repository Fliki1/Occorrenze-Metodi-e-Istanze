from pydriller import Repository
import logging
import pandas as pd
import re
from itertools import groupby
from operator import itemgetter

from src import Parse, Comment, ManageDataset, Class, ProgressionBar

logger = logging.getLogger(__name__)  # nome del modulo corrente (Near.py)

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
    file_handler = logging.FileHandler('./log/Near.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def remove_chars(entry):
    x = re.sub('\W', ' ', entry)
    return(x)

def get_range(dictionary, end):
    return [i for i in dictionary if i[0] <= end]


def getlistrighe(righenear):
    return [rig[0] for rig in righenear]

def consecutive_line_mod(listrighe, rigaAPI):
    """
    Conteggio righe modificate consecutive prima della invocazione a libreria/metodo presente nel codice
    :param listrighe: righe modificate prima della invocazione a metodo
    :param rigaAPI: riga in cui è presente una chiamata API
    :return: il più grande conteggio di righe modificate prima consecutive
    """
    esito = 0
    for k, g in groupby(enumerate(listrighe), lambda ix: ix[0] - ix[1]):
        conse = list(map(itemgetter(1), g))
        if conse[-1] == rigaAPI or conse[-1] == rigaAPI - 1:
            if len(conse) > esito:
                esito = len(conse)
    return esito


def nearMining(newmetric, repo, total_commits, verbose):
    # Setting log
    log(verbose)

    # finestra di righe da controllare
    nearline = 5

    # Core methods
    for commit in ProgressionBar.progressBar(Repository(path_to_repo=repo).traverse_commits(), total_commits,
                                             prefix='Progress:', suffix='Complete', length=50):

        # dataframe di supporto
        methodfile = pd.DataFrame(columns=["HashCommit", "Time", "Filename", "Line", "Token_Method", "Class"], index=[])

        # per ogni commit
        for file in commit.modified_files:
            #print("===========================================================")
            # se è stato modificato un file .java
            if (file.change_type.name == "ADD" or file.change_type.name == "MODIFY" or file.change_type.name == "DELETE") \
                    and file.filename[-5:] == ".java":

                # Info
                name = file.filename
                logger.info(f'FileName: {name}')  # name file
                #print(name)
                change = file.change_type.name  # ADD - MODIFY ...
                logger.info(f'Change: {change}')  # tipo di modifica
                commithash = commit.hash
                logger.info(f'CommitHash: {commithash}')  # hash commit
                commitime = commit.committer_date.strftime("%d/%m/%Y")
                logger.info(f'Time commit: {commitime}')    # time commit

                # Setting
                multicomments = False
                # lista (riga, classe) del codice corrente
                classes = Class.lookForClasses(file.source_code)
                diff = file.diff_parsed
                added = diff["added"]
                deleted = diff["deleted"]
                adel = added + deleted


                # Se è un file cancellato o vuoto: skip
                if file.source_code == None:
                    continue

                # codice per riga
                lines = file.source_code.split("\n")
                # Ricerca di invocazione metodi nel codice corrente
                for i, element in enumerate(lines):
                    #print("riga - codice ", i, element)

                    # ricerca nella linea la presenza di pluri-commento
                    if Comment.isStartMultipleComment(element):
                        multicomments = True
                    if Comment.isEndMultipleComment(element):
                        multicomments = False
                    if multicomments:
                        continue

                    # ricerca nella linea la presenza di invocazione singolo-commento - metodo
                    if Comment.isSingleComment(element):
                        element = Comment.removeComment(element)
                        logger.info(f'No commento: {element}')  # no commento

                    # Se trovo un metodo
                    matchMethodCall = Comment.reMethodCall.search(element)

                    if matchMethodCall:
                        # Scompongo la linea in token
                        tokens = Parse.parseLine(element)
                        classx = Class.getActiveClass(classes, i)    # TODO: evitabile?
                        methodfile.loc[len(methodfile.index)] = [commithash[-5:], commitime, name, i, tokens, classx]
                        #print("metodo ", element)

                # ==============================================================================================
                # righe modificate prima del metodo

                # per ciascuna chiamata API
                for rowmethod in methodfile.itertuples(index=True, name='Pandas'):
                    # print(row.Filename, row.Line)  # , row.Token_Method)
                    # estrapoliamo le sole modifiche prima dell'invozaione del metodo
                    righenear = get_range(adel, rowmethod.Line)
                    # se non vuoto
                    if righenear:
                        # restringo agli ultimi {nearline} modifiche
                        righenear = righenear[-nearline:]


                    # METRICA 1
                    # ricerca di num righe modificate consecutivamente prima all'invocazione dell'API
                    #print("riga con API", rowmethod.Line)
                    #print("righe modificate prima", righenear)
                    listrighe = getlistrighe(righenear)
                    # print(listrighe)
                    # consecutive righe modificate rispetto alla riga di invocazione metodo
                    esitoMone = consecutive_line_mod(listrighe, rowmethod.Line)
                    # TODO: print("metrica 1:",esitoMone)


                    # METRICA 2
                    # print("riga con API", rowmethod.Line)
                    # print("righe modificate prima", righenear)
                    # if rowmethod.riga == last di righenear
                    esitoMtwo = False
                    if righenear:
                        if rowmethod.Line == righenear[-1][0]:
                            for tok in rowmethod.Token_Method:
                                if tok[0] in righenear[-1][1]:
                                    esitoMtwo = True
                    # TODO: esitoMtwo

                    # METRICA 3
                    # per ciascun method o variabile (riferimento all'uso dell' API)
                    for tokenapi in rowmethod.Token_Method:
                        foundriferimenti = []
                        if (tokenapi[1] == "Variable" or tokenapi[1] == "Method"):
                            #print("ricerco ", tokenapi)
                            #print("in: ", righenear)
                            foundriferimenti = [s for s in righenear if tokenapi[0] in s[1]]
                            # tutte le occorrenze di variabili o metodi presenti nelle righe precedenti alla chiamata
                            # API presente in rowmethod
                            #print("TROVATO",foundriferimenti)
                        newmetric.loc[len(newmetric.index)] = [commithash[-5:], commitime, name, tokens, classx, \
                                                              esitoMone, esitoMtwo, len(foundriferimenti)]

                        # TODO: salvare la lunghezza di questi trovati!!!!!!!!!!! foundriferimenti len()


                # free methodclass e linefile
                del methodfile
                methodfile = pd.DataFrame(columns=["HashCommit", "Time", "Filename", "Line", "Token_Method", "Class"],
                                           index=[])



                """
                # Linee modificate del file
                for index, lineadel in enumerate(adel):
                    # Setting Commenti in linee modificate
                    multicomments = False

                    # ricerca nella linea la presenza di pluri-commento
                    if Comment.isStartMultipleComment(lineadel[1]):
                        multicomments = True
                    if Comment.isEndMultipleComment(lineadel[1]):
                        multicomments = False
                    if multicomments:
                        continue

                    # ricerca nella linea la presenza di invocazione singolo-commento - metodo
                    if Comment.isSingleComment(lineadel[1]):
                        #print("commento lineadel ",lineadel)
                        # converto la tupla element in lista per poterla modificare e togliere il commento di troppo
                        my_lineadel = list(lineadel)
                        my_lineadel[1] = Comment.removeComment(my_lineadel[1])
                        lineadel = tuple(my_lineadel)
                        logger.info(f'No commento in ADD-DEL: {lineadel[1]}')  # no commento nelle linee modificate
                        #print("no commento lineadel ", lineadel)

                    # Caso limite?
                    my_point_lineadel = list(lineadel)
                    my_point_lineadel[1] = remove_chars(my_point_lineadel[1])
                    lineadel = tuple(my_point_lineadel)

                    print(f"TOKENIZZO {index}/{len(adel)}", lineadel[1])
                    tokensLine = Parse.parseNormLine(lineadel[1])
                    print("TOKENIZZATOOOO: ",tokensLine)
                    #linefile.loc[len(linefile.index)] = [commithash[-5:], commitime, name, lineadel[0], tokensLine]
                """
                #print(methodfile)
                #print(linefile)


            """
                # ogni riga aggiunta o cancellata nel file 
                # {'added': [(1, ''), (2, '// import java.util.*;'), (3,... 'delete': ...}
                diff = file.diff_parsed
                added = diff["added"]
                deleted = diff["deleted"]
                lines = added + deleted  # [(1, ''), (2, '// import java.util.*;'), (3,... puro codice solo modificato nel commit
                cutOffPoint = len(added)
                # print("==================")

                # print(file.source_code)   # file.source_code = source code of the file (can be _None_ if the file is deleted or only renamed)
                # print(file.source_code_before)   # file.source_code_before = source code of the file before the change (can be _None_ if the file is added or only renamed)

                # lista (riga, classe) del codice corrente
                classesInAdded = Class.lookForClasses(file.source_code)
                # lista (riga, classe) del codice come era prima
                classesInDeleted = Class.lookForClasses(file.source_code_before)
                # status MultipleComment
                multicomments = False

                for i, element in zip(range(len(lines)), lines):
                    # print("added + deleted ", i, element)

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
                        logger.info(f'Riga con commento: {i},{element}')  # commento
                        # print("added + deleted ", i, element)
                        logger.info(f'No commento: {element[1]}')  # no commento
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
                            ind = dataset.loc[
                                (dataset["Filename"] == name) & (dataset["Line number"] == element[0])].index
                            if len(ind) != 1:
                                # ind = lista di indici di dataset in cui è presente lo stesso riferimento cercato: ERRORE
                                logger.info(f'Warning: counted the wrong number of indices')  # warning
                                print("Warning: counted the wrong number of indices")
                                logger.debug(f'"DEBUG {dataset.loc[(dataset["Filename"] == name) & (dataset["Line number"] == element[0])]}')
                                #print("DEBUG ", dataset.loc[(dataset["Filename"] == name) & (dataset["Line number"] == element[0])])
                            ind = ind[0]
                            # update
                            dataset.at[ind, "Change type"].append(change)  # lista cambiamenti [ADD,DELETE,DELETE...
                            dataset.at[ind, "Code"].append(element[1])  # new code
                            dataset.at[ind, "Tokens"].append(tokens)  # token new code
                            dataset.at[ind, "NumEdit"] = dataset.at[ind, "NumEdit"] + 1  # numero modifiche subite

                        # Update Variabili Instanze Set
                        if matchInstAss:
                            logger.info(f'Variabile:, {element[1]}')  # Variabile found
                            # print("VARIABILE: ", element[1])
                            variables = ManageDataset.addVariables(variables, tokens, name, verbose)
                        # Update Metodi Set
                        if matchMethodCall:
                            logger.info(f'Methodo:, {element[1]}')  # Method found
                            # print("METODO: ", element[1])
                            if i < cutOffPoint:
                                activeClass = Class.getActiveClass(classesInAdded, element[0])
                            else:
                                activeClass = Class.getActiveClass(classesInDeleted, element[0])
                            methods = ManageDataset.addMethods(methods, variables, tokens, name, element[0],
                                                               activeClass, verbose)
            """

