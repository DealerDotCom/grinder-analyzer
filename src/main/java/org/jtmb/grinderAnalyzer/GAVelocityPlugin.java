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

import java.util.Properties;
import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;
import java.util.Set;
import org.apache.log4j.Logger;

public class GAVelocityPlugin {

    protected ArrayList<String> columnNames = new ArrayList<String>();
    // key: tx name, val: ReportRow
    protected HashMap<String, ReportRow> rowMap = new HashMap<String, ReportRow>();

    protected HashMap<String, String> graphMap = new HashMap<String, String>();
    protected ReportRow totalsRow = null;
    protected Configuration config;
    private static final Logger logger = Logger.getLogger(GAVelocityPlugin.class);
    private boolean isHTTP = false;

    public GAVelocityPlugin(Properties p) {
        this.config = new Configuration(p);
        if (config.isShowTests()) {
            columnNames.add(Columns.TEST_PASSED);
        }
        if (config.isShowErrors()) {
            columnNames.add(Columns.TESTS_ERRS);
        }
        if (config.isShowErrorRate()) {
            columnNames.add(Columns.PASS_RATE);
        }
        if (config.isShowMeanTime()) {
            columnNames.add(Columns.RTIME);
        }
        if (config.isShowStandardDev()) {
            columnNames.add(Columns.RTIME_STD_DEV);
        }
        if (config.isShowTPS()) {
            columnNames.add(Columns.TPS);
        }
        graphMap.put(Columns.TX_NAME, "perf");
        graphMap.put(Columns.RTIME, "meanMax_rtime");
        for (String name : columnNames) {
            logger.debug("non - HTTP Column name: " + name);
        }
    }

    public void addDataRow(ReportRow r) {
        String name = r.getTxName();
        this.rowMap.put(name, r);
    }

    public Object[] getDataRows() {
        return this.rowMap.values().toArray();
    }

    public ReportRow getRow(String name) {
        return this.rowMap.get(name);
    }

    public void updateRow(String name, ReportRow row) {
        this.rowMap.put(name, row);
    }

    public List<String> getColumnNames() {
        return columnNames;
    }

    public void addColumnName(String name) {
        logger.debug("Adding column -- " + name);
        columnNames.add(name);
    }

    public boolean isHTTP() {
        return this.isHTTP;
    }
    
    /**
     * Setting this plugin to HTTP-mode is a one-way operation.
     *  
     **/
    public void enableHTTPStatistics() {
        logger.warn("Enabling statistics for HTTP tests.");
        if (! this.isHTTP) {
            if (config.isShowResponseLength()) {
                columnNames.add(Columns.RESPONSE_LEN);
            }
            if (config.isShowBytesPerSec()) {
                columnNames.add(Columns.BYTES_PERSEC);
            }
            if (config.isShowResponseErrors()) {
                columnNames.add(Columns.RESPONSE_ERRORS);
            }
            if (config.isShowResolveHost()) {
                columnNames.add(Columns.RESOLVE_HOST);
            }
            if (config.isShowConnect()) {
                columnNames.add(Columns.CONNECT);
            }
            if (config.isShowFirstByte()) {
                columnNames.add(Columns.FIRST_BYTE);
            }
            graphMap.put(Columns.BYTES_PERSEC, "bandwidth");
            graphMap.put(Columns.FIRST_BYTE, "rtime");
            for (String name : columnNames) {
                logger.debug(" HTTP Column name: " + name);
            }
        }
        this.isHTTP = true;
    }


    public ReportRow getTotalsRow() {
        return totalsRow;
    }

    public void setTotalsRow(ReportRow r) {
        this.totalsRow = r;
    }
    
    /**
     * Wrapper for config.getOSStatsLink()
     * @return
     */
    public String getOsStatsLink(){
        if (!this.config.isUseOSStats()) {
            return "";
        }
        return this.config.getOSStatsLink();
    }

    /**
     * Returns a set of all transaction names
     * 
     * @return
     */
    public Set<String> getTxNames() {
        return this.rowMap.keySet();
    }

    /**
     * 
     * For a given column in the report, return which graph (if any) that should be linked to.
     * 
     * @param columnName
     * @return
     * 
     *         May want to move the graph mappings to the report row classes
     */
    public String getColumnGraph(String columnName) {
        if (graphMap.containsKey(columnName)) {
            return graphMap.get(columnName);
        }
        return "";
    }

    /**
     * Gets the names of the response time group columns defined by the user in the config.
     * 
     * @return
     */
    public List<String> getRtgroupColumnNames() {
        ArrayList<String> responseTimeColumnNames = new ArrayList<String>();
        for (String name : columnNames) {
            if (name.toUpperCase().endsWith(" SEC") && !name.equals(Columns.BYTES_PERSEC)) {
                responseTimeColumnNames.add(name);
            }
        }
        return responseTimeColumnNames;
    }

    /**
     * @param args
     */
    public static void main(String[] args) {
        System.out.println("Main method -- for running quick tests in the IDE");

    }
}
