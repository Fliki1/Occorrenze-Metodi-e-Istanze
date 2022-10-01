import javalang

def parseLine(line):
    """
    Effettua il parsing di una linea di codice Java suddividendo il codice in token e estrapolando
    la coppia tipo sintattico e valore corrispondente:
    (Identifier - Operator - String - Separator...) e valore (roll, +, "ciao", ;...)
    :param line: line code
    :return: parseIdentifier(identificatore, valore)
    """
    lineTokens = list(javalang.tokenizer.tokenize(line))
    # print(lineTokens)   # [Identifier "System" line 1, position 9, Separator "." line 1,
    values = []
    types = []
    for token in lineTokens:
        values.append(token.value)
        types.append(type(token).__name__)
    lineList = list(zip(values, types))     # (identificatore, valore)
    return parseIdentifier(lineList)

def parseIdentifier(lineList):
    """
    Specifica tipologia di token trovati.
    Gli Identifier trovati possono essere: Method - Function - Class - Variable
    :param lineList: coppia(identificatore, valore)
    :return: lineList ziplist con Identifier associato a: Method - Function - Class - Variable e valore
    """
    auxList = lineList.copy()
    for i in range(len(auxList)):
        if auxList[i][1] == 'Identifier' and i+1 < len(auxList):
            # Euristiche per determinare il ruolo del tipo sintattico analizzato
            if auxList[i+1][0] == '(' and auxList[i-1][0] == '.':
                lineList[i] = (lineList[i][0], 'Method')
            elif auxList[i+1][0] == '(':
                lineList[i] = (lineList[i][0], 'Function')
            elif auxList[i][0][0].isupper():
                lineList[i] = (lineList[i][0], 'Class')
            else:
                lineList[i] = (lineList[i][0], 'Variable')
    return lineList

def parseNormLine(line):
    """
    Effettua il parsing di una linea di codice Java suddividendo il codice in token e estrapolando
    la coppia tipo sintattico e valore corrispondente:
    (Identifier - Operator - String - Separator...) e valore (roll, +, "ciao", ;...)
    :param line: line code
    :return: parseIdentifier(identificatore, valore)
    """
    lineTokens = list(javalang.tokenizer.tokenize(line))
    #print(lineTokens)   # [Identifier "System" line 1, position 9, Separator "." line 1,
    values = []
    types = []
    for token in lineTokens:
        values.append(token.value)
        types.append(type(token).__name__)
    lineList = list(zip(values, types))     # (identificatore, valore)
    return lineList