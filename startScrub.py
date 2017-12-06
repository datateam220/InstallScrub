import InstallScrub

#Project Name
project_name = "PROJECT_NAME"

#Feature Classes
Master_FC = r'T:\BSD\1_ Municipal Projects\MUNICIPALITY\GIS\DATA\PROJECT_GDB\FEATURE_DATASET\FEATURE_CLASS'
Collector_FC = r'T:\BSD\1_ Municipal Projects\MUNICIPALITY\GIS\DATA\PROJECT_GDB\FEATURE_TABLE'

#Voltage Threshold
voltage_threshold = 120


#############DO NOT EDIT BELOW THIS POINT##############

# VAR NAME| ID Field |    Pole Number   |des. fixt|Old Lamp Typ| OldWattage |  Voltage   |  New Fixt. | Ins.Status |  NewPC  |   Issues  |  Comments  |  AStat  | ANotes  |  INS  | IDate  #
Master_Fields = ['TANKO_ID','POLENUM','DESFIXT','INSOLDLAMP','INSOLDWATT','INSVOLTAGE','INSFIXTURE','INSCOMPLET','INSPCSC','INSISSUES','INSCOMMENT','INSSTAT','INSNOTE','INSBY','INSDATE']
Collector_Fields = ['TANKO_ID','POLENUM','DESFIXT','INSOLDLAMP','INSOLDWATT','INSVOLTAGE','INSFIXTURE','INSCOMPLET','INSPCSC','INSISSUES','INSCOMMENT','INSSTAT','INSNOTE','Editor','EditDate']
FCs = [Master_FC, Collector_FC]
Fields = [Master_Fields,Collector_Fields]

#Run Standard Scrub
SESSION = InstallScrub.Session(project_name,FCs,Fields, voltage_threshold)
SESSION.openLogs()
for i in FCs:
	SESSION.add_Dataset()
for ID, Dataset in SESSION.Datasets.iteritems():
	Dataset.populateRecords()
SESSION.Datasets[0].compareRecords(SESSION.Datasets[1])
SESSION.Datasets[1].findAllIssues()
SESSION.Datasets[0].populateUpdates(SESSION.Datasets[1])
SESSION.Datasets[0].writeData()
SESSION.endSession()