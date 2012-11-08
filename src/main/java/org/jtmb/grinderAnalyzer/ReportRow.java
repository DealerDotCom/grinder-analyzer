/*
 Copyright (C) 2007-2012, Travis Bear
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

import java.text.NumberFormat;
import org.apache.log4j.Logger;
import java.util.HashMap;
import java.util.Locale;

public class ReportRow {

    private String txName;
    private NumberFormat inputNumberFormat; // used when parsing the grinder log file
    private NumberFormat outputNumberFormat;
    private NumberFormat outputPercentFormat;
    private static final Logger logger = Logger.getLogger(ReportRow.class);

    private HashMap<String, Number> transactionData;

    public ReportRow(Configuration config) {
        if (config.isNonDefaultLocale()) {
            // assume that at a minimum, a language has been provided
            Locale locale = new Locale(config.getLocaleLanguage());
            if (! config.getLocaleCountry().equals("")) {
                locale = new Locale(config.getLocaleLanguage(), config.getLocaleCountry());
            }
            if (! config.getLocaleVariant().equals("")) {
                locale = new Locale(config.getLocaleLanguage(),
                        config.getLocaleCountry(),
                        config.getLocaleVariant());
            }
            inputNumberFormat = NumberFormat.getNumberInstance(locale);
        }
        else {
            inputNumberFormat = NumberFormat.getNumberInstance(); // default locale
        }
        outputNumberFormat = NumberFormat.getNumberInstance();
        outputPercentFormat = NumberFormat.getNumberInstance();
        this.outputPercentFormat.setMaximumFractionDigits(3);
        this.outputPercentFormat.setMinimumFractionDigits(3);
        this.transactionData = new HashMap<String, Number>();
    }

    private NumberFormat getOutputNumberFormat(String columnName) {
        // pass/fail column is in percent format
    	if (columnName.equals(Columns.PASS_RATE)) {
    		return outputPercentFormat;
    	}
    	// response time group columns are in percent format
    	if (columnName.toUpperCase().endsWith(" SEC") && ! columnName.equals(Columns.BYTES_PERSEC)) {
    		return outputPercentFormat;
    	}
    	return outputNumberFormat;
    }
    
    public String getColumnData(String columnName) {
        Number num = getColumnDataAsNum(columnName);
        if (num.floatValue() < 0.0) {
        	return "";
        }
        return getOutputNumberFormat(columnName).format(num);
    }

    public Number getColumnDataAsNum(String columnName) {
    	return (transactionData.containsKey(columnName) ? transactionData.get(columnName) : 0);   
	}
    
    private Number getNumberFromString(String num) {
    // expects a String in the format of the input locale
        try {
            return inputNumberFormat.parse(num);
        } catch (Exception e) {
            logger.debug("Couldn't parse '" + num + "' as a number.  Using -1");
            return -1;
        }
    }

    public void setTests(String tests) {
        transactionData.put(Columns.TEST_PASSED, getNumberFromString(tests));
    }

    public void setErrors(String errors) {
        transactionData.put(Columns.TESTS_ERRS, getNumberFromString(errors));
    }

    public void setMeanTestTime(String meanTestTime) {
        transactionData.put(Columns.RTIME, getNumberFromString(meanTestTime));
    }

    public void setTestTimeStandardDev(String testTimeStandardDev) {
        transactionData.put(Columns.RTIME_STD_DEV, getNumberFromString(testTimeStandardDev));
    }

    public void setMeanResponseLength(String meanResponseLength) {
        transactionData.put(Columns.RESPONSE_LEN, getNumberFromString(meanResponseLength));
    }

    public void setBytesPerSec(String bytesPerSec) {
        transactionData.put(Columns.BYTES_PERSEC, getNumberFromString(bytesPerSec));
    }

    public void setResponseErrors(String responseErrors) {
        transactionData.put(Columns.RESPONSE_ERRORS, getNumberFromString(responseErrors));
    }

    public void setTPS(String tps) {
        transactionData.put(Columns.TPS, getNumberFromString(tps));
    }

    public void setMeanTimeResolveHost(String meanTimeResolveHost) {
        transactionData.put(Columns.RESOLVE_HOST, getNumberFromString(meanTimeResolveHost));
    }

    public void setMeanTimeConnection(String meanTimeConnection) {
        transactionData.put(Columns.CONNECT, getNumberFromString(meanTimeConnection));
    }

    public void setMeanTimeFirstByte(String meanTimeFirstByte) {
        transactionData.put(Columns.FIRST_BYTE, getNumberFromString(meanTimeFirstByte));
    }

    public void addNumericTransactionData(String key, Float val) {
        transactionData.put(key, (Number) val);
    }
    
    public String getTxName() {
        return txName;
    }

    public String getSafeTxName() {
        return txName.replaceAll(" ", "_").replaceAll("/", "_").replaceAll(":", "_");
    }

    public void setTxName(String txName) {
        this.txName = txName;
    }

    public void calculatePassRate() {
        double tests = getColumnDataAsNum(Columns.TEST_PASSED).doubleValue();
        double errors = getColumnDataAsNum(Columns.TESTS_ERRS).doubleValue();
        double rate = tests + errors == 0 ? 0 : 1.0 - errors / (errors + tests);
        transactionData.put(Columns.PASS_RATE, (Number) new Double(rate));
    }

}
