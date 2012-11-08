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

import java.io.File;
import java.io.FileInputStream;
import java.util.Properties;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import org.apache.log4j.Logger;
import org.jtmb.velocityMerger.VelocityMerger;

public class Configuration {

    private Properties props;
    private String reportDir;

    // chart settings
    private int buckets;
    private boolean showDate; // this setting for graphs, not report columns
    private int tpsChartWidth;
    private int tpsChartHeight;
    private int bwChartWidth;
    private int bwChartHeight;
    private int rtChartWidth;
    private int rtChartHeight;
    private int tpsWeight;
    private int responseTimeWeight;
    private String dateFormat;
    private boolean useThresholds = true;
    private List<Float> rtimeThresholds;
    
    private boolean showTransactionData = true;

    // enabled columns in all reports
    private boolean showTests = true;
    private boolean showErrors = true;
    private boolean showErrorRate = true;
    private boolean showMeanTime = true;
    private boolean showStandardDev = true;
    private boolean showTPS = false;

    // additional enabled columns in HTTP reports
    private boolean showResponseLength = true;
    private boolean showBytesPerSec = true;
    private boolean showResponseErrors = false;
    private boolean showResolveHost = true;
    private boolean showConnect = true;
    private boolean showFirstByte = true;
    
    // locale settings
    private boolean useNonDefautLocale = false;
    private String localeLanguage = "";
    private String localeCountry = "";
    private String localeVariant = "";
    
    // link to OS-level stats
    private boolean useOSStats = false;
    private String OSStatsLink = "";

    // defaults
    private static final String NEWLINE = "\n"; // TODO get from System props
    private static final String INDENT = "   ";
    private static final Float MAX_POSSIBLE_TIME = new Float(99999999.9);
    private static final String DEFAULT_CONFIG_FILE = "conf/analyzer.properties";
    private static final String DEFAULT_BUCKETS = "250";
    private static final String DEFAULT_BW_CHART_HEIGHT = "320";
    private static final String DEFAULT_BW_CHART_WIDTH = "640";
    private static final String DEFAULT_RT_CHART_HEIGHT = "640";
    private static final String DEFAULT_RT_CHART_WIDTH = "380";
    private static final String DEFAULT_DATE_FORMAT = "'Test executed' MMMM dd yyyy, HH:MM";
    private static final String DEFAULT_RTIME_WEIGHT = "1";
    private static final String DEFAULT_TPS_WEIGHT = "3";
    private static final String DEFAULT_TPS_CHART_HEIGHT = "640";
    private static final String DEFAULT_TPS_CHART_WIDTH = "460";
    private static final String DEFAULT_REPORT_DIR = "grinderReport";
    private static final String DEFAULT_OSSTATS_LINK = "..";

    private static final Logger logger = Logger.getLogger(Configuration.class);

    public Configuration(String configFile) {
        this.props = new Properties();
        System.out.println("Loading analyzer configs at " + configFile);
        File file = new File(configFile);
        if (!file.exists()) {
            System.err.println("FATAL: could not locate config file '" + file.getAbsolutePath() + "'");
            System.exit(1);
        }
        try {
            FileInputStream fis = new FileInputStream(file);
            props.load(fis);
        } catch (Exception e) {
            System.err.println("FATAL: error loading config file " + file.getAbsolutePath());
            System.exit(1);
        }
        loadConfig();
    }

    public Configuration(Properties p) {
        this.props = p;
        loadConfig();
    }

