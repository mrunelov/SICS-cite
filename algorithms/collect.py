AAN_dir = '../AAN/'
burstfile = AAN_dir + 'data/Burst-detection-analysis-AAN.csv'


def create_csv_all_AAN():
	# burst file headers:
	# Word,Level,Weight,Length,Start,End (word is title.strip().replace(",",""))
	with open("all_AAN.csv", "w+") as csv: