# Copyright (C) 2012, Travis Bear
# All rights reserved.
#
# In addition to the individuals named above, several anonymous users
# have contributed as well.
#
# This file is part of Grinder Analyzer.
#
# Grinder Analyzer is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Grinder Analyzer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Grinder Analyzer; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from ga.fileutils import reverseSeek
from org.apache.log4j import Logger
import ga.constants
import sys

class SummaryDataRegistry:
    """
    Container for the summary data at the end of the grinder out_ file.
    
    """
    lineNameMap = None
    txNumNameMap = None
    
    def __init__(self, outFile):
        """
        Loads everything from the mapping file.  Filters out duplicate names.
        
        """
        self.txNumNameMap = {}
        self.lineNameMap = {} # key: data line, val: tx name
        finalOutLines = reverseSeek (outFile, TABLE_MARKER)
        for line in finalOutLines:
            if line.find( "Test" ) == 0 or line.find("Test") == 1 or line.startswith("Totals"):
                if line.startswith("Totals"):
                    # Format the totals line to be identical to test lines
                    line=line.replace("Totals", "Totals 0") # add a column
                    line='%s "%s"' %(line, ALL_TRANSACTIONS_VALUE)
                testName = self._getInitialTxName(line)
                if CONFIG.isShowTransactionData() or testName == "All Transactions":
                    self.lineNameMap [line] = testName
        if len(self.lineNameMap) == 0:
            msg = """
                FATAL:  Incomplete or corrupted grinder mapping file.  No summary data containing
                test number/name mappings found."""
            logger.fatal(msg)
            sys.exit(1)
            
        duplicateTxNames = self._getListDuplicates(self.lineNameMap.values())
        if len(duplicateTxNames) > 0:
            logger.info("Duplicate transaction names found: %s" %duplicateTxNames)
        for line in self.lineNameMap.keys():
            txName = self._getInitialTxName(line)
            txNum = self._getTxNum(line)
            if duplicateTxNames.__contains__(txName):
                txName ="%s_%s" %(txName, txNum)
            self.txNumNameMap[txNum] = txName
            self.lineNameMap[line] = txName
        logger.debug("Final tx names: %s" %self.txNumNameMap.values())


    def _getTxNum(self, line):
        return line.split( " " )[1] # test number is 2nd column
    
    def _getInitialTxName(self, line):
        return line.split( '"' )[1]   # test names appear in quotes
    
    def _getListDuplicates(self, list):
        """
        Returns a subset of list containing items that appear more than once
        """
        itemCountMap = {}
        for item in list:
            if itemCountMap.has_key(item):
                itemCountMap[item] += 1
            else:
                itemCountMap[item] = 1
        # list comprehension, w00t
        return [ key for key in itemCountMap.keys() if itemCountMap[key] > 1]
 
    def getTxNumNameMap(self):
        return self.txNumNameMap
    
    def getTestDataLines(self):
        return self.lineNameMap.keys()
    
    def getTxName(self, line):
        return self.lineNameMap[line]



ALL_TRANSACTIONS_VALUE="All Transactions"
CONFIG = ga.constants.CONFIG
logger = Logger.getLogger("ga.summary")
TABLE_MARKER="Final statistics for this process"
