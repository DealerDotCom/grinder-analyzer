/*
 Copyright (C) 2010-2012, Travis Bear
 All rights reserved.

 This file is part of Grinder Analyzer.

 Grinder Analyzer is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 Grinder Analyzer is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Grinder Analyzer; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */



package org.jtmb.grinderAnalyzer;

public class Columns {
    // all these these values to appear as column names in the
    // generated .html report
    
    // all tests
    public static final String TX_NAME = "Transacton Name";
    public static final String TEST_PASSED = "Tests Passed";
    public static final String TESTS_ERRS = "Tests w/ Errors";
    public static final String PASS_RATE = "Pass Rate";
    public static final String RTIME = "Mean Response Time";
    public static final String RTIME_STD_DEV = "Response time standard dev.";
    public static final String TPS = "Tx/Sec";
    
    //http tests
    public static final String RESPONSE_LEN = "Mean Response Length";
    public static final String BYTES_PERSEC = "Bytes per Sec";
    public static final String RESPONSE_ERRORS = "Response Errors";
    public static final String RESOLVE_HOST = "Mean Time Resolve Host";
    public static final String CONNECT = "Mean Time Establish Connection";
    public static final String FIRST_BYTE = "Mean Time to First Byte"; 
}
