from math import log

def power(base, value):
	n = round(log(value, base))
	return pow(base,n)	

