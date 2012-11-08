#!/bin/sh

USR_LOCAL="/usr/local/"
JAVA="java"

for J in $(ls -r $USR_LOCAL | grep jdk | grep "1.7")
do
   JAVA_SEVEN=$J
done
echo "Discovered java 7: $JAVA_SEVEN"

unlink $USR_LOCAL$JAVA

ln -s $USR_LOCAL$JAVA_SEVEN $USR_LOCAL$JAVA

java -version
jython --version

