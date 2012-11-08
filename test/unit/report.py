import ga.report
import ga.summary
import unittest
import os

class TestGetGrinderVersion(unittest.TestCase):

    def test_major_minor(self):
        '''
        2.3
        '''
        majorVersion = "2"
        minorVersion = "3"
        versionString = "%s.%s" % (majorVersion, minorVersion)
        versionData = ga.report._getGrinderVersion(ga.report.GRINDER_VERSION_TAG + versionString)
        self.assertEqual(versionData[0], versionString)
        self.assertEqual(versionData[1], majorVersion)
        self.assertEqual(versionData[2], minorVersion)
        self.assertEqual(len(versionData), 4)
        
    def test_major_minor_build(self):
        '''
        4.5.22-beta
        '''
        majorVersion = "4"
        minorVersion = "5"
        buildVersion = "22-beta"
        versionString = "%s.%s.%s" % (majorVersion, minorVersion, buildVersion)
        versionData = ga.report._getGrinderVersion(ga.report.GRINDER_VERSION_TAG + versionString)
        self.assertEqual(versionData[0], versionString)
        self.assertEqual(versionData[1], majorVersion)
        self.assertEqual(versionData[2], minorVersion)
        self.assertEqual(versionData[3], buildVersion)
        self.assertEqual(len(versionData), 4)
        
    def test_extra_fields(self):
        '''
        11.22.33.44.55.66-arst
        '''
        majorVersion = "11"
        minorVersion = "22"
        buildVersion = "33.44.55.66-arst"
        versionString = "%s.%s.%s" % (majorVersion, minorVersion, buildVersion)
        versionData = ga.report._getGrinderVersion(ga.report.GRINDER_VERSION_TAG + versionString)
        self.assertEqual(versionData[0], versionString)
        self.assertEqual(versionData[1], majorVersion)
        self.assertEqual(versionData[2], minorVersion)
        self.assertEqual(versionData[3], buildVersion.split(".")[0])
        self.assertEqual(len(versionData), 4)
        
    def test_missing_fields(self):
        '''
        3
        '''
        versionData = ga.report._getGrinderVersion(ga.report.GRINDER_VERSION_TAG + "3")
        self.assertTrue(versionData == None)


    def test_g30_beta33(self):
        '''
        3.0-beta33
        '''
        majorVersion = "3"
        minorVersion = "0-beta33"
        versionString = "%s.%s" % (majorVersion, minorVersion)
        versionData = ga.report._getGrinderVersion(ga.report.GRINDER_VERSION_TAG + versionString)
        self.assertEqual(versionData[0], versionString)
        self.assertEqual(versionData[1], majorVersion)
        self.assertEqual(versionData[2], "0")
        self.assertEqual(len(versionData), 4)


class TestGetReporter(unittest.TestCase):

    def test_unsupported_old_version(self):
        reporter = ga.report.getReporter(None, G30_HTTP_SUMMARY_DATA, ga.report.GRINDER_VERSION_TAG + "2.4.6")
        self.assertTrue(reporter == None)
    
    def test_unsupported_future_major_version(self):
        reporter = ga.report.getReporter(None, G30_HTTP_SUMMARY_DATA, ga.report.GRINDER_VERSION_TAG + "4.4.6")
        self.assertTrue(reporter == None)
        
    def test_g30_nonHttp(self):
        reporter = ga.report.getReporter(None, G30_NON_HTTP_SUMMARY_DATA, ga.report.GRINDER_VERSION_TAG + "3.0.0")
        self.assertTrue(isinstance(reporter, ga.report.LegacyNonHTTPReporter))
    
    def test_g30_Http(self):
        reporter = ga.report.getReporter(None, G30_HTTP_SUMMARY_DATA, ga.report.GRINDER_VERSION_TAG + "3.0.0")
        self.assertTrue(isinstance(reporter, ga.report.LegacyHTTPReporter))
        
    def test_g32_Http(self):
        reporter = ga.report.getReporter(None, G32_HTTP_SUMMARY_DATA, ga.report.GRINDER_VERSION_TAG + "3.2")
        self.assertTrue(isinstance(reporter, ga.report.G32HTTPReporter))
    
    def test_g38_Http(self):
        reporter = ga.report.getReporter(None, G38_HTTP_SUMMARY_DATA, ga.report.GRINDER_VERSION_TAG + "3.8")
        self.assertTrue(isinstance(reporter, ga.report.G32HTTPReporter))
    
    def test_g38_nonHttp(self):
        reporter = ga.report.getReporter(None, G38_NON_HTTP_SUMMARY_DATA, ga.report.GRINDER_VERSION_TAG + "3.8")
        self.assertTrue(isinstance(reporter, ga.report.G32NonHTTPReporter))
        
    def test_unsupported_future_minor_version(self):
        reporter = ga.report.getReporter(None, G30_HTTP_SUMMARY_DATA, ga.report.GRINDER_VERSION_TAG + "3.999")
        self.assertTrue(reporter == None)    


LEGACY_LOGS_DIR = "../functional/legacy_grinder_logs"
CURRENT_LOGS_DIR = "../functional/grinder_logs"
G38_HTTP_SUMMARY_DATA = ga.summary.SummaryDataRegistry(CURRENT_LOGS_DIR + os.sep + "g38HTTP/ubuntu-0.log")
G38_NON_HTTP_SUMMARY_DATA = ga.summary.SummaryDataRegistry(CURRENT_LOGS_DIR + os.sep + "g38NonHTTP/ubuntu-0.log")
G32_HTTP_SUMMARY_DATA = ga.summary.SummaryDataRegistry(LEGACY_LOGS_DIR + os.sep + "g32Normal/out_travisb01-0.log")
G30_HTTP_SUMMARY_DATA = ga.summary.SummaryDataRegistry(LEGACY_LOGS_DIR + os.sep + "g30Normal/out_agent16-0.log")
G30_NON_HTTP_SUMMARY_DATA = ga.summary.SummaryDataRegistry(LEGACY_LOGS_DIR + os.sep + "g30NonHTTP/out_0.log")

