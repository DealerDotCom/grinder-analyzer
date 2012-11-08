"""
This module is an example Logster parser for Grinder logs.  It is not
a general-purpose solution, and will take some modification before
it will be useful in your particular case.
"""

import time
import re
import sys
import traceback

from logster_helper import MetricObject, LogsterParser
from logster_helper import LogsterParsingException

# mappings for Grinder 3.6, HTTP-format requests
COL_Thread=0
COL_Run=1
COL_Test=2
COL_Start_time=3
COL_Test_time=4
COL_Errors=5
COL_HTTP_response_code=6
COL_HTTP_response_length=7
COL_HTTP_response_errors=8
COL_Time_to_resolve_host=9
COL_Time_to_establish_connection=10
COL_Time_to_first_byte=11
INFINITY = 999999999.0
RESPONSE_TIME_THRESHOLDS_MS = [50.0,75.0,120.0,INFINITY]
class TestStats:
    """
    container class for all the different metrics associated with a 
    single test:  pass/fail rate, various components of response
    time, etc.
    """
    def __init__(self, test_name, test_num):
        self.test_name = test_name
        self.test_num = test_num
        self.test_time=0.0
        self.pass_count=0.0
        self.fail_count=0.0
        self.response_length=0.0
        self.time_resolve_host=0.0
        self.time_establish_connection=0.0
        self.time_first_byte=0.0
        self.total_lines = 0.0
        self.name = ""
        self.response_time_groups = {}
        for threshold in RESPONSE_TIME_THRESHOLDS_MS:
            self.response_time_groups[threshold] = 0.0

    def __str__(self):
        return "-- %s, %d lines" %(self.name, self.total_lines)



class GrinderLogster(LogsterParser):

    def __init__(self, option_string=None):
        self.lines = 0.0
        self.dc_e_test = TestStats("dc_e", "0")


    def _get_time_threshold(self, test_stats, test_time):
        #print "Getting threshold for time: %d in %s" %(test_time, RESPONSE_TIME_THRESHOLDS_MS)
        for threshold in RESPONSE_TIME_THRESHOLDS_MS:
           if test_time < threshold:
              return threshold

 
    def parse_line(self, line):
        words = line.split(', ')
        test_num = words[COL_Test].strip()
        current_test = self.dc_e_test
        if test_num == "2":
            current_test = self.dc_f_test
        try:
            if words[COL_Errors] == "0":
                current_test.pass_count += 1.0
            else:
                current_test.fail_count += 1.0
            test_time = float(words[COL_Test_time])
            current_test.test_time += test_time
            #print "words: %s, tt_col: %d, test time: %d, %d" %(words, COL_Test_time, current_test.test_time, float(words[COL_Test_time]))
            current_test.response_length += float(words[COL_HTTP_response_length])
            current_test.time_resolve_host += float(words[COL_Time_to_resolve_host])
            current_test.time_establish_connection += float(words[COL_Time_to_establish_connection])
            current_test.time_first_byte += float(words[COL_Time_to_first_byte])
            current_test.total_lines += 1.0 
            current_test.response_time_groups[self._get_time_threshold(current_test, test_time)] += 1.0
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            raise LogsterParsingException, "Line '%s' does not appear to be a valid grinder log message.\n %s" % (line, e)


    def _add_metrics(self, metrics_list, test_stats):
        '''
        metrics_list is an output param
        '''
        #TODO: divide by "total passed" instead of "total lines"
        metrics_list.append(MetricObject("%s.test_time" %test_stats.test_name, (test_stats.test_time / test_stats.total_lines), "ms"))
        metrics_list.append(MetricObject("%s.pass_rate" %test_stats.test_name, (test_stats.pass_count / test_stats.total_lines), "rate"))
        metrics_list.append(MetricObject("%s.resolve_host" %test_stats.test_name, (test_stats.time_resolve_host / test_stats.total_lines), "ms"))
        metrics_list.append(MetricObject("%s.establish_connection" %test_stats.test_name, (test_stats.time_establish_connection / test_stats.total_lines), "ms"))
        metrics_list.append(MetricObject("%s.first_byte" %test_stats.test_name, (test_stats.time_first_byte / test_stats.total_lines), "ms"))
        # handle response time groups
        # TODO: generalize this... assumes specific set of response
        #       time groups  [0.05,0.075,0.12,9999999.0]
        threshold_keys = RESPONSE_TIME_THRESHOLDS_MS
        metrics_list.append(MetricObject("%s.under_%d_ms" %(test_stats.test_name, threshold_keys[0]), (test_stats.response_time_groups[threshold_keys[0]] / test_stats.total_lines), "rate"))
        metrics_list.append(MetricObject("%s.%d_to_%d_ms" %(test_stats.test_name, threshold_keys[0], threshold_keys[1]), (test_stats.response_time_groups[threshold_keys[1]] / test_stats.total_lines), "rate"))
        metrics_list.append(MetricObject("%s.%d_to_%d_ms" %(test_stats.test_name, threshold_keys[1], threshold_keys[2]), (test_stats.response_time_groups[threshold_keys[2]] / test_stats.total_lines), "rate"))
        metrics_list.append(MetricObject("%s.over_%d_ms" %(test_stats.test_name, threshold_keys[2]), (test_stats.response_time_groups[threshold_keys[3]] / test_stats.total_lines), "rate"))

    def get_state(self, duration):
        self.duration = duration
        outlines = []
        if self.dc_e_test.total_lines > 0:
            self._add_metrics(outlines, self.dc_e_test)
        return outlines

