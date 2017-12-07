import arcpydatetime, csv

class Session(object):
	def __init__(self, project_name,FCs,Fields):
		self.project_name = project_name
		self.FCs = FCs
		self.Fields = Fields
		self.Datasets = {}
		self.sessionStart = datetime.datetime.now()
		self.openLogs()
		print("Install Scrub session start: " + str(self.sessionStart))

	def openLogs(self):
		session_time = str(self.sessionStart).translate(None,":")
		self.changes = self.project_name + "_log_" + session_time + ".csv"
		self.note_log = self.project_name + "_notes_" + session_time + ".txt"
		self.change_file = open(self.changes,"wb")
		self.change_log = csv.writer(self.change_file,delimiter = ",") # to write to this later: logger.writerow(STUFF_TO_WRITE)
		self.change_log.writerow(["Tanko ID", "Attribute", "Previous Value", "New Value", "Time Comparison Made"])
		self.note_file = open(self.note_log,"w")# to write to this later: note_file.write(STUFF TO WRITE)
		self.note_file.write("Install Scrub session start: " + str(self.sessionStart))

		
	def add_Dataset(self):
		Dataset_ID = 0
		while Dataset_ID in self.Datasets.keys():
			Dataset_ID += 1
		self.Datasets[Dataset_ID] = Dataset(self.FCs[Dataset_ID],self.Fields[Dataset_ID],Dataset_ID, self.change_log, self.note_file)

	def removeDataset(self,ID):
		self.Datasets.pop(ID)	

	def closeLogs(self):
		self.change_file.close()
		self.note_file.close()

	def endSession(self):
		self.note_file.write("\nInstall Scrub session end: " + str(datetime.datetime.now()))
		self.closeLogs()
		print("Install Scrub session end: " + str(datetime.datetime.now()))			


class Dataset(object):
	def __init__(self, location, fields, ID, change_file, note_file):
		self.location = location
		self.fields = fields
		self.ID = ID
		self.records = {}
		self.logger = change_file
		self.note_file = note_file
	
	def populateRecords(self):
		with arcpy.da.SearchCursor(self.location, self.fields) as data:
			for point in data:
				ID = str(point[0])
				self.records[ID] = Fixture(ID,point[1],point[2],point[3],point[4],point[5],point[6],point[7],point[8],point[9],point[10],point[11],point[12],point[13],point[14],self.note_file)
		print("Records for dataset ID: " + str(self.ID) + " imported successfully.")

	def populateUpdates(self,other):
		for ID, OBJ in other.records.iteritems():
			self.records[ID].update(OBJ)
		print("Updates populated.")

	def writeData(self):
		with arcpy.da.UpdateCursor(self.location,self.fields) as update_Data:
			for update in update_Data:
				ID = str(update[0])
				#print(ID)
				if self.records[ID].updateFlag == "U" and self.records[ID].getINSSTAT() is not None:
					update[3] = self.records[ID].getOLDLAMP()
					update[4] = self.records[ID].getOLDWATT()
					update[5] = self.records[ID].getINSVOLTAGE()
					update[6] = self.records[ID].getINSFIXTURE()
					update[7] = self.records[ID].getINSCOMPLET()
					update[8] = self.records[ID].getINSPCSC()
					update[9] = self.records[ID].getINSISSUES()
					update[10] = self.records[ID].getINSCOMMENT()
					update[11] = self.records[ID].getINSSTAT()
					if self.records[ID].getINSNOTE() is not None and len(self.records[ID].getINSNOTE()) > 500:
						update[12] = self.records[ID].getINSNOTE()[0:500]
					else:
						update[12] = self.records[ID].getINSNOTE()
					update[13] = self.records[ID].getINSBY()
					update[14] = self.records[ID].getINSDATE()
					try:
						update_Data.updateRow(update)
					except:
						print("Bad values:", update)
				else:
					pass
			print("Data written to feature class.")

	#Compare each field to find changes between datasets
		#Log changed fields
		#	- CSV with datetime stamp
	def compareRecords(self,other):
		for ID, attr  in other.records.iteritems():
			if attr.compareATTRS(self.records[ID]):
				self.logger.writerow([attr.getTANKO_ID(),"No changed attributes", "No changed from value", "No changed to value",str(datetime.datetime.now())])
			else:
				changed_attrs = {}
				for attribute, value in attr.INST_ATTRIBUTES.iteritems():
					if value != self.records[ID].INST_ATTRIBUTES[attribute]:
						changed_attrs[attribute] = (self.records[ID].INST_ATTRIBUTES[attribute], value)
					else:
						pass
				comp_note = ""
				for changed_attr, change in changed_attrs.iteritems():
					if checkNull(change[0]) and not checkNull(change[1]):
						fromVal = None
						toVal = change[1].encode('utf-8')
					elif checkNull(change[1]) and not checkNull(change[0]):
						fromVal = change[1].encode('utf-8')
						toVal = None
					elif not checkNull(change[0]) and not checkNull(change[1]):
						fromVal = change[0].encode('utf-8')
						toVal = change[1].encode('utf-8')
					else:
						fromVal = None
						toVal = None
					self.logger.writerow([attr.getTANKO_ID().encode('utf-8'), changed_attr, fromVal, toVal, str(datetime.datetime.now())])
					comp_note += changed_attr  + ", "
				if self.records[ID].getINSDATE() is not None:
					self.records[ID].updateFlag = "P"
					if self.records[ID].getINSNOTE() is not None:
						prev_note = comp_note[0:-2] + " attribute(s) updated; " + self.records[ID].getINSNOTE()
						self.records[ID].createNote(prev_note)
						self.note_file.write("\nTanko ID: "+ attr.getTANKO_ID() +": " + prev_note)
				else:
					self.records[ID].updateFlag = "Y"


	#find issue for a whole dataset
	def findAllIssues(self):
		for ID, OBJ in self.records.iteritems():
			OBJ.findIssues()
		print("Issues found!")

