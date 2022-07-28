"""
    Script di partenza
"""
from pydriller import Repository
import pandas as pd
import re
import javalang

def parseLine(line):
    lineTokens = list(javalang.tokenizer.tokenize(line))
    values = []
    types = []
    for token in lineTokens:
        values.append(token.value)
        types.append(type(token).__name__)
    lineList = list(zip(values, types))
    return parseIdentifier(lineList)

def parseIdentifier(lineList):
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
                
def addVariables(table, tokens, filename):
    for i in range(len(tokens)):
        if tokens[i][1] == "Variable" and tokens[i-1][1] == "Class":
            # table = table.append({"Filename":filename, "Varname":tokens[i][0],\
            #                       "Vartype":tokens[i-1][0]}, ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i-1][0]]
            table.drop_duplicates(inplace = True)
        elif tokens[i][1] == "Variable" and tokens[i-1][0] == ">":
            j = tokens.index(("<","Operator"))
            # table = table.append({"Filename":filename, "Varname":tokens[i][0],\
            #                       "Vartype":tokens[j-1][0]}, ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[j-1][0]]
            table.drop_duplicates(inplace = True)
    return table
    
def addMethods(table, variables, tokens, filename, line_num, activeClass):
    for i in range(len(tokens)):
        if tokens[i][1] == "Method" and tokens[i-2][1] == "Variable":
            vartype = checkVariableClass(variables, filename, tokens[i-2][0])
            if vartype:
                # table = table.append({"Filename":filename, "MethodName":tokens[i][0],\
                #                       "Class":vartype, "Line number":line_num},\
                #                      ignore_index = True)
                table.loc[len(table.index)] = [filename, tokens[i][0], vartype,\
                                               activeClass, line_num]
        elif tokens[i][1] == "Method" and tokens[i-2][1] == "Class":
            # table = table.append({"Filename":filename, "MethodName":tokens[i][0],\
            #                       "Class":tokens[i-2][0], "Line number":line_num},\
            #                      ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i-2][0],\
                                           activeClass, line_num]
        elif tokens[i][1] == "Method" and tokens[i-4][1] == "Class":
            # table = table.append({"Filename":filename, "MethodName":tokens[i][0],\
            #                       "Class":tokens[i-4][0], "Line number":line_num},\
            #                      ignore_index = True)
            table.loc[len(table.index)] = [filename, tokens[i][0], tokens[i-4][0],\
                                           activeClass, line_num]
    return table
    
def checkVariableClass(table, filename, varname):
    auxset = table[table["Filename"] == filename]
    auxset = auxset[auxset["Varname"] == varname]
    if auxset.shape[0] > 1:
        print("Multiple variables with the same name detected in the same file.")
        return
    elif auxset.shape[0] == 0:
        print("Variable declaration not previously found")
        return
    else:
        return auxset.iat[0, 2]

def isComment(reList, string):
    matches = []
    for regEx in reList:
        matches.append(regEx.search(string))
    if matches.count(None) != len(matches):
        return True
    return False

def lookForClasses(file):
    if file == None:
        return
    classes = []
    lines = file.split("\n")
    for i in range(len(lines)):
        tokens = lines[i].split(" ")
        if "class" in tokens:
            classes.append((i, tokens[tokens.index("class") + 1]))
    return classes
    
def getActiveClass(classes, line_num):
    activeClass = None
    for aux in classes:
        if line_num >= aux[0]:
            activeClass = aux[1]
    return activeClass

dataset = pd.DataFrame(columns=["Filename","Change type", "Line number", "Code", "Tokens", "NumEdit"],\
                       index = [])
variables = pd.DataFrame(columns=["Filename","Varname","Vartype"], index = [])
methods = pd.DataFrame(columns=["Filename","MethodName","Class", "CallingClass", "Line number"], index=[])

reMethodCall = re.compile('\s*\S+\s*\.\s*\S+\s*\(.*\).*;\s*')
reInstAss = re.compile('\s*\S+\s*=\s*new\s*\S+\s*;\s*')

reIsComment = []
reIsComment.append(re.compile('\s*//.*'))
reIsComment.append(re.compile('\s*/\*.*'))

# reClassDeclaration = re.compile(".*class\s+\S+\s*")

# for commit in Repository('https://github.com/mauricioaniche/repodriller').traverse_commits():
for commit in Repository('https://github.com/tdebatty/java-LSH').traverse_commits():
    for file in commit.modified_files:
        if (file.change_type.name == "ADD" or file.change_type.name == "MODIFY"\
        or file.change_type.name == "DELETE") and file.filename[-5:] == ".java":
            name = file.filename
            diff = file.diff_parsed
            change = file.change_type.name
            added = diff["added"]
            deleted = diff["deleted"]
            lines = deleted + added
            cutOffPoint = len(added)
            classesInAdded = lookForClasses(file.source_code)
            classesInDeleted = lookForClasses(file.source_code_before)
            for i, element in zip(range(len(lines)), lines):
                matchMethodCall = reMethodCall.search(element[1])
                matchInstAss = reInstAss.search(element[1])
                if isComment(reIsComment, element[1]):
                    continue
                if matchMethodCall or matchInstAss:
                    tokens = parseLine(element[1])
                    if dataset.loc[(dataset["Filename"] == name) & (dataset["Line number"] == element[0])].empty:
                        dataset.loc[len(dataset.index)] = [name, [change], element[0], [element[1]], [tokens], 0]
                    else:
                        ind = dataset.loc[(dataset["Filename"] == name) & (dataset["Line number"] == element[0])].index
                        if len(ind) != 1:
                            print("counted the wrong number of indices")
                        ind = ind[0]
                        dataset.at[ind, "Change type"].append(change)
                        dataset.at[ind, "Code"].append(element[1])
                        dataset.at[ind, "Tokens"].append(tokens)
                        dataset.at[ind, "NumEdit"] = dataset.at[ind, "NumEdit"] + 1
                if matchInstAss:
                    variables = addVariables(variables, tokens, name)
                if matchMethodCall:
                    if i < cutOffPoint:
                        activeClass = getActiveClass(classesInAdded, element[0])
                    else:
                        activeClass = getActiveClass(classesInDeleted, element[0])
                    methods = addMethods(methods, variables, tokens, name, element[0], activeClass)
         
dataset.set_index(["Filename", "Line number"], inplace = True)
dataset.sort_index(inplace = True)
# dataset.to_csv("commitTable.csv")
# dataset.to_excel("commitTable.xlsx")

method_count = methods.value_counts(["MethodName", "Class",])
method_count.rename("Count", inplace = True)
classes = pd.Series(data = [ [] for ind in range(len(method_count))], index = method_count.index)
for i in method_count.index:
    temp = methods.loc[methods["MethodName"] == i[0]]
    for j in temp.index:
        if temp.loc[j]["CallingClass"] not in classes[i]:
            classes[i].append(temp.loc[j]["CallingClass"])
classes.rename("CallingClasses", inplace = True)
method_count = pd.DataFrame(method_count)
method_count = pd.concat([method_count, classes], axis = 1)
method_count.reset_index(inplace=True)
method_count.to_csv("methodTable.csv", index = False)
method_count.to_excel("methodTable.xlsx", index = False)
