
This directory contains two tools for moving Grinder data into Graphite.

 * glf	        : Like GrinderAnalyzer, glf (Graphite Log Feeder)
                  parses logs from completed Grinder runs.  The
                  data is then sent to Graphite for visualization.
                  This is a well-tested tool suitable for general use.
                  
                  In the future glf and GrinderAnalyzer are expected
                  to merge into a single tool.

                  The glf project web site:
                     https://bitbucket.org/travis_bear/graphitelogfeeder
 

 * logster	: Realtime forwarding of Grinder data to Graphite.
                  Allows you to visualize data from a running Grinder
                  test.

                  Contains a sample Grinder Logster parser that you
                  can add to your logster installation.  This is an
                  example implementation only, not a general-purpose
                  solution.  It will require modification to be 
                  suitable for your specific application.

                  Logster:
                     https://github.com/etsy/logster
		  


