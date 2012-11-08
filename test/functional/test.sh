#!/bin/bash

# Copyright (C) 2008-2012, Travis Bear
# All rights reserved.
#
# With contributions from:
#    Scott Russell
#
# This file is part of The Scale Harness software distribution. Refer to
# the file LICENSE which is part of The Scale Harness distribution for
# licensing details.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

# 
#   DESCRIPTION:  Harness to run some common test scenarios
#        AUTHOR:  Travis Bear 
#       CREATED:  9/22/2008




######################################################################
# Clean build GA from source
######################################################################
function makeCleanBuild() {
   cd $ANALYZER_SOURCE_ROOT
   ant >> test/functional/ant.out
   cd -
}



######################################################################
# Exctact a new grinder analyzer
######################################################################
function extractCleanBuild {
   echo
   pwd
   echo
   rm -rf ./GrinderAnalyzer*
   cp $ANALYZER_SOURCE_ROOT/pkg/GrinderAnalyzer* .
   tar -zxpf $(ls | grep GrinderAnalyzer)
   rm *.gz
}



######################################################################
# Execute test suites
######################################################################
function executeTests() {
   for TESTDIR in $TESTDIRS
   do
      echo
      echo " - - - - Starting new test for $TESTDIR - - - " 
      STATUS="PASS"
      GRINDEROUTFILE=$($DATADIR/get_mapping_file.sh $DATADIR/$TESTDIR)
      TESTOUTPUT=$RESULTSDIR/$TESTDIR/output
      if [ "$GRINDEROUTFILE" == "" ]
      then 
         echo "    out file not found.  Skipping $TESTDIR"
         echo "    $TESTDIR    INVALID" >> $SUMMARYFILE
         continue
      fi
      DATAFILES=$($DATADIR/get_data_files.sh $DATADIR/$TESTDIR)

      MUSTHAVES=$DATADIR/$TESTDIR/mustHave
      MUSTNOTHAVES=$DATADIR/$TESTDIR/mustNotHave
      if ! ls $MUSTHAVES > /dev/null 2>&1  && ! ls $MUSTNOTHAVES > /dev/null 2>&1
      then
         echo "No valid test criteria for $TESTDIR, skipping."
         echo "    $TESTDIR    INVALID" >> $SUMMARYFILE
         continue
      fi

      # preliminary check passed, let's do some work
      mkdir $RESULTSDIR/$TESTDIR
      #echo "testing $TESTDIR.  Grinder Outfile: $GRINDEROUTFILE   Data files: $DATAFILES  stdout:  $TESTOUTPUT"
      #echo "jython ./run.py \"$DATAFILES\" $GRINDEROUTFILE > $TESTOUTPUT 2>&1"
      jython ./analyzer.py "$DATAFILES" $GRINDEROUTFILE > $TESTOUTPUT 2>&1
      mv grinderReport $RESULTSDIR/$TESTDIR/grinderReport

      # write test conditions to new test file
      awk '{print "if ! grep \"" $0  "\" " FILE "> /dev/null; then STATUS=FAIL; echo \"     Did not find required text: " $0 "\";fi"}' FILE=$TESTOUTPUT $MUSTHAVES > .test.$TESTDIR
      awk '{print "if grep \"" $0  "\" " FILE " > /dev/null; then STATUS=FAIL; echo \"     Found forbidden text: " $0 "\";fi"}' FILE=$TESTOUTPUT $MUSTNOTHAVES >> .test.$TESTDIR

      # execute test file to evalute results of grinder run
      . .test.$TESTDIR
      echo "echo \"    $TESTDIR    $STATUS\" >> $SUMMARYFILE"
      echo "    $TESTDIR    $STATUS" >> $SUMMARYFILE
      echo "Status: $STATUS"
   done
}



######################################################################
# Main flow begins here
######################################################################

# check for jython
if ! which jython > /dev/null 2>&1
then
   echo "FATAL: jython not installed or not in default path.  Please"
   echo "       install jython before continuing."
   exit 1
fi

if ! pwd | grep "test/functional$" > /dev/null
then
   echo "FATAL:  test.sh can only be run from the test directory"
   exit 1
fi

DATADIR=$1
if [ -z "$DATADIR" ]
then
   echo "usage:  test.sh <data dir>"
   exit 1
fi

if [ ! -d "$DATADIR" ]
then
   echo "FATAL: not a directory: $DATADIR"
   exit 1
fi
if [ ! -f "$DATADIR/get_data_files.sh" ]
then
   echo "FATAL: $DATADIR is not a valid test log dir.  No 'get_data_files' script present."
   exit 1
fi
if [ ! -f "$DATADIR/get_mapping_file.sh" ]
then
   echo "FATAL: $DATADIR is not a valid test log dir.  No 'get_mapping_file' script present."
   exit 1
fi


ANALYZER_SOURCE_ROOT="../.."

#./j6.sh
makeCleanBuild
extractCleanBuild

ANALYZERDIR=$(ls | grep GrinderAnalyzer)
echo $ANALYZERDIR
cd $ANALYZERDIR

DATADIR="../$DATADIR"
TESTDIRS=$(ls $DATADIR | grep -v .sh$)
SUMMARYFILE="resultsSummary.txt"

RESULTSDIR="results_j5"
rm -rf $RESULTSDIR
mkdir $RESULTSDIR
../j5.sh
echo "Java 5 test run at `date`" > $SUMMARYFILE
executeTests

RESULTSDIR="results_j6"
rm -rf $RESULTSDIR
mkdir $RESULTSDIR
../j6.sh
echo "Java 6 test run at `date`" >> $SUMMARYFILE
executeTests

echo
echo
echo "Results:"
echo
cat $SUMMARYFILE

