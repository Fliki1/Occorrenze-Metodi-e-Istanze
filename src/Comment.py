import re

# Espressioni regolari per selezionare le righe di codice contenenti instanziazioni di oggetti o chiamate di metodi

reMethodCall = re.compile('\s*\S+\s*\.\s*\S+\s*\(.*\).*;\s*')   # chiamate a metodo
#reInstAss = re.compile('\s*\S+\s*=\s*new\s*\S+\(.*\)\s*;\s*')   # new istanza
reInstAss = re.compile('^(\s*\S+\s*=\s*)?new\s*\S+\(.*\)\s*;\s*')   # new istanza anche senza (= new) ma solo new


# Espressioni regolari per i commenti

reIsComment = []
reIsComment.append(re.compile('\s*//.*'))                       # //       commento singola riga
reIsComment.append(re.compile('\s*/\*.*'))                      # /* start commento di plurime righe
reIsComment.append(re.compile('\s*\*/'))                        # */ end   commento di plurime righe

# reClassDeclaration = re.compile(".*class\s+\S+\s*")           # regex per dichiarazione di classi: public 'class' A{
                                                                # sostituita con la libreria javalang (Parse.py)
def isSingleComment(string):
    """
    Si usano espressioni regolari anche per controllare che la riga di codice non sia stata commentata
    Javalang non riesce a processare questo tipo di controllo
    :param reList: reIsComment
    :param string: line code
    :return: boolean: True: commented line code - False: otherwise
    """

    if reIsComment[0].search(string):
        return True
    return False

def removeComment(string):
    """
    Rimuovere i commenti dalla riga di codice da analizzare che presenta '//'
    :param string: riga di codice commentata
    :return: porzione di riga di codice non commentata
    """

    if reIsComment[0].search(string):
        indcom = string.index('//')
        return (string[:indcom])
    return string

def isStartMultipleComment(string):
    if reIsComment[1].search(string):
        return True
    return False

def isEndMultipleComment(string):
    if reIsComment[2].search(string):
        return True
    return False