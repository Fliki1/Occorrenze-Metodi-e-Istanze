import javalang

def parseLine(line):
    """
    Effettua il parsing di una linea di codice Java suddividendo il codice in token e assegnando
    un tipo sintattico a ognuno di essi
    :param line: line code
    :return: parseIdentifier
    """
    lineTokens = list(javalang.tokenizer.tokenize(line))
    values = []
    types = []
    for token in lineTokens:
        values.append(token.value)
        types.append(type(token).__name__)
    lineList = list(zip(values, types))
    return parseIdentifier(lineList)

def parseIdentifier(lineList):
    """
    Specifica tipologia di token trovati.
    Gli Identifier trovati possono essere: Method - Function - Class - Variable
    :param lineList: line code Identifier-ata
    :return: lineList con Identifier specifico (Method - Function - Class - Variable)
    """
    auxList = lineList.copy()
    for i in range(len(auxList)):
        if auxList[i][1] == 'Identifier':
            if auxList[i+1][0] == '(' and auxList[i-1][0] == '.':
                lineList[i] = (lineList[i][0], 'Method')
            elif auxList[i+1][0] == '(':
                lineList[i] = (lineList[i][0], 'Function')
            elif auxList[i][0][0].isupper():
                lineList[i] = (lineList[i][0], 'Class')
            else:
                lineList[i] = (lineList[i][0], 'Variable')
    return lineList
