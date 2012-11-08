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

from org.apache.log4j import Logger
import analyzer
import ga.constants

#####################################################################
# Container for per-datapoint graph data
#####################################################################

class AbstractBucket:
    """
    Contains all the info for each data point in the graph/.csv file
    """
    startTime = None
    endTime = None
    transactionDataMap = None # per-bucket map of tx numbers to bucket data
    bucketDurationMs = None
    logAnalyzer = None
    rtGroup = None
    
    def __init__ (self, start, end, lAnalyzer):
        self.startTime = start
        self.endTime = end
        self.transactionDataMap = {}
        self.logAnalyzer = lAnalyzer
        for testNumber in self.logAnalyzer.getTransactionMap().keys():
            #logger.info("DEBUG: defining %s" %testNumber)
            self.transactionDataMap[testNumber] = TransactionBucketData()
        self.bucketDurationMs = self.endTime - self.startTime
        logger.debug ("DEBUG: bucket duration = " + str(self.bucketDurationMs) + ", Start: " + str(start) + ", end:" + str(end))

    def __addTestData__(self, testNumber, columns):
        raise NotImplementedError
 
    def addLine (self, columns):
        """
        Takes a line from the data file and increments the transaction counters
        """
        key = columns[analyzer.TEST_NUMBER_COLUMN].strip()
        self.__addTestData__(analyzer.ALL_TRANSACTIONS_KEY, columns)
        if ga.constants.CONFIG.isShowTransactionData():
            self.__addTestData__(key, columns)

    def getStartTime(self):
        return self.startTime
    
    def getEndTime(self):
        return self.endTime

    def getTxSecPass(self, txNumber):
        ''' For a given transaction name, reports the transactions
        per second that passed in this bucket '''
        return self.transactionDataMap[txNumber].totalPass * self.logAnalyzer.getAgentMultiplier() / (self.bucketDurationMs / 1000.0)
    
    def getTxSecFail(self, txNumber):
        ''' For a given transaction name, reports the transactions
        per second that failed in this bucket '''
        return self.transactionDataMap[txNumber].totalFail * self.logAnalyzer.getAgentMultiplier() / (self.bucketDurationMs / 1000.0)

    def getMeanResponseTime(self, txNumber):
        ''' For a given transaction name, reports the average total response
        time for transactions that passed.  Returned units are seconds, not ms'''
        meanResponseTime = 0.0
        passed = self.transactionDataMap[txNumber].totalPass
        if self.transactionDataMap[txNumber].totalPass != 0:
            meanResponseTime = self.transactionDataMap[txNumber].totalResponseTime / (1000.0 * passed)
        logger.debug("passed: %d, total rt: %d, mean rt: %f" % (passed, self.transactionDataMap[txNumber].totalResponseTime, meanResponseTime))
        return meanResponseTime
    
    def getMaxResponseTime(self, txNumber):
        return self.transactionDataMap[txNumber].maxResponseTime / 1000.0

    def toString(self):
        s = "start time: " + str(self.startTime)
        s += ", end time: " + str(self.endTime)
        for key in self.transactionNameDataMap.keys():
            s += "\n\t key: " + key
            #s += ", tx name: " + self.transactionNameDataMap[key]
            s += ", " + self.transactionNameDataMap[key].getStats()
        return s


