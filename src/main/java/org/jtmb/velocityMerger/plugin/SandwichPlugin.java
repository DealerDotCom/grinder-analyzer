package org.jtmb.velocityMerger.plugin;

import java.util.Properties;
import org.apache.log4j.Logger;

public class SandwichPlugin {

	private static final Logger logger = Logger.getLogger(SandwichPlugin.class);

	public SandwichPlugin(Properties p) {
		logger.debug("Sandwich plugin loaded");
	}

	public String getMeat() {
		return "pastrami";
	}
}
