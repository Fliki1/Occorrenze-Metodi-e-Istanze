import logging

logger = logging.getLogger(__name__)  # nome del modulo corrente (ManageDataset.py)

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
    file_handler = logging.FileHandler('./log/ManageDataset.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def addVariables(table, tokens, filename, verbose):
    """
    Update Dataset variables contenente le instanze trovate nel progetto
    :param table: variables dataset
    :param tokens: code tokens line
    :param filename: java file
    :return: table updated
    """

    # Setting log
    log(verbose)

    for i in range(len(tokens)):
        if tokens[i][1] == "Variable" and tokens[i - 1][1] == "Class":
            # case Class x = new Class()
            # table = table.append({"Filename":filename, "Varname":tokens[i][0],\
            #                       "Vartype":tokens[i-1][0]}, ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i - 1][0]]
            logger.info(f'addVariabile:, {[filename, tokens[i][0], tokens[i - 1][0]]}')  # Variabile found
            #print([filename, tokens[i][0], tokens[i - 1][0]])
            table.drop_duplicates(inplace=True)     # evitiamo di tenere in memoria copie della stessa instanza
        elif tokens[i][1] == "Variable" and tokens[i - 1][0] == ">":
            # type safety java case eg: List<MyObj> pippo = new List<MyObj>();
            j = tokens.index(("<", "Operator"))
            # table = table.append({"Filename":filename, "Varname":tokens[i][0],\
            #                       "Vartype":tokens[j-1][0]}, ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[j - 1][0]]
            logger.info(f'addVariabile:, {[filename, tokens[i][0], tokens[j - 1][0]]}')
            #print([filename, tokens[i][0], tokens[j - 1][0]])
            table.drop_duplicates(inplace=True)     # evitiamo di tenere in memoria copie della stessa instanza
        elif tokens[i][1] == "Variable" and tokens[i-1][1] == "Separator" and tokens[i-2][0] == "this" \
                and (tokens[i + 3][1] == "Class" or tokens[i + 3][1] == "Function"):
            # case: this.mb = new Class()
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i + 3][0]]
            logger.info(f'addVariabile:, {[filename, tokens[i][0], tokens[i + 3][0]]}')
            #print([filename, tokens[i][0], tokens[i + 3][0]])
            table.drop_duplicates(inplace=True)     # evitiamo di tenere in memoria copie della stessa instanza
        elif tokens[i][1] == "Variable" and tokens[i-1][1] == "Separator" and tokens[i-2][0] == "this" \
                and (tokens[i + 6][1] == "Class" or tokens[i + 6][1] == "Function"):
            # case this.mb[i] = new Class()
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i + 6][0]]
            logger.info(f'addVariabile:, {[filename, tokens[i][0], tokens[i + 6][0]]}')
            #print([filename, tokens[i][0], tokens[i + 6][0]])
            table.drop_duplicates(inplace=True)  # evitiamo di tenere in memoria copie della stessa instanza
        elif tokens[i][1] == "Variable" and i == 0 and tokens[i+2][0] == "new":
            # case: filereader = new FileReader()
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i + 3][0]]
            logger.info(f'addVariabile:, {[filename, tokens[i][0], tokens[i + 3][0]]}')
            #print([filename, tokens[i][0], tokens[i + 3][0]])
            table.drop_duplicates(inplace=True)  # evitiamo di tenere in memoria copie della stessa instanza
    return table


def addMethods(table, variables, tokens, filename, line_num, activeClass, verbose):
    """
    Update Dataset methods contenente i metodi invocati nel progetto
    :param table: methods dataset
    :param variables: variabile invocazione metodo
    :param tokens: riga in tokens
    :param filename: file java
    :param line_num: riga file java
    :param activeClass: lista classi attive
    :return: table update
    """

    # Setting log
    log(verbose)

    for i in range(len(tokens)):
        # Case: variable.method()
        if tokens[i][1] == "Method" and tokens[i - 2][1] == "Variable":
            vartype = checkVariableClass(variables, filename, tokens[i - 2][0])
            if vartype:
                # table = table.append({"Filename":filename, "MethodName":tokens[i][0],\
                #                       "Class":vartype, "Line number":line_num},\
                #                      ignore_index = True)
                table.loc[len(table.index)] = [filename, tokens[i][0], vartype, activeClass, line_num]
                logger.info(f'addMethod:, {[filename, tokens[i][0], vartype, activeClass, line_num]}')
        # Case: class.method()
        elif tokens[i][1] == "Method" and tokens[i - 2][1] == "Class":
            # table = table.append({"Filename":filename, "MethodName":tokens[i][0],\
            #                       "Class":tokens[i-2][0], "Line number":line_num},\
            #                      ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i - 2][0], activeClass, line_num]
            logger.info(f'addMethod:, {[filename, tokens[i][0], tokens[i - 2][0], activeClass, line_num]}')
        # Case: chiamate annidate di metodo es. Logger.getLogger(LSH.class.getName()).log(Level.SEVERE, null, ex);
        elif tokens[i][1] == "Method" and tokens[i - 4][1] == "Class":
            # table = table.append({"Filename":filename, "MethodName":tokens[i][0],\
            #                       "Class":tokens[i-4][0], "Line number":line_num},\
            #                      ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i - 4][0], activeClass, line_num]
            logger.info(f'addMethod:, {[filename, tokens[i][0], tokens[i - 4][0], activeClass, line_num]}')
    return table


def checkVariableClass(table, filename, varname):
    """
    Metodo per verificare la classe
    :param table: dataset di riferimento
    :param filename: java file
    :param varname: variabile
    :return: riferimento
    """
    auxset = table[table["Filename"] == filename]
    auxset = auxset[auxset["Varname"] == varname]
    if auxset.shape[0] > 1:
        # es. v1.setEntry(rand.nextInt(n), rand.nextDouble());
        logger.info(f'Multiple variables with the same name detected in the same file/line.')
        #print("Multiple variables with the same name detected in the same file/line.")
        return
    elif auxset.shape[0] == 0:
        logger.info(f'Variable declaration not previously found: {varname}')
        #print("Variable declaration not previously found:", varname)
        # TODO: gestire l'ordine di generazione dei dati?
        return
    else:
        return auxset.iat[0, 2]