# Copyright (C) 2010-2012, Travis Bear
# All rights reserved.
##
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



"""
Based on the simple HTTP script in the Grinder script gallery.

Dirt-simple grinder test script.  Purpose is to hit a local tomcat to generate
some test data which may then be run through grinder analyzer.  Useful when
new revs of The Grinder become available and we need to test the analyzer
against any changes in the log file format.

Classes:

    TestRunner:     main entry point for the grinder


"""



from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder

# constants
TOMCAT_HOST = "qa-perftest001"
TOMCAT_PORT = 8080
THINK_TIME = 400

test1 = Test(1, "Tomcat home")
request1 = test1.wrap(HTTPRequest())
# http://localhost:8080
url1 = "http://%s:%d" % (TOMCAT_HOST, TOMCAT_PORT)

test2 = Test(2, "Tomcat relnotes")
request2 = test2.wrap(HTTPRequest())
# http://localhost:8080/RELEASE-NOTES.txt
url2 = "http://%s:%d/RELEASE-NOTES.txt" % (TOMCAT_HOST, TOMCAT_PORT)

test3 = Test(3, "Tomcat documentation")
request3 = test3.wrap(HTTPRequest())
# http://localhost:8080/docs/
url3 = "http://%s:%d/docs/" % (TOMCAT_HOST, TOMCAT_PORT)

test4 = Test(4, "Tomcat servlets")
request4 = test4.wrap(HTTPRequest())
# http://localhost:8080/examples/servlets/
url4 = "http://%s:%d/examples/servlets/" % (TOMCAT_HOST, TOMCAT_PORT)

log = grinder.logger.info 

class TestRunner:
    """ Grinder entry point """
    def __call__(self):
        print ("Sending %s" % url1)
        request1.setUrl(url1)
        request1.setUrl('http://www.google.com')
        response1=request1.GET()

        print ("Sending %s" % url2)
        request2.GET(url2)
        
        print ("Sending %s" % url3)
        request3.GET(url3)
        
        print ("Sending %s" % url4)
        request4.GET(url4)

        log(" ------- ======== %s " %request1.getUrl())
        #log(" ------- ======== %s " %response1.getText())
        log(" ------- ======== %s " %response1.toString())


        grinder.sleep(THINK_TIME)
