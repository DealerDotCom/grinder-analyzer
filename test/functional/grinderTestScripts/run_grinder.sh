#!/bin/bash

GRINDER_HOME=$1

if [ "x$GRINDER_HOME" == "x" ]
then
   echo "usage: run.sh <grinder home>"
   exit 1
fi

if [ ! -d "$GRINDER_HOME" ]
then
   echo "FATAL: invalid grinder home: $GRINDER_HOME"
   exit 1
fi


GRINDER_PROPS="grinder.testScript.properties"
#GRINDER_PROPS="grinder.testScript.locale_DE.properties"

echo "Running with grinder at $GRINDER_HOME"
for JAR in $GRINDER_HOME/lib/*.jar
do
   CLASSPATH=$CLASSPATH:$JAR
done

java -cp $CLASSPATH net.grinder.Grinder $GRINDER_PROPS


