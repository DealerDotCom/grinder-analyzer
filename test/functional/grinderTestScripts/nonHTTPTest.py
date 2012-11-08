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

Classes:

    TestRunner:     main entry point for the grinder

"""

from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
 
test1 = Test(1, "Log method")
 
# Wrap the info() method with our Test and call the result logWrapper.
logWrapper = test1.wrap(grinder.logger.info)
 
class TestRunner:
    def __call__(self):
        logWrapper("Hello World")
        grinder.sleep(250)

