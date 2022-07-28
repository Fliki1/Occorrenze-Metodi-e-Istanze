
def lookForClasses(file):
    """
    Dato l'intero codice di un file si cerca la presenza di tutte le classi e corrispondente riga
    :param file: intero codice di un file
    :return: lista contenenti (riga, classe) presenti nel singolo file
    """
    if file == None:
        return
    classes = []
    lines = file.split("\n")        # split per \n l'intero codice
    # print(lines)                  # ['', '// import java.util.*;  ', 'import java.util.Scanner; // Import the Scanner class', '', 'class Main {',
    for i in range(len(lines)):
        tokens = lines[i].split(" ")                # split per " " codice già splittato da \n
        # print("tokens", tokens)                   # [''] - ['//', 'import', 'java.util.*;', '', ''] - [
        if "class" in tokens:
            if tokens.index("class") + 1 < len(tokens):     # se esiste un riferimento dopo 'class'
                classes.append((i, tokens[tokens.index("class") + 1]))
    # print(classes) [(1, 'ConstructorOverloading'), (20, 'House')] [(4, 'Main')] [(4, 'Main')] []
    return classes


def getActiveClass(classes, line_num):
    """
    Riconoscere la classe analizzata based on lookForClasses precedentemente eseguito (riga, classe)
    :param classes: lista di classi a conoscenza [(1, 'test'), (22, 'ParentTest'), (33, 'test')]
    :param line_num: riga analizzata
    :return: Classe associata a quella riga secondo lookForClasses eseguito in precedenza, None se non presente
    """
    activeClass = None
    for aux in classes:
        if line_num >= aux[0]:
            activeClass = aux[1]
    return activeClass