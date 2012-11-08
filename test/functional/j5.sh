#!/bin/sh

USR_LOCAL="/usr/local/"
JAVA="java"

for J in $(ls -r $USR_LOCAL | grep jdk | grep "1.5")
do
   JAVA_FIVE=$J
done
echo "Discovered java 5: $JAVA_FIVE"

unlink $USR_LOCAL$JAVA

ln -s $USR_LOCAL$JAVA_FIVE $USR_LOCAL$JAVA

java -version
jython --version

