# Copyright (C) 2007-2012, Travis Bear
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

'''
It is the job of the reporter to examine the final lines of the grinder
out file, and, based on this data, generate a list of ReportRow objects
that can be used by the velocity template.
'''
# python imports
import sys
import os
import os.path as path
import shutil

# java imports
from org.apache.log4j import *
from org.jtmb.grinderAnalyzer import MDC
from org.jtmb.grinderAnalyzer import ReportRow
from java.text import NumberFormat

import ga.constants

class AbstractReporter:

    _summaryData = None
    
    def __init__(self, summaryData):
        self._summaryData = summaryData

    def getTestsColumn(self):
        raise NotImplementedError

    def getErrorsColumn(self):
        raise NotImplementedError

    def getStdevColumn(self):
        raise NotImplementedError

    def getMeanTimeColumn(self):
        raise NotImplementedError

    def getTxNameColumn(self):
        raise NotImplementedError
    
    def getTPSColumn(self):
        raise NotImplementedError

    def getRow(self):
        raise NotImplementedError
    
    def readGrinderOutFile(self, summaryData):
        # reset the test directory
        # TODO this logic does not belong in a method named 'readGrinderOutFile' !
        if path.isdir(CONFIG.reportDir):
            logger.warn("Deleting previous report directory '" + CONFIG.reportDir + "'.")
            shutil.rmtree(CONFIG.reportDir)
        if path.isfile(CONFIG.reportDir):
            logger.warn("Pre-existing file '" + CONFIG.reportDir + "' collides with report dir name.  Deleting.")
            os.remove(CONFIG.reportDir)
        os.mkdir(CONFIG.reportDir)
        shutil.copytree(MDC.get('current.dir') + os.sep + "templates", CONFIG.reportDir + os.sep + "templates")
        analyzerPlugin = ga.constants.VORPAL.getPlugin("analyzer")
        # add the configured response time thresholds to the analyzer columns
        if CONFIG.useThresholds and len(CONFIG.rtimeThresholds) > 0:
            numberFormat = NumberFormat.getNumberInstance()
            list = CONFIG.rtimeThresholds            
            thresholds = list[:len(list) - 1]
            # the first group
            colName = "under %s sec" % numberFormat.format(thresholds[0])
            analyzerPlugin.addColumnName(colName)
            # the middle groups
            if len(thresholds) > 1:
                for i in range(len(thresholds) - 1):
                    colName = "%s to %s sec" % (numberFormat.format(thresholds[i]), numberFormat.format(thresholds[i + 1]))
                    analyzerPlugin.addColumnName(colName)
            # the last group
            name = "over %s sec" % numberFormat.format(thresholds[len(thresholds) - 1])
            analyzerPlugin.addColumnName(name)
        logger.warn("Starting log analysis.")
        for line in summaryData.getTestDataLines():
            if CONFIG.isShowTransactionData():
                if line.startswith("Test") or line.startswith("(Test"):
                    row = self.getRow(line)
                    logger.debug("Adding row name %s" % row.getTxName())
                    analyzerPlugin.addDataRow(row)
            if line.startswith("Totals"):
                analyzerPlugin.setTotalsRow(self.getRow(line, True))

    def writeReportToFile(self):
        file = open(CONFIG.reportDir + os.sep + "report.html", "w")
        # thanks to Rafal for the utf encoding fix
        file.write(ga.constants.VORPAL.mergeTemplateFile(CONFIG.reportDir + os.sep + "templates/agent.vm").encode(UTF_ENCODING))
        file.close()



