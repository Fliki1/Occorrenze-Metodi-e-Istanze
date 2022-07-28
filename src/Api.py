from pydriller import Repository
import logging

from src import Parse, Comment, ManageDataset, Class, ProgressionBar

logger = logging.getLogger(__name__)  # nome del modulo corrente (Api.py)

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


def apiMining(dataset, variables, methods, repo, total_commits, verbose):
    # Setting log
    log(verbose)

    # Core methods
    for commit in ProgressionBar.progressBar(Repository(path_to_repo=repo).traverse_commits(), total_commits,
                                             prefix='Progress:', suffix='Complete', length=50):
        # per ogni commit
        for file in commit.modified_files:
            # se è stato modificato un file .java
            if (file.change_type.name == "ADD" or file.change_type.name == "MODIFY" or file.change_type.name == "DELETE") \
                    and file.filename[-5:] == ".java":

                # nome classe
                name = file.filename
                logger.info(f'FileName: {name}')  # name file
                change = file.change_type.name  # ADD - MODIFY ...
                logger.info(f'Change: {change}')  # tipo di modifica

                # ogni riga aggiunta o cancellata nel file {'added': [(1, ''), (2, '// import java.util.*;'), (3,... 'delete': ...}
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

                    tokens = Parse.parseLine(element[1])
                    # eg invocazione di Metodo: Day arr[] = Day.values(); diventa
                    # [('Day', 'Class'), ('arr', 'Variable'), ('[', 'Separator'), (']', 'Separator'), ('=', 'Operator'),
                    # ('Day', 'Class'), ('.', 'Separator'), ('values', 'Method'), ('(', 'Separator'), (')', 'Separator'),
                    # (';', 'Separator')]

                    if matchMethodCall or matchInstAss:
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
                        methods = ManageDataset.addMethods(methods, variables, tokens, name, element[0], activeClass,
                                                           verbose)
