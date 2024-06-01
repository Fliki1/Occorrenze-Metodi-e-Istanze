from pydriller import Repository, Git
import pandas as pd
import argparse
import logging
import gc, os

from src import MethodParam3

# create logger
logger = logging.getLogger(__name__)  # nome del modulo corrente (main.py): global logger


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
    df.to_csv(commit.project_name + "_all_1.csv", index =False)
        


if __name__ == "__main__":

    urls = get_git_urls()

    # Invocazione metodo con (urls)
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
        
        MethodParam3.methodMining(repo, total_commits)
        esiti = MethodParam3.methodParamScanning(repo, total_commits)

        #saving(esiti)
        
        gc.collect()

    logger.info('Fine del Hard Java API')