    private void loadConfig() {
        buckets = getIntProperty("buckets", DEFAULT_BUCKETS);
        reportDir = props.getProperty("report_dir", DEFAULT_REPORT_DIR);
        bwChartHeight = getIntProperty("bw_chart_height", DEFAULT_BW_CHART_HEIGHT);
        bwChartWidth = getIntProperty("bw_chart_width", DEFAULT_BW_CHART_WIDTH);
        dateFormat = props.getProperty("date_format", DEFAULT_DATE_FORMAT);
        responseTimeWeight = getIntProperty("response_time_weight", DEFAULT_RTIME_WEIGHT);
        rtChartHeight = getIntProperty("rt_chart_height", DEFAULT_RT_CHART_HEIGHT);
        rtChartWidth = getIntProperty("rt_chart_width", DEFAULT_RT_CHART_WIDTH);
        tpsChartHeight = getIntProperty("tps_chart_height", DEFAULT_TPS_CHART_HEIGHT);
        tpsChartWidth = getIntProperty("tps_chart_width", DEFAULT_TPS_CHART_WIDTH);
        tpsWeight = getIntProperty("tps_weight", DEFAULT_TPS_WEIGHT);

        showTransactionData = getBoolProperty("show_transaction_data", "true");
        showDate = getBoolProperty("show_date", "false");
        showTests = getBoolProperty("show_tests", "false");
        showErrors = getBoolProperty("show_errors", "false");
        showErrorRate = getBoolProperty("show_error_rate", "false");
        showMeanTime = getBoolProperty("show_mean_time", "false");
        showStandardDev = getBoolProperty("show_standard_dev", "false");
        showTPS = getBoolProperty("show_TPS", "false");

        showResponseLength = getBoolProperty("show_response_length", "false");
        showBytesPerSec = getBoolProperty("show_bytes_per_sec", "false");
        showResponseErrors = getBoolProperty("show_response_errors", "false");
        showResolveHost = getBoolProperty("show_resolve_host", "false");
        showConnect = getBoolProperty("show_connect", "false");
        showFirstByte = getBoolProperty("show_first_byte", "false");
        
        // locale settings
        useNonDefautLocale = getBoolProperty("use_non_default_locale", "false");
        localeLanguage = props.getProperty("user.language"); // no default
        localeCountry = props.getProperty("user.country");   // no default
        localeVariant = props.getProperty("user.variant");   // no default (get from sys properties?)
        
        // OS stats link
        useOSStats = getBoolProperty("use_os_perf_link", "false");
        OSStatsLink = props.getProperty("os_perf_link", DEFAULT_OSSTATS_LINK);

        // get the response time thresholds
        useThresholds = getBoolProperty("use_thresholds", "false");
        rtimeThresholds = new ArrayList<Float>();
        String thresholdsProperty = props.getProperty("response_time_thresholds", "");
        if (thresholdsProperty != "") {
            for (String word : thresholdsProperty.split(",")) {
                rtimeThresholds.add(new Float(word));
            }
        }
        if (rtimeThresholds.size() == 0) {
            //Thresholds were enabled but not defined.  Disabling feature
            useThresholds = false;
        } else {
            rtimeThresholds.add(MAX_POSSIBLE_TIME);
            Collections.sort(rtimeThresholds);
        }
    }

    private Float getFloatProperty(String propname, String defaultValue) {
        Float floatProp = null;
        String property = props.getProperty(propname, defaultValue);
        try {
            floatProp = new Float(property);
        } catch (NumberFormatException nfe) {
            System.err.println("FATAL: '" + property + "' is an invalid config setting for '" + propname + "'.");
            System.exit(1);
        }
        return floatProp;
    }

    private Integer getIntProperty(String propname, String defaultValue) {
        Integer intProp = null;
        String property = props.getProperty(propname, defaultValue);
        try {
            intProp = new Integer(property);
        } catch (NumberFormatException nfe) {
            System.err.println("FATAL: '" + property + "' is an invalid config setting for '" + propname + "'.");
            System.exit(1);
        }
        return intProp;
    }

    private boolean getBoolProperty(String propname, String defaultValue) {
        String property = props.getProperty(propname, defaultValue);
        return property.toLowerCase().startsWith("t");
    }

    public int getBuckets() {
        return buckets;
    }

    public boolean isShowDate() {
        return showDate;
    }

    public int getTpsChartWidth() {
        return tpsChartWidth;
    }

    public int getTpsChartHeight() {
        return tpsChartHeight;
    }

    public int getBwChartWidth() {
        return bwChartWidth;
    }

    public int getBwChartHeight() {
        return bwChartHeight;
    }

    public int getRtChartWidth() {
        return rtChartWidth;
    }

    public int getRtChartHeight() {
        return rtChartHeight;
    }

    public int getTpsWeight() {
        return tpsWeight;
    }

    public int getResponseTimeWeight() {
        return responseTimeWeight;
    }

    public String getDateFormat() {
        return dateFormat;
    }
    
    public boolean isShowTransactionData() {
        return this.showTransactionData;
    }

    public boolean isUseThresholds() {
        return useThresholds;
    }

    public Object[] getRtimeThresholds() {
        return rtimeThresholds.toArray();
    }

    public boolean isShowTests() {
        return showTests;
    }

    public boolean isShowErrors() {
        return showErrors;
    }

    public boolean isShowMeanTime() {
        return showMeanTime;
    }

    public boolean isShowErrorRate() {
        return showErrorRate;
    }

    public boolean isShowStandardDev() {
        return showStandardDev;
    }

    public boolean isShowTPS() {
        return showTPS;
    }

    public boolean isShowResponseLength() {
        return showResponseLength;
    }

    public boolean isShowBytesPerSec() {
        return showBytesPerSec;
    }

    public boolean isShowResponseErrors() {
        return showResponseErrors;
    }

    public boolean isShowResolveHost() {
        return showResolveHost;
    }

