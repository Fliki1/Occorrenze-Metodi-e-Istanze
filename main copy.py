from pydriller import Repository, Git
import pandas as pd
import argparse
import logging
import gc, os

from src import Print, Api_copy, Near

# TODO: gestione casi di casting: LSHMinHash saved_lsh = (LSHMinHash) ois.readObject();

# create logger
logger = logging.getLogger(__name__)  # nome del modulo corrente (main.py): global logger

"""
    DataFrame di supporto per la gestione e analisi dei dati:
        dataset = tutte le linee di codice
        variables = associa ogni istanza alle sue classi di appartenenza
        methods = associa ogni metodo alla sua classe (in relazione all'istanza di appartenenza)
        newmetric = ricerca correlazione modifiche vicine a invocazione di librerie
"""
dataset = pd.DataFrame(columns=["Filename", "Change type", "Line number", "Code", "Tokens", "NumEdit"], index=[])
variables = pd.DataFrame(columns=["Filename", "Varname", "Vartype"], index=[])
methods = pd.DataFrame(columns=["Filename", "MethodName", "Class", "CallingClass", "Line number"], index=[])



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
        dataset = Api_copy.apiMining(variables, methods, repo, total_commits, verb)
        # New metric
        # Near.nearMining(newmetric, repo, total_commits, verb)

        # Save results
        for filename, df in dataset.items():
            #print(filename)
            if not os.path.exists("./results/" + commit.project_name):
                os.mkdir("./results/" + commit.project_name)
            # Printing Dataset
            #df.set_index(["Filename", "Line number"], inplace=True)
            #df.sort_index(inplace=True)
            df.to_csv("./results/" + commit.project_name + "/"+ filename[:-4]+"csv", index=False)


        # Reset Dataframe
        del dataset
        del variables
        del methods
        #del newmetric
        gc.collect()
        dataset = pd.DataFrame(columns=["Filename", "Change type", "Line number", "Code", "Tokens", "NumEdit"],
                               index=[])
        variables = pd.DataFrame(columns=["Filename", "Varname", "Vartype"], index=[])
        methods = pd.DataFrame(columns=["Filename", "MethodName", "Class", "CallingClass", "Line number"], index=[])


    logger.info('Fine del Hard Java API')