class G32NonHTTPReporter(AbstractReporter):

    def __init__(self, summaryData):
        AbstractReporter.__init__(self, summaryData)
        logger.info("Using reporter for Non-HTTP data.")
        
    def getTestsColumn(self):
        return 2

    def getErrorsColumn(self):
        return 3

    def getStdevColumn(self):
        return 5

    def getMeanTimeColumn(self):
        return 4

    def getTxNameColumn(self):
        return 7
    
    def getTPSColumn(self):
        return 6
    
    def getRow (self, line, isTotals=False):
        row = ReportRow(CONFIG)
        columns = line.split()
        row.setErrors(columns[self.getErrorsColumn()])
        row.setMeanTestTime(columns[self.getMeanTimeColumn()])
        row.setTests(columns[self.getTestsColumn()])
        row.setTestTimeStandardDev(columns[self.getStdevColumn()])
        row.setTPS(columns[self.getTPSColumn()])
        row.calculatePassRate()
        if isTotals:
            row.setTxName("Totals")
        else:
            name = self._summaryData.getTxName(line)
            row.setTxName(name)
        return row



class LegacyNonHTTPReporter(AbstractReporter):

    def __init__(self, summaryData):
        AbstractReporter.__init__(self, summaryData)
        logger.info("Using legacy reporter for Non-HTTP data.")
        
    def getTestsColumn(self):
        return 2

    def getErrorsColumn(self):
        return 3

    def getStdevColumn(self):
        return 5

    def getMeanTimeColumn(self):
        return 4

    def getTxNameColumn(self):
        return 6
    
    def getRow (self, line, isTotals=False):
        row = ReportRow(CONFIG)
        columns = line.split()
        row.setErrors(columns[self.getErrorsColumn()])
        row.setMeanTestTime(columns[self.getMeanTimeColumn()])
        row.setTests(columns[self.getTestsColumn()])
        row.setTestTimeStandardDev(columns[self.getStdevColumn()])
        row.calculatePassRate()
        if isTotals:
            row.setTxName("Totals")
        else:
            name = self._summaryData.getTxName(line)
            row.setTxName(name)
        return row



class AbstractHTTPReporter(AbstractReporter):

    def __init__(self, summaryData):
        AbstractReporter.__init__(self, summaryData)
        ga.constants.VORPAL.getPlugin("analyzer").enableHTTPStatistics()
        
    def getRow (self, line, isTotals=False):
        row = ReportRow(CONFIG)
        columns = line.split()
        row.setBytesPerSec(columns[self.getBytesPerSecColumn()])
        row.setErrors(columns[self.getErrorsColumn()])
        row.setMeanResponseLength(columns[self.getResponseLengthColumn()])
        row.setMeanTestTime(columns[self.getMeanTimeColumn()])
        row.setMeanTimeConnection(columns[self.getEstablishConnectionColumn()])
        row.setMeanTimeFirstByte(columns[self.getFirstByteColumn()])
        row.setMeanTimeResolveHost(columns[self.getResolveHostColumn()])
        row.setResponseErrors(columns[self.getResponseErrorsColumn()])
        row.setTests(columns[self.getTestsColumn()])
        row.setTestTimeStandardDev(columns[self.getStdevColumn()])
        row.calculatePassRate()
        if isTotals:
            row.setTxName("Totals")
        else:
            name = self._summaryData.getTxName(line)
            row.setTxName(name)
        return row
       
    def getResponseLengthColumn(self):
        raise NotImplementedError

    def getBytesPerSecColumn(self):
        raise NotImplementedError

    def getResponseErrorsColumn(self):
        raise NotImplementedError

    def getResolveHostColumn(self):
        raise NotImplementedError

    def getEstablishConnectionColumn(self):
        raise NotImplementedError

    def getFirstByteColumn(self):
        raise NotImplementedError



class LegacyHTTPReporter(AbstractHTTPReporter):
    """
    Contains mappings for grinder 30-beta33, 3.0, and 3.1
    """
    
    def __init__(self, summaryData):
        AbstractHTTPReporter.__init__(self, summaryData)
        logger.info("Using legacy reporter for HTTP data.")
        
    def getTestsColumn(self):
        return 2

    def getErrorsColumn(self):
        return 3

    def getStdevColumn(self):
        return 5

    def getMeanTimeColumn(self):
        return 4

    def getResponseLengthColumn(self):
        return 6

    def getBytesPerSecColumn(self):
        return 7

    def getResponseErrorsColumn(self):
        return 8

    def getResolveHostColumn(self):
        return 9

    def getEstablishConnectionColumn(self):
        return 10

    def getFirstByteColumn(self):
        return 11

    def getTxNameColumn(self):
        return 12  



