# ANTLR for file format check and parsing
PROJECTLIB_PATH=$(shell pwd)
ANTLR_JAR=${PROJECTLIB_PATH}/antlr-4.7.1-complete.jar
export CLASSPATH=.:${ANTLR_JAR}
ANTLR4=java -Xmx500M -cp "${ANTLR_JAR}:${CLASSPATH}" org.antlr.v4.Tool
GRUN=java org.antlr.v4.runtime.misc.TestRig
WORKDIR=./antlr_jsonml

test:
	#rm -r ${WORKDIR}
	mkdir -p ${WORKDIR}
	cp JSONMLGrammar.g4 ${WORKDIR}/JSONMLGrammar.g4
	cd ${WORKDIR}; ${ANTLR4} -Dlanguage=Python3 JSONMLGrammar.g4
	cd ${WORKDIR}; ${GRUN} JSONMLGrammar jsonml -tokens