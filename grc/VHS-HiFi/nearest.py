# this module will be imported in the into your flowgraph

from math import log

def power(value, base):
	n = round(log(value,base))
	return pow(base,n)	

	