class G32HTTPReporter(AbstractHTTPReporter):
    """
    Contains mappings introduced in The Grinder 3.2
    """
    
    def getRow (self, line, isTotals=False):
        columns = line.split()
        row = AbstractHTTPReporter.getRow(self, line, isTotals)
        row.setTPS(columns[self.getTPSColumn()])
        return row
    
    def __init__(self, summaryData):
        AbstractHTTPReporter.__init__(self, summaryData)
        logger.info("Using reporter for HTTP data.")
        
    def getTestsColumn(self):
        return 2

    def getErrorsColumn(self):
        return 3

    def getStdevColumn(self):
        return 5

    def getMeanTimeColumn(self):
        return 4

    def getTPSColumn(self):
        return 6

    def getResponseLengthColumn(self):
        return 7

    def getBytesPerSecColumn(self):
        return 8

    def getResponseErrorsColumn(self):
        return 9

    def getResolveHostColumn(self):
        return 10

    def getEstablishConnectionColumn(self):
        return 11

    def getFirstByteColumn(self):
        return 12

    def getTxNameColumn(self):
        return 13


def _getGrinderVersion(firstLine):
    grinderVersion = firstLine.split(GRINDER_VERSION_TAG)[1].strip()
    logger.info("Discovered grinder version '%s'" %grinderVersion)
    words = grinderVersion.split(".")
    if len(words) < 2:
        logger.fatal("Invalid grinder version: '%s'" %grinderVersion)
        return None
    major = words[0]
    minor = words[1].split("-")[0]
    if len(words) == 2:
        return (grinderVersion, major, minor, None)
    return (grinderVersion, major, minor, words[2])



def getReporter(mappingFile, summaryData, firstLine=None):
    """
    Detects the version of the grinder that was used to write the log files.
    Returns a reporter containing mappings specific to that log file format.
    Bails out on unsupported or unrecognized log file formats.
    
    Params:
        * mappingFile:    string.  path to grinder mapping file.  Can be
                          null if firstLine is specified
        * summaryData:    ga.summary.SummaryDataRegistry
        * firstLine:      String.  The first line of the grinder mapping file.
    
    """
    if not firstLine:
        file=open(mappingFile)
        firstLine=file.readline()
        file.close()
    fullGrinderVersion, majorVersion, minorVersion, buildVersion = _getGrinderVersion(firstLine)
    if fullGrinderVersion == None:
        logger.fatal("Unsupported grinder version.  Aborting")
        return None
    majorVersion = int(majorVersion)
    minorVersion = int(minorVersion)
    if majorVersion != GRINDER_THREE:
        logger.fatal("Unsupported Grinder version: %s.  Aborting" %fullGrinderVersion)
        return None
    if minorVersion > MAX_SUPPORTED_MINOR_VERSION:
        logger.fatal("Unsupported Grinder version: %s.  Aborting" %fullGrinderVersion)
        return None
    # Check for non-http test data
    useHTTP = len(summaryData.getTestDataLines()[0].split()) >= 14
    if minorVersion < G32_MINOR_VERSION:
        if useHTTP:
            return LegacyHTTPReporter(summaryData)
        else:
            return LegacyNonHTTPReporter(summaryData)
    if useHTTP:
        return G32HTTPReporter(summaryData)
    else:
        return G32NonHTTPReporter(summaryData)


logger = Logger.getLogger("ga.report")
CONFIG = ga.constants.CONFIG
UTF_ENCODING="utf-8"
GRINDER_VERSION_TAG = "The Grinder version "
GRINDER_THREE = 3
G32_MINOR_VERSION = 2
MAX_SUPPORTED_MINOR_VERSION = 11