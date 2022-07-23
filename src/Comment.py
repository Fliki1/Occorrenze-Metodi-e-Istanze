import re

# Espressioni regolari per selezionare le righe di codice contenenti instanziazioni di oggetti o chiamate di metodi

reMethodCall = re.compile('\s*\S+\s*\.\s*\S+\s*\(.*\).*;\s*')   # chiamate a metodo
reInstAss = re.compile('\s*\S+\s*=\s*new\s*\S+\(.*\)\s*;\s*')   # new instanza

# Espressioni regolari per i commenti

reIsComment = []
reIsComment.append(re.compile('\s*//.*'))                       # // commento singola riga
reIsComment.append(re.compile('\s*/\*.*'))                      # /* commento di plurime righe

# reClassDeclaration = re.compile(".*class\s+\S+\s*")           # regex per dichiarazione di classi: public 'class' A{
                                                                # sostituita con la libreria javalang (Parse.py)
def isComment(string):
    """
    Si usano espressioni regolari anche per controllare che la riga di codice non sia stata commentata
    Javalang non riesce a processare questo tipo di controllo
    :param reList: reIsComment
    :param string: line code
    :return: boolean: True: commented line code - False: otherwise
    """
    if reIsComment[1].search(string):
        print("Trovato /*")
        return True

    elif reIsComment[0].search(string):
        print("Trovato //")
        return True


    """matches = []
    for regEx in reIsComment:
        matches.append(regEx.search(string))
    if matches.count(None) != len(matches):
        print(matches.count(None), len(matches))
        print("commento")
        return True"""
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
