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

# test
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
            # print("===========================================================")
            # se è stato modificato un file .java
            if (file.change_type.name == "ADD" or file.change_type.name == "MODIFY" or file.change_type.name == "DELETE") \
                    and file.filename[-5:] == ".java":

                # Info
                name = file.filename
                logger.info(f'FileName: {name}')  # name file
                # print(name)
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
                # per ciascuna chiamata API
                for rowmethod in methodfile.itertuples(index=True, name='Pandas'):
                    # Set esito new Metrica
                    esitoMone = 0
                    esitoMtwo = False
                    esitoMthree = 0

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


                        # METRICA 2
                        # print("riga con API", rowmethod.Line)
                        # print("righe modificate prima", righenear)
                        if righenear:
                            if rowmethod.Line == righenear[-1][0]:
                                for tok in rowmethod.Token_Method:
                                    if tok[0] in righenear[-1][1]:
                                        esitoMtwo = True

                    # METRICA 3
                    # per ciascun method o variabile (riferimento all'uso dell' API)
                    for tokenapi in rowmethod.Token_Method:

                        if (tokenapi[1] == "Variable" or tokenapi[1] == "Method"):
                            #print("ricerco ", tokenapi)
                            #print("in: ", righenear)
                            foundriferimenti = len([s for s in righenear if tokenapi[0] in s[1]])
                            if esitoMthree < foundriferimenti:
                                esitoMthree = foundriferimenti
                            # tutte le occorrenze di variabili o metodi presenti nelle righe precedenti alla chiamata
                            # API presente in rowmethod
                            #print("TROVATO",foundriferimenti)
                    newmetric.loc[len(newmetric.index)] = [commithash[-5:], commitime, name, rowmethod.Token_Method, classx, esitoMone, esitoMtwo, esitoMthree]


                # free methodclass
                del methodfile
                methodfile = pd.DataFrame(columns=["HashCommit", "Time", "Filename", "Line", "Token_Method", "Class"],
                                           index=[])
