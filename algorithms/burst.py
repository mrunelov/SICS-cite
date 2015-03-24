import pybursts

def burst(offsets, s=2, gamma=0.1):
	"""
	http://www.cs.cornell.edu/home/kleinber/bhs.pdf
	offsets: a list of time offsets (numeric)
	s: the base of the exponential distribution that is used for modeling the event frequencies
	gamma: coefficient for the transition costs between states

	Details:
	The model is a hidden Markov process in which, after each event, 
	the state of the system proba-blistically determines how much time will pass until the next event occurs.  
	While the system isin state i, the gaps between events are assumed to be drawn from an exponential distribution 
	with expected value proportional to s ** -i.  The value of s may be modified; 
	higher values increase the strictness of the algorithm’s criterion for how dramatic an increase of activity has to be
	to beconsidered a ‘burst’. 

	The cost of a state change is proportional to the increase in state number; 
	this proportion can be modified by setting the parameter gamma. Higher values mean roughly that bursts must be sustained
	over longer periods of time in order for the algorithm to recognize them. Note that the algorithm will not work if there are
	two events that occur at the same time.
	"""
	print pybursts.kleinberg(offsets, s=s, gamma=gamma)

def normalize_offsets(offsets):
	min_value = min(offsets)
	return [x - min_value for x in offsets]


offsets = [4, 17, 23, 27, 33, 35, 37, 76, 77, 82, 84, 88, 90, 92]
offsets = normalize_offsets(offsets)
print offsets
burst(offsets)

