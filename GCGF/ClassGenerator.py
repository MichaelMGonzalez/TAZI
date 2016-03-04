__author__ = "Michael Gonzalez"
__email__ = "mmg005@eng.ucsd.edu"

import xml.etree.ElementTree as ETree
import functools
def createComment( comment, dash="-"):
    dashes = (40-len(comment)/2)*dash
    if len(comment) % 2 == 0: comment+=dash
    return "/** " + dashes + "" + comment + "" + dashes + " **/" 
class Arg:
    def __init__(self, value, name):
        self.value = value
	self.name = name
class CObj:
    countMap = {}
    def __init__(self, objType):
        self.objType = objType
        if objType not in CObj.countMap: CObj.countMap[objType] = 1
        else: CObj.countMap[objType] += 1
	self.name = str.lower(objType) + str(CObj.countMap[objType])
    def setArgs(self, args):
        self.args = args
class ClassGenerator:
    objects = []
    libraries = []
    objInstances = []
    loopBody = []
    name = "" 

    def __init__( self, api):
        self.parseApiGspec(api)
    def getSetupFunction(self):
        def concatLines(acc, line): return acc + "   " + line + ".setup();\n"
	return functools.reduce( concatLines, self.objInstances, "void setup() {\n" ) + "}"
    def getLoopFunction(self):
        def concatLines(acc, line): return acc + "   " + line + "\n"
	return functools.reduce( concatLines, self.loopBody, "void loop() {\n" ) + "}"
    def getLibraries(self):
        def concatLib( acc, elem): return acc + '#include <' + elem + '>\n'
	return functools.reduce( concatLib, set(self.libraries), "" )
    def getConstants(self):
        retStrings = []
	for obj in self.objects:
	    for arg in obj.args:
	        currStr = "#define " + str.upper(obj.name) + "_" + arg.name + " " + str(arg.value)
	        retStrings.append(currStr)
	return retStrings
    def getObjectDeclarations(self):
        retStrings = []
	for obj in self.objects:
	    argC = 0
	    instanceName = str.lower(obj.name)
	    self.objInstances.append(instanceName)
	    currStr = obj.objType + " " + instanceName + "("
	    for arg in obj.args :
		if argC is not 0:
		    currStr = currStr + ", "
	        currStr = currStr + str.upper(obj.name) + "_" + str( arg.name )
		argC = argC + 1
	    currStr = currStr + ");"
	    retStrings.append(currStr)
        return retStrings
    def parseApiGspec(self, root):
        for component in root:
	    if component.tag == "name": self.name = component.text
	    if component.tag != "component":
	        continue
	    for node in component:
	        if node.tag != "api":
		    continue
                currentObj = CObj( node.attrib["class"] )
		if "polls" in node.attrib.keys():
		    self.loopBody.append( currentObj.name + ".poll();" )
	        args = []
		# Handle all the arguments for the object
	        for arg in node.findall("arg"):
	            currentArg = Arg( arg.attrib["digitalliteral"], arg.attrib["arg"] )
		    if currentArg.value == "None": 
		        currentArg.value = arg.attrib["analogliteral"] 
		    args.append( currentArg )
		# Handle all the extra required libraries
		for lib in node.find("required_files").findall("file"):
		    self.libraries.append( lib.attrib["name"] )
	        currentObj.setArgs( args )
	        self.objects.append( currentObj )
	        self.libraries.append( node.attrib["include"])
    def getClass(self):
	nl = "\n"
        def a( string ): return nl+string
	#def createComment( string ): return self.createComment(string)
        rv = createComment(" Robot Name ", dash="#") 
        rv += a(createComment("*"*len(self.name), dash="~"))
        rv += a(createComment("*"*len(self.name), dash="~"))
        rv += a(createComment(self.name, dash="="))
        rv += a(createComment("*"*len(self.name), dash="~"))
        rv += a(createComment("*"*len(self.name), dash="~"))
        rv += a(createComment("{"*(len(self.name)/2) +"^_^"+ "}"*(len(self.name)/2), dash="#")) 
        rv += nl
        rv += nl
        rv += nl
        rv += nl
        rv += a(createComment("", dash="="))
        rv += a(createComment("Libraries"))
        rv += a(createComment("", dash="="))
        rv += nl
        rv += a(self.getLibraries())
        rv += a(createComment("", dash="="))
        rv += a(createComment("Pin Constants"))
        rv += a(createComment("", dash="="))
        rv += nl
        for string in self.getConstants():
            rv += a(string)
        rv += nl
        rv += a(createComment("", dash="="))
        rv += a(createComment("Object Declarations"))
        rv += a(createComment("", dash="="))
        rv += nl
        for string in self.getObjectDeclarations():
            rv += a(string)
        rv += nl
        rv += a(createComment("", dash="="))
        rv += a(createComment("Setup Function"))
        rv += a(createComment("", dash="="))
        rv += nl
        rv += a(self.getSetupFunction())
        rv += nl
        rv += a(createComment("", dash="="))
        rv += a(createComment("Loop Function"))
        rv += a(createComment("", dash="="))
        rv += nl
        rv += a(self.getLoopFunction())
	return rv

if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser("stuff")
    argparser.add_argument("-g", "--gspec", required=True)
    args = argparser.parse_args()
    api = ETree.parse(args.gspec).getroot()
    generator = ClassGenerator(api)
    print generator.getClass()

    