class HTTPBucket(AbstractBucket):

    def __init__ (self, start, end, lAnalyzer):
        AbstractBucket.__init__(self, start, end, lAnalyzer)

    def __addTestData__(self, testNumber, columns):
        ''' Adds data from a single line in the grinder log to
        this bucket. '''
        responseTime = int(columns[analyzer.RESPONSE_TIME_COLUMN])
        self.transactionDataMap[testNumber].checkMaxResponseTime(responseTime)
        resolveTime = int(columns[analyzer.RESOLVE_TIME_COLUMN])
        connectTime = int(columns[analyzer.CONNECT_TIME_COLUMN])
        firstByteTime = int(columns[analyzer.FIRST_BYTE_TIME_COLUMN])
        passed = True
        if columns[analyzer.ERRORS_COLUMN].strip() != "0":
            passed = False
        bytes = long(columns[analyzer.BYTES_COLUMN])
        if passed:
            #logger.info("incrementing test number %s on txDatamap %s" %(testNumber, self.transactionDataMap))
            self.transactionDataMap[testNumber].incrementPassed()
        else:
            self.transactionDataMap[testNumber].incrementFailed()       
        self.transactionDataMap[testNumber].incrementBytes(bytes)
        self.transactionDataMap[testNumber].incrementResponseTime(responseTime)
        self.transactionDataMap[testNumber].incrementResolveTime(resolveTime)
        self.transactionDataMap[testNumber].incrementConnectTime(connectTime)
        self.transactionDataMap[testNumber].incrementFirstByteTime(firstByteTime)



    def getMeanFinishTime(self, txNumber):
        ''' For a given transaction name, reports the average amount of time
        between receiving the first byte and the completion of the request.'''
        meanResponseTime = 0.0
        passed = self.transactionDataMap[txNumber].totalPass
        if self.transactionDataMap[txNumber].totalPass != 0:
            meanResponseTime = (self.transactionDataMap[txNumber].totalResponseTime - self.transactionDataMap[txNumber].totalFirstByteTime) / (1000.0 * passed)
        logger.debug("passed: " + str(passed) + ", total ft:" + str(self.transactionDataMap[txNumber].totalResponseTime) + ", mean rt:" + str(meanResponseTime))
        return meanResponseTime

    def getMeanResolveHostTime(self, txNumber):
        '''
        Average time to resolve the hostname
        '''
        meanResolveTime = 0.0
        passed = self.transactionDataMap[txNumber].totalPass
        total_time=0
        if passed != 0:
            total_time = self.transactionDataMap[txNumber].totalResolveTime
            meanResolveTime = total_time / (1000.0 * passed)
        logger.debug("passed: %d, total resolve time: %d, mean resolve time: %f" % (passed,
                                                                                total_time,
                                                                                meanResolveTime))
        return meanResolveTime

    def getMeanConnectTime(self, txNumber):
        '''
        average time between host name resolution and connection establishment
        '''
        meanConnectTime = 0.0
        passed = self.transactionDataMap[txNumber].totalPass
        if self.transactionDataMap[txNumber].totalPass != 0:
            meanConnectTime = (self.transactionDataMap[txNumber].totalConnectTime - self.transactionDataMap[txNumber].totalResolveTime) / (1000.0 * passed)
        logger.debug("passed: %d, total connect time: %d, mean resolve time: %f" % (passed,
                                                                                self.transactionDataMap[txNumber].totalConnectTime,
                                                                                meanConnectTime))
        return meanConnectTime

    def getMeanFirstByteTime(self, txNumber):
        '''
        average time between connection establishment and reciept of the
        first response byte
        '''
        begin=1342733788743
        meanFirstByteTime = 0.0
        total_fb_time=0
        total_c_time=0
        passed = self.transactionDataMap[txNumber].totalPass
        if passed != 0:
            total_fb_time = self.transactionDataMap[txNumber].totalFirstByteTime
            total_c_time = self.transactionDataMap[txNumber].totalConnectTime
            meanFirstByteTime = (total_fb_time - total_c_time) / (1000.0 * passed)
        if meanFirstByteTime < 0:
            logger.info("\n")
        return meanFirstByteTime
    
    def getMeanThroughputKBSec(self, txNumber):
        ''' For a given transaction name, reports the average
        throughput measured in KB/sec. '''
        secondsPerBucket = self.bucketDurationMs / 1000.0
        bytesPerKB = 1024.0
        return self.transactionDataMap[txNumber].totalBytesDownloaded * self.logAnalyzer.getAgentMultiplier() / (bytesPerKB * secondsPerBucket)



class NonHTTPBucket(AbstractBucket):

    def __init__ (self, start, end, lAnalyzer):
        AbstractBucket.__init__(self, start, end, lAnalyzer)
        
    # TODO - have HTTPBucket call this method to avoid code duplication
    def __addTestData__(self, testNumber, columns):
        ''' Adds data from a single line in the grinder log to
        this bucket. '''
        responseTime = int(columns[analyzer.RESPONSE_TIME_COLUMN])
        self.transactionDataMap[testNumber].checkMaxResponseTime(responseTime)
        passed = True
        if columns[analyzer.ERRORS_COLUMN].strip() != "0":
            passed = False
        if passed:
            #logger.info("incrementing test number %s on txDatamap %s" %(testNumber, self.transactionDataMap))
            self.transactionDataMap[testNumber].incrementPassed()
        else:
            self.transactionDataMap[testNumber].incrementFailed()       
        self.transactionDataMap[testNumber].incrementResponseTime(responseTime)




#####################################################################
# Container class
#####################################################################
class TransactionBucketData:
    """
    Simple data structure to hold per-bucket statistics for each
    transaction.  Non-HTTP Buckets ignore some of these fields.
    """ 
    totalPass = 0
    totalFail = 0
    totalBytesDownloaded = 0
    totalResponseTime = 0
    totalResolveTime = 0
    totalConnectTime = 0
    totalFirstByteTime = 0
    maxResponseTime = 0        # local (per-bucket) max.  Not global max.
    
    def getStats(self):
        stats = "Pass: " + str(self.totalPass) 
        stats += ", failed: " + str(self.totalFail) 
        stats += ", bytes: " + str(self.totalBytesDownloaded) 
        stats += ", rt: " + str(self.totalResponseTime)
        return stats
    def incrementPassed(self):
        self.totalPass += 1       
    def incrementFailed(self):
        self.totalFail += 1
    def incrementBytes(self, bytes):
        self.totalBytesDownloaded += bytes
    def incrementResponseTime(self, rt):
        self.totalResponseTime += rt
    def incrementResolveTime(self, rt):
        self.totalResolveTime += rt
    def incrementConnectTime(self, ct):
        self.totalConnectTime += ct
    def incrementFirstByteTime(self, fbt):
        self.totalFirstByteTime += fbt
    def checkMaxResponseTime(self, responseTime):
        if responseTime > self.maxResponseTime:
            self.maxResponseTime = responseTime


def getBucket(startTime, endTime, analyzer):
    '''
    Function to return a bucket of the correct type (HTTP/Non-HTTP)
    '''
    if ga.constants.VORPAL.getPlugin("analyzer").isHTTP():
        return HTTPBucket(startTime, endTime, analyzer)
    else:
        return NonHTTPBucket(startTime, endTime, analyzer)


logger = Logger.getLogger("ga.bucket")