    public boolean isShowConnect() {
        return showConnect;
    }

    public boolean isShowFirstByte() {
        return showFirstByte;
    }
    
    public boolean isNonDefaultLocale() {
        return useNonDefautLocale;
    }
    
    public String getLocaleLanguage() {
        return localeLanguage;
    }
    
    public String getLocaleCountry() {
        return localeCountry;
    }
    
    public String getLocaleVariant() {
        return localeVariant;
    }

    public int getTPSWeight() {
        return tpsWeight;
    }
    
    public Properties getStartupProperties() {
        return props;
    }

    public String getReportDir() {
        return reportDir;
    }
    
    public boolean isUseOSStats() {
        return useOSStats;
    }
    
    public String getOSStatsLink() {
        return OSStatsLink;
    }

    public String toString() {
        StringBuffer sb = new StringBuffer("GRINDER ANALYZER CONFIG" + NEWLINE);
        sb.append(INDENT + "Report directory: " + new File(this.reportDir).getAbsolutePath() + NEWLINE);
        sb.append(INDENT + "Buckets: " + this.buckets + NEWLINE);
        sb.append(INDENT + "Show date in charts: " + this.showDate + NEWLINE);
        sb.append(INDENT + "Bandwidth chart height: " + this.bwChartHeight + NEWLINE);
        sb.append(INDENT + "Bandwidth chart width: " + this.bwChartWidth + NEWLINE);
        sb.append(INDENT + "Date Format: " + this.dateFormat + NEWLINE);
        sb.append(INDENT + "Response time chart weight: " + this.responseTimeWeight + NEWLINE);
        sb.append(INDENT + "Response time chart height: " + this.rtChartHeight + NEWLINE);
        sb.append(INDENT + "Response time chart width: " + this.rtChartWidth + NEWLINE);
        if (this.useThresholds) {
            sb.append(INDENT + "Using response time thresholds:" + NEWLINE);
            for (Float threshold : rtimeThresholds) {
                if (! threshold.equals(MAX_POSSIBLE_TIME)) {
                    sb.append(INDENT + INDENT + threshold + " seconds" + NEWLINE);
                }
            }
        } else {
            sb.append(INDENT + "Response time thresholds feature disabled." + NEWLINE);
        }
        sb.append(INDENT + "TPS chart weight: " + this.tpsWeight + NEWLINE);
        sb.append(INDENT + "TPS chart height: " + this.tpsChartHeight + NEWLINE);
        sb.append(INDENT + "TPS chart width: " + this.tpsChartWidth + NEWLINE);
        
        sb.append(INDENT + "Only show summary data: " + ! this.showTransactionData + NEWLINE);

        sb.append(INDENT + "Show tests passed: " + this.showTests + NEWLINE);
        sb.append(INDENT + "Show tests failed: " + this.showErrors + NEWLINE);
        sb.append(INDENT + "Show test failure rate: " + this.showErrorRate + NEWLINE);
        sb.append(INDENT + "Show mean time to resolve host: " + this.showMeanTime + NEWLINE);
        sb.append(INDENT + "Show test time standard deviation: " + this.showStandardDev + NEWLINE);
        sb.append(INDENT + "Show TPS: " + this.showTPS + NEWLINE);

        sb.append(INDENT + "Show response length: " + this.showResponseLength + NEWLINE);
        sb.append(INDENT + "Show bytes per second: " + this.showBytesPerSec + NEWLINE);
        sb.append(INDENT + "Show response errors: " + this.showResponseErrors + NEWLINE);
        sb.append(INDENT + "Show resolve host time: " + this.showResolveHost + NEWLINE);
        sb.append(INDENT + "Show establish connection time: " + this.showConnect + NEWLINE);
        sb.append(INDENT + "Show time to first byte: " + this.showFirstByte + NEWLINE);
        if (useNonDefautLocale) {
            sb.append(INDENT + "Use locale: custom" + NEWLINE);
            sb.append(INDENT + INDENT + "Language: '" + localeLanguage + "'" + NEWLINE);
            sb.append(INDENT + INDENT + "Country: '" + localeCountry + "'" + NEWLINE);
            sb.append(INDENT + INDENT + "Variant: '" + localeVariant + "'" + NEWLINE);
        }
        else {
            sb.append(INDENT + "Use locale: default" + NEWLINE);
        }
        if (this.useOSStats) {
            sb.append(INDENT + "Link to OS stats: " + this.OSStatsLink + NEWLINE);
        }
        else {
            sb.append(INDENT + "Link to OS stats: false" + NEWLINE);
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        String configFile = args.length > 0 ? args[0] : DEFAULT_CONFIG_FILE;
        Configuration config = new Configuration(configFile);
        System.out.println(config);
    }
}
