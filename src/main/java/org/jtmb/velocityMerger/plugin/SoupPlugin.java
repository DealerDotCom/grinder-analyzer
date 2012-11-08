package org.jtmb.velocityMerger.plugin;

import java.util.Properties;
import org.apache.log4j.*;

public class SoupPlugin {
	
	private static final Logger logger = Logger.getLogger(SoupPlugin.class);

	public SoupPlugin(Properties p) {
		logger.debug("Soup plugin loaded");
	}

	public int getTemperature() {
		return 85;
	}
}
