from pydriller import Repository, Git
import pandas as pd
import argparse
import logging
import gc, os

from src import MethodOut2

# create logger
logger = logging.getLogger(__name__)  # nome del modulo corrente (main.py): global logger

"""
    DataFrame di supporto per la gestione e analisi dei dati:
        dataset = tutte le linee di codice
        variables = associa ogni istanza alle sue classi di appartenenza
        methods = associa ogni metodo alla sua classe (in relazione all'istanza di appartenenza)
        newmetric = ricerca correlazione modifiche vicine a invocazione di librerie
"""


def remove_duplicates(urls):
    """ Return list dei urls non duplicati """
    logger.info('Rimozione url duplicati')
    return list(set(urls))


def get_git_urls():
    """ Domanda all'user i git da analizzare, return lista url leciti """
    url_input = input("Enter Gits Repositories: ")
    urls = url_input.split(", ")
    urls_not_duplicate = remove_duplicates(urls)  # remove duplicate urls
    return urls_not_duplicate


def log(verbos):
    """ Setto i parametri per gestire il file di log """
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    if verbos:
        # create console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    # FileHandler: outputfile
    file_handler = logging.FileHandler('./log/main.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def arg_parse():
    """ Verifico la possibile chiamata verbose """
    parser = argparse.ArgumentParser(prog="Hard Java API",
                                     description="Script che cerca di rilevare la difficoltà di utilizzo delle librerie"
                                                 "Java")
    parser.add_argument("-v", "--verbose", help="restituisce output verboso", action="store_true")
    args = parser.parse_args()
    return args.verbose

def path(repo_name):
    if not os.path.exists("./results/" + repo_name):
        os.mkdir("./results/" + repo_name)

def saving(esiti):
    dati = []

    # Itera su ogni classe, metodo e tupla
    for classe, metodi in esiti.items():
        for metodo, tuple in metodi.items():
            for riga_di_codice, tag in tuple:
                # Aggiungi i dati a una riga
                riga = [classe, metodo, riga_di_codice, tag]
                dati.append(riga)

    # Crea un DataFrame da dati
    df = pd.DataFrame(dati, columns=['Classe', 'Metodo', 'Riga di Codice', 'Tag'])

    # Salva il DataFrame in un file CSV
    df.to_csv(commit.project_name + "_out_2.csv", index =False)
        


if __name__ == "__main__":
    # Log: gestisce sia la console che il salvataggio dei log [-v] (diversi per modulo)
    verb = arg_parse()  # args parse: verbose choise ?
    log(verb)  # log file

    logger.info('Inizio Hard Java API')
    urls = get_git_urls()

    # Invocazione metodo con (urls, verbose)
    for repo in urls:
        # Set ProgressionBar setup
        tmp_repo = Repository(path_to_repo=repo).traverse_commits()
        commit = next(tmp_repo)
        logger.info(f'Project: {commit.project_name}')  # project name
        print(f'(Hard API Java) Project: {commit.project_name}')
        git = Git(commit.project_path)
        logger.debug(f'Project: {commit.project_name} #Commits: {git.total_commits()}')  # total commits
        total_commits = git.total_commits()

        # Core process
        # dataset = Api_mod.apiMining(variables, methods, repo, total_commits, verb)
        
        MethodOut2.istanceMining(repo, total_commits)
        MethodOut2.methodMining(repo, total_commits)
        esiti = MethodOut2.methodScanning(repo, total_commits)

        saving(esiti)
        
        gc.collect()

    logger.info('Fine del Hard Java API')
