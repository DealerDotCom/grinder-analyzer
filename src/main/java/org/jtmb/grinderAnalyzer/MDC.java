package org.jtmb.grinderAnalyzer;

import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

/**
 * Helper MDC used to pass data between Java and Python.
 */
public class MDC {
	
	private static Map<String,Object> context = new ConcurrentHashMap<String,Object>();
	
	/**
	 * Puts a value into the MDC.
	 * @param key The key of the value.
	 * @param value The value to be put into the MDC.
	 */
	public static synchronized void put(final String key, final Object value) {
		context.put(key, value);
	}
	
	/**
	 * Retrieves a value denoted by the provided key from the MDC.
	 * @param The key of the value to be retrieved.
	 * @return The associated value or {@code null} if the mapping does not exist.
	 */
	public static synchronized Object get(final String key) {
		return context.get(key);
	}
}