class Fixture(object):
	def __init__(self,TANKO_ID,POLE_NUM,DESFIXT,OLDLAMP,OLDWATT,VOLTAGE,INSFIXTURE,INSCOMPLET,INSPCSC,INSISSUES,INSCOMMENT,INSSTAT,INSNOTE,INSBY,INSDATE,note_file):		
		self.TANKO_ID = self.cleanValue(TANKO_ID)
		self.POLE_NUM = self.cleanValue(POLE_NUM)
		self.DESFIXT = self.cleanValue(DESFIXT)
		self.INST_ATTRIBUTES = {"INSOLDLAMP":self.cleanValue(OLDLAMP),"INSOLDWATT":self.cleanValue(OLDWATT),"INSVOLTAGE":self.cleanValue(VOLTAGE),"INSFIXTURE":self.cleanValue(INSFIXTURE),"INSCOMPLET":self.cleanValue(INSCOMPLET),"INSPCSC":self.cleanValue(INSPCSC),"INSISSUES":self.cleanValue(INSISSUES),"INSCOMMENT":self.cleanValue(INSCOMMENT)}
		self.INSSTAT = self.cleanValue(INSSTAT)
		self.INSNOTE = self.cleanValue(INSNOTE)
		self.INSBY = self.cleanValue(INSBY)
		self.INSDATE = self.cleanValue(INSDATE)
		self.note_file = note_file
		#Defaults
		self.num_defaults = 0
		self.defaults = []

		#Tracking attributes
		self.updateFlag = 'N'
		self.updateDate = None

	#getters
	def getTANKO_ID(self):
		return self.TANKO_ID
	def getPOLE_NUM(self):
		return self.POLE_NUM
	def getDESFIXT(self):
		return self.DESFIXT
	def getOLDLAMP(self):
		return self.INST_ATTRIBUTES["INSOLDLAMP"]
	def getOLDWATT(self):
		return self.INST_ATTRIBUTES["INSOLDWATT"]
	def getINSVOLTAGE(self):
		return self.INST_ATTRIBUTES["INSVOLTAGE"]
	def getINSFIXTURE(self):
		return self.INST_ATTRIBUTES["INSFIXTURE"]
	def getINSCOMPLET(self):
		return self.INST_ATTRIBUTES["INSCOMPLET"]
	def getINSPCSC(self):
		return self.INST_ATTRIBUTES["INSPCSC"]
	def getINSISSUES(self):
		return self.INST_ATTRIBUTES["INSISSUES"]
	def getINSCOMMENT(self):
		return self.INST_ATTRIBUTES["INSCOMMENT"]
	def getINSSTAT(self):
		return self.INSSTAT
	def getINSNOTE(self):
		return self.INSNOTE
	def getINSBY(self):
		return self.INSBY
	def getINSDATE(self):
		return self.INSDATE	
	
	#setters
	def setOLDLAMP(self, input_var):
		self.INST_ATTRIBUTES["INSOLDLAMP"] = input_var
	def setOLDWATT(self, input_var):
		self.INST_ATTRIBUTES["INSOLDWATT"] = input_var		
	def setINSVOLTAGE(self, input_var):
		self.INST_ATTRIBUTES["INSVOLTAGE"] = input_var
	def setINSFIXTURE(self, input_var):
		self.INST_ATTRIBUTES["INSFIXTURE"] = input_var		
	def setINSCOMPLET(self, input_var):
		self.INST_ATTRIBUTES["INSCOMPLET"] = input_var		
	def setINSPCSC(self, input_var):
		self.INST_ATTRIBUTES["INSPCSC"] = input_var		
	def setINSISSUES(self, input_var):
		self.INST_ATTRIBUTES["INSISSUES"] = input_var		
	def setINSCOMMENT(self, input_var):
		self.INST_ATTRIBUTES["INSCOMMENT"] = input_var
	def setINSSTAT(self, input_var):
		self.INSSTAT = input_var	
	def setINSNOTE(self, input_var):
		self.INSNOTE = input_var
	def setINSBY(self, input_var):
		self.INSBY = input_var
	def setINSDATE(self, input_var):
		self.INSDATE = input_var

	def cleanValue(self,value):
		if value and value != " ":
			return value
		else:
			return None

	#analysis	
	def compareATTRS(self, other):
		#compares attributes between this record and another
		if self.INST_ATTRIBUTES == other.INST_ATTRIBUTES:
			return True
		else:
			return False

	def calc_defaults(self):
		#counts the number of default attributes and creates a list
		defaults = {"INSOLDLAMP":"Choose...","INSOLDWATT":"Choose...","INSVOLTAGE":"Choose...","INSFIXTURE":"Choose...","INSCOMPLET":"Not Yet Installed","INSPCSC":"Choose...","INSISSUES":"None","INSCOMMENT":None}
		for field, value in self.INST_ATTRIBUTES.iteritems():
			if value == defaults[field] or value is None:
				self.num_defaults += 1
				self.defaults.append(field)
			else:
				continue

	def analyze_Defaults(self):	
		# Check for accidentally edited points or incomplete records - If INSCOMPLET = "Not Yet Installed"
		self.calc_defaults()
		if self.num_defaults == 8: #check if all install attributes are default
			#if all attributes are default, flag the record not to be updated.
			self.updateFlag = 'N'
		# Check for skips.
		elif "Skipped" in self.getINSCOMPLET():
			# - Update INSSTAT to "SKIPPED"
			self.setINSSTAT("SKIPPED")
			# - Log note: "RCID: <RCID VALUE>: <INSCOMPLET VALUE> - Installer commented, '<INSCOMMENT VALUE>'"
			skip_note = self.getINSCOMPLET()
			#check if there are issues and add it to the skip note
			if self.getINSISSUES() != 'None' and self.getINSISSUES() is not None:
				skip_note += ' - '+ self.getINSISSUES()
			#If there are no issues the skip note only needs to be the inscomplet value
			else:
				pass
			self.createNote(skip_note)
		#check for incomplete surveys after skips
		elif self.num_defaults > 0:
			insnote = "Incomplete Survey:"
			OKDefaults = ['INSOLDLAMP','INSOLDWATT','INSVOLTAGE','INSFIXTURE','INSCOMPLET','INSPCSC']
			Incomplete = False
			for field in OKDefaults:
				if field in self.defaults:
					Incomplete = True
					insnote += ' ' + field + ','
				else:
					continue
			#finish and push a note to data if the field is incomplete, update INSSTAT
			if Incomplete == True:
				insnote = insnote[0:-1] +' not filled out.'
				self.createNote(insnote)
				self.setINSSTAT("DATA ISSUE")
			else:
				pass
		else:
			#all fields are filled out, do nothing
			pass

	def analyze_Issues(self):	
		#Check for issues
		if self.getINSISSUES() != 'None' and self.getINSISSUES() is not None:
			#flag the issue in insstat
			if self.getINSSTAT() is None:
				self.setINSSTAT("FIELD ISSUE")
			else: 
				self.setINSSTAT(self.getINSSTAT() + "; FIELD ISSUE")
			#create a note for the issue
			issue_note = self.getINSISSUES()
	 		self.createNote(issue_note)

	def analyze_InstalledFixture(self):			
		# Check to see if the installed fixture meets the design
			# if DESFIXT != INSFIXTURE
		if (self.getDESFIXT() != self.getINSFIXTURE()) and (self.getINSFIXTURE() != 'Choose...' and self.getINSFIXTURE() is not None):
			# Update INSSTAT to "DATA ISSUE"
			if self.getINSSTAT() is None:
				self.setINSSTAT("DATA ISSUE")
			else: 
				self.setINSSTAT(self.getINSSTAT() + "; DATA ISSUE")
			# log note: "RCID <RCID VALUE>: Design calls for <DESFIXT> to be installed; installer indicated <INSFIXTURE> was installed."
			disc_note = 'Design calls for ' + self.getDESFIXT() + ' to be installed; installer indicated ' + self.getINSFIXTURE() + ' was installed.'
			self.createNote(disc_note)

	def analyze_Voltage(self):
		# Check to see if a fixture is high VOLTAGE:
			# if INSVOLTAGE > 120
		try:
			if self.getINSVOLTAGE() and self.getINSVOLTAGE() != 'Choose...': #check for empty strings and default answer. will eval to False if the string is empty
				volts = int(self.getINSVOLTAGE())
				if  volts > 120:
					# Update INSSTAT to "DATA ISSUE"
					if self.getINSSTAT() is None:
						self.setINSSTAT("FIELD ISSUE")
					else: 
						self.setINSSTAT(self.getINSSTAT() + "; FIELD ISSUE")
					# log note: "RCID <RCID VALUE>: Installer indicated fixture has voltage of <INSVOLTAGE VALUE>. Verify whether or not this is a high voltage fixture."
					hv_note = 'Installer indicated fixture has voltage of ' + self.getINSVOLTAGE() + '. Verify whether or not this is a high voltage fixture.'
					self.createNote(hv_note)
					# Check for comments not related to issues or skips:	
			else:
				return None
		except ValueError:
			return None

	
	def analyze_commentsOnly(self):
		if self.getINSCOMMENT() is not None and self.getINSCOMMENT() != "" :
			# UPDATE INSSTAT to "REVIEW"
			if self.getINSSTAT() is None:
				self.setINSSTAT("REVIEW")
				#Note the comment
			try:
				comment_note = 'Installer commented, "' + self.getINSCOMMENT() + '."'
			except:
				print("the comment:", self.getINSCOMMENT(), "will not print")	
			self.createNote(comment_note)
		elif (self.getINSSTAT() is not None and self.getINSSTAT() != 'DATA ISSUE') and self.getINSCOMMENT() is None: #####################################
			comment_note = "No installer comment."
			self.createNote(comment_note)
		else:
			pass

	def analyze_remainingRecords(self):	
		#if insstat is none and inscomplet  DNE not yet installed
		if self.getINSSTAT() is None and self.getINSCOMPLET() != 'Not Yet Installed':
			self.setINSSTAT('COMPLETE')
		if self.getINSNOTE() is not None:
			Note = "Tanko ID " + self.getTANKO_ID() +': ' + self.getINSNOTE()
			self.write_log_note(Note)

	#assemble notes
	def createNote(self, NOTE):
		NOTE = NOTE.encode('utf-8')
		if self.getINSNOTE() is None:
			self.setINSNOTE(NOTE)
		else:
			self.setINSNOTE(self.getINSNOTE() + '; ' + NOTE)

	def write_log_note(self,note):
		self.note_file.write("\n" + note)

	#Find issue for individual record
	def findIssues(self):
		#run each of the analysis functions
		self.analyze_Defaults()
		self.analyze_Issues()
		self.analyze_InstalledFixture()
		self.analyze_Voltage()
		self.analyze_commentsOnly()
		self.analyze_remainingRecords()

	def update(self,other):
		if self.updateFlag == 'Y':
			self.INST_ATTRIBUTES = other.INST_ATTRIBUTES
			self.setINSSTAT(other.getINSSTAT()) 
			self.setINSNOTE(other.getINSNOTE())
			self.setINSBY(other.getINSBY())
			self.setINSDATE(other.getINSDATE())
			self.updateDate = datetime.datetime.now()
			self.updateFlag = 'U'
			self.note_file.write("\n Tanko ID " + self.getTANKO_ID() + " updated at " + str(self.updateDate))
		elif self.updateFlag == 'P':
			self.INST_ATTRIBUTES = other.INST_ATTRIBUTES
			self.setINSSTAT(other.getINSSTAT()) 
			if self.getINSNOTE() is not None and other.getINSNOTE() is not None:
				self.setINSNOTE(other.getINSNOTE() + '; ' + self.getINSNOTE())
			else:
				self.setINSNOTE(other.getINSNOTE())
			self.updateDate = datetime.datetime.now()
			self.updateFlag = 'U'
			self.note_file.write("\n Tanko ID " + self.getTANKO_ID() + " updated at " + str(self.updateDate))
		else:
			pass		
def checkNull(value):
	if value is None:
		return True
	else:
		return False