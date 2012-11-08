#!/bin/sh

USR_LOCAL="/usr/local/"
JAVA="java"

for J in $(ls -r $USR_LOCAL | grep jdk | grep "1.6")
do
   JAVA_SIX=$J
done
echo "Discovered java 6: $JAVA_SIX"

unlink $USR_LOCAL$JAVA

ln -s $USR_LOCAL$JAVA_SIX $USR_LOCAL$JAVA

java -version
jython --version

