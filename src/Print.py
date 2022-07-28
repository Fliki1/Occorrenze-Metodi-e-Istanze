import pandas as pd

def printData(dataset, variables, methods):
    # Fare il set_index dei dataframe causa problemi con la successiva analisi e gioco dei dati...
    # evitare se bisogna utilizzare questi per un analisi o conteggio vedi: methods

    # Printing Dataset
    dataset.set_index(["Filename", "Line number"], inplace=True)
    dataset.sort_index(inplace=True)
    dataset.to_csv("./results/DataSet-commitTable.csv")
    dataset.to_excel("./results/DataSet-commitTable.xlsx")
    # print(dataset[:20])

    # Printing Variables
    variables.set_index(["Filename", "Varname"], inplace=True)
    variables.sort_index(inplace=True)
    variables.to_csv("./results/VariablesTable.csv")
    variables.to_excel("./results/VariablesTable.xlsx")
    # print(variables[:20])

    # Printing Methods
    methods.to_csv("./results/MethodsTable.csv")
    methods.to_excel("./results/MethodsTable.xlsx")
    # print(methods_print[:20])

    # Printing Methods
    method_count = methods.value_counts(["MethodName", "Class"])  # Return a Series containing counts of unique rows in the DataFrame.
    # method_count.columns = ["MethodName", "Class", "Count"]       # Rinomina le colonne
    method_count.rename("Count", inplace=True)

    # Creo una Serie che tiene [MethodName, Class, lista CallingClasses]
    classes = pd.Series(data=[[] for ind in range(len(method_count))], index=method_count.index)
    # Salvo in classes la lista di classi che invocano ciascun metodo
    for i in method_count.index:  # per ciascuna coppia (MethodName e Class di appartenenza)
        temp = methods.loc[methods["MethodName"] == i[0]]  # prendo tutte le entry in methods con lo stesso MethodName
        for j in temp.index:  # per ciascuna entry presente in methods con questo MethodName
            if temp.loc[j]["CallingClass"] not in classes[i]:
                classes[i].append(temp.loc[j]["CallingClass"])  # salvo tutte le classi che invocano questo metodo
    classes.rename("CallingClasses", inplace=True)

    # Concat method_count e classes
    method_count = pd.DataFrame(method_count)
    method_count = pd.concat([method_count, classes], axis=1)
    method_count.reset_index(inplace=True)
    # Save
    method_count.to_csv("./results/FinalMethodTable.csv", index=False)
    method_count.to_excel("./results/FinalMethodTable.xlsx", index=False)