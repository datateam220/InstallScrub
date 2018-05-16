import arcpy, datetime, csv
def to_utf8(lst):
    return [unicode(elem).encode('utf-8') for elem in lst]

class Session(object):
	def __init__(self, project_name,FCs,Fields, voltage_threshold = 120):
		self.project_name = project_name
		self.FCs = FCs
		self.Fields = Fields
		self.voltage_threshold = voltage_threshold
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
		self.Datasets[Dataset_ID] = Dataset(self.FCs[Dataset_ID],self.Fields[Dataset_ID],Dataset_ID, self.change_log, self.note_file, self.voltage_threshold)

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
	def __init__(self, location, fields, ID, change_file, note_file, voltage_threshold = 120):
		self.location = location
		self.fields = fields
		self.ID = ID
		self.records = {}
		self.logger = change_file
		self.note_file = note_file
		self.voltage_threshold = voltage_threshold
	
	def populateRecords(self):
		with arcpy.da.SearchCursor(self.location, self.fields) as data:
			for point in data:
				ID = point[0]
				self.records[ID] = Fixture(ID,point[1],point[2],point[3],point[4],point[5],point[6],point[7],point[8],point[9],point[10],point[11],point[12],point[13],point[14],self.note_file, self.voltage_threshold)
		print("Records for dataset ID: " + str(self.ID) + " imported successfully.")

	def populateUpdates(self,other):
		for ID, OBJ in other.records.iteritems():
			self.records[ID].update(OBJ)
		print("Updates populated.")

	def writeData(self):
		with arcpy.da.UpdateCursor(self.location,self.fields) as update_Data:
			for update in update_Data:
				ID = update[0]
				#print(ID)
				if self.records[ID].updateFlag == "U" and self.records[ID].INSSTAT is not None:
					update[3] = self.records[ID].OLDLAMP
					update[4] = self.records[ID].OLDWATT
					update[5] = self.records[ID].INSVOLTAGE
					update[6] = self.records[ID].INSFIXTURE
					update[7] = self.records[ID].INSCOMPLET
					update[8] = self.records[ID].INSPCSC
					update[9] = self.records[ID].INSISSUES
					update[10] = self.records[ID].INSCOMMENT
					update[11] = self.records[ID].INSSTAT
					if self.records[ID].INSNOTE is not None and len(self.records[ID].INSNOTE) > 500:
						update[12] = self.records[ID].INSNOTE[0:500]
					else:
						update[12] = self.records[ID].INSNOTE
					update[13] = self.records[ID].INSBY
					update[14] = self.records[ID].INSDATE
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
				self.logger.writerow([attr.TANKO_ID,"No changed attributes", "No changed from value", "No changed to value",str(datetime.datetime.now())])
			else:
				changed_attrs = {}
				for attribute, value in attr.INST_ATTRIBUTES.iteritems():
					if value != self.records[ID].INST_ATTRIBUTES[attribute]:
						changed_attrs[attribute] = (self.records[ID].INST_ATTRIBUTES[attribute], value)
					else:
						pass
				comp_note = ""
				for changed_attr, change in changed_attrs.iteritems():
					fromVal = change[0]
					toVal = change[1]
					row = [attr.TANKO_ID, changed_attr, fromVal, toVal, str(datetime.datetime.now())]
					self.logger.writerow(to_utf8(row))
					comp_note += changed_attr  + ", "
				if self.records[ID].INSDATE is not None:
					self.records[ID].updateFlag = "P"
					if self.records[ID].INSNOTE is not None:
						prev_note = comp_note[0:-2] + " attribute(s) updated; " + self.records[ID].INSNOTE
						self.records[ID].createNote(prev_note)
						self.note_file.write('\nTanko ID: {0}: {1}'.format(attr.TANKO_ID,prev_note.encode('utf-8'))) 
				else:
					self.records[ID].updateFlag = "Y"


	#find issue for a whole dataset
	def findAllIssues(self):
		for ID, OBJ in self.records.iteritems():
			OBJ.findIssues()
		print("Issues found!")

class Fixture(object):
	def __init__(self,TANKO_ID,POLE_NUM,DESFIXT,OLDLAMP,OLDWATT,VOLTAGE,INSFIXTURE,INSCOMPLET,INSPCSC,INSISSUES,INSCOMMENT,INSSTAT,INSNOTE,INSBY,INSDATE,note_file, voltage_threshold = 120):		
		self.init_hidden_values()
		self.TANKO_ID = TANKO_ID
		self.POLE_NUM = POLE_NUM
		self.DESFIXT = DESFIXT
		self.INST_ATTRIBUTES = {"INSOLDLAMP":OLDLAMP,"INSOLDWATT":OLDWATT,"INSVOLTAGE":VOLTAGE,"INSFIXTURE":INSFIXTURE,"INSCOMPLET":INSCOMPLET,"INSPCSC":INSPCSC,"INSISSUES":INSISSUES,"INSCOMMENT":INSCOMMENT}
		self.INSSTAT = INSSTAT
		self.INSNOTE = INSNOTE
		self.INSBY = INSBY
		self.INSDATE = INSDATE
		self.note_file = note_file
		self.voltage_threshold = voltage_threshold
		#Defaults
		self.num_defaults = 0
		self.defaults = []

		#Tracking attributes
		self.updateFlag = 'N'
		self.updateDate = None

		

	@property
	def TANKO_ID(self):
		return self.__TANKO_ID
	@TANKO_ID.setter
	def TANKO_ID(self,val):
		self.__TANKO_ID = str(self.cleanValue(val))

	@property
	def POLE_NUM(self):
		return self.__POLE_NUM
	@POLE_NUM.setter
	def POLE_NUM(self,val):
		self.__POLE_NUM = self.cleanValue(val)

	@property
	def DESFIXT(self):
		return self.__DESFIXT
	@DESFIXT.setter
	def DESFIXT(self,val):
		self.__DESFIXT = self.cleanValue(val)	

	# Property for the whole install attributes dict. individual attributes will follow.
	@property 
	def INST_ATTRIBUTES(self):
		return self.__INST_ATTRIBUTES
	@INST_ATTRIBUTES.setter
	def INST_ATTRIBUTES(self,val_dict):
		try:
			for k,v in val_dict.iteritems():
				self.__INST_ATTRIBUTES[k] = self.cleanValue(v)
		except Exception as e:
			print(e)
			#raise TypeError('Attributes dictionary not properly initialized in Fixture object definition.')

	@property
	def OLDLAMP(self):
		return self.__INST_ATTRIBUTES['INSOLDLAMP']
	@OLDLAMP.setter
	def OLDLAMP(self, val):
		self.__INST_ATTRIBUTES['INSOLDLAMP'] = self.cleanValue(val)

	@property
	def OLDWATT(self):
		return self.__INST_ATTRIBUTES['INSOLDWATT']
	@OLDWATT.setter
	def OLDWATT(self, val):
		self.__INST_ATTRIBUTES['INSOLDWATT'] = self.cleanValue(val)

	@property
	def INSVOLTAGE(self):
		return self.__INST_ATTRIBUTES['INSVOLTAGE']
	@INSVOLTAGE.setter
	def INSVOLTAGE(self, val):
		self.__INST_ATTRIBUTES['INSVOLTAGE'] = self.cleanValue(val)

	@property
	def INSFIXTURE(self):
		return self.__INST_ATTRIBUTES['INSFIXTURE']
	@INSFIXTURE.setter
	def INSFIXTURE(self, val):
		self.__INST_ATTRIBUTES['INSFIXTURE'] = self.cleanValue(val)

	@property
	def INSCOMPLET(self):
		return self.__INST_ATTRIBUTES['INSCOMPLET']
	@INSCOMPLET.setter
	def INSCOMPLET(self, val):
		self.__INST_ATTRIBUTES['INSCOMPLET'] = self.cleanValue(val)

	@property
	def INSPCSC(self):
		return self.__INST_ATTRIBUTES['INSPCSC']
	@INSPCSC.setter
	def INSPCSC(self, val):
		self.__INST_ATTRIBUTES['INSPCSC'] = self.cleanValue(val)

	@property
	def INSISSUES(self):
		return self.__INST_ATTRIBUTES['INSISSUES']
	@INSISSUES.setter
	def INSISSUES(self, val):
		self.__INST_ATTRIBUTES['INSISSUES'] = self.cleanValue(val)

	@property
	def INSCOMMENT(self):
		return self.__INST_ATTRIBUTES['INSCOMMENT']
	@INSCOMMENT.setter
	def INSCOMMENT(self, val):
		self.__INST_ATTRIBUTES['INSCOMMENT'] = self.cleanValue(val)

	@property
	def INSSTAT(self):
		return self.__INSSTAT
	@INSSTAT.setter
	def INSSTAT(self,val):
		self.__INSSTAT = self.cleanValue(val)
		
	@property
	def INSNOTE(self):
		return self.__INSNOTE
	@INSNOTE.setter
	def INSNOTE(self,val):
		self.__INSNOTE = self.cleanValue(val)

	@property
	def INSBY(self):
		return self.__INSBY
	@INSBY.setter
	def INSBY(self,val):
		self.__INSBY = self.cleanValue(val)

	@property
	def INSDATE(self):
		return self.__INSDATE
	@INSDATE.setter
	def INSDATE(self,val):
		self.__INSDATE = self.cleanValue(val)	

	def cleanValue(self,value):
		"""
		This method takes an input value from a field in a dataset and checks if it is NULL, blank (i.e.
		edited but given no value), an integer, or a string. 
		 - If the value is blank or NULL, the function returns None so that it is obvious the field 
		   has been edited (it should otherwise still be populated with the default value). This 
		   scenario should not be possible for any field other than INSCOMMENT given that the standard 
		   set up removes nullability of fields.
		 - If the value is an integer, this method will convert the value to a UTF-8 encoded string.
		 - In standard cases, this method returns the value as a UTF-8 encoded string.
		"""
		if value is not None and value != " ":
			if type(value) not in [int,datetime.datetime,unicode]:
				return value.encode('utf-8')[0:500]
#			elif type(value) == unicode:
#				return value.decode('ascii').encode('utf-8')
			else:
				return value
		else:
			return None

	def init_hidden_values(self):
		self.__INST_ATTRIBUTES = {"INSOLDLAMP":'',"INSOLDWATT":'',"INSVOLTAGE":'',"INSFIXTURE":'',"INSCOMPLET":'',"INSPCSC":'',"INSISSUES":'',"INSCOMMENT":''}
		self.__TANKO_ID = None 
		self.__POLE_NUM = None 
		self.__DESFIXT = None 
		self.__INSSTAT = None 
		self.__INSNOTE = None 
		self.__INSBY = None 
		self.__INSDATE = None 
	#analysis	
	def compareATTRS(self, other):
		#compares attributes between this record and another
		if self.INST_ATTRIBUTES == other.INST_ATTRIBUTES:
			#print('True')
			return True
		else:
			#print('False')
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
		elif "Skipped" in self.INSCOMPLET:
			# - Update INSSTAT to "SKIPPED"
			self.INSSTAT = "SKIPPED"
			# - Log note: "RCID: <RCID VALUE>: <INSCOMPLET VALUE> - Installer commented, '<INSCOMMENT VALUE>'"
			skip_note = self.INSCOMPLET
			#check if there are issues and add it to the skip note
			if self.INSISSUES != 'None' and self.INSISSUES is not None:
				skip_note += ' - '+ self.INSISSUES
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
				self.INSSTAT = "INCOMPLETE"
			else:
				pass
		else:
			#all fields are filled out, do nothing
			pass

	def analyze_Issues(self):	
		#Check for issues
		if self.INSISSUES != 'None' and self.INSISSUES is not None:
			#flag the issue in insstat
			if self.INSSTAT is None:
				self.INSSTAT = "FIELD ISSUE"
			else: 
				self.INSSTAT = self.INSSTAT + "; FIELD ISSUE"
			#create a note for the issue
			issue_note = self.INSISSUES
	 		self.createNote(issue_note)

	def analyze_InstalledFixture(self):			
		# Check to see if the installed fixture meets the design
			# if DESFIXT != INSFIXTURE
		#03052018: It may be better to validate this via part number, i.e., PART_NUM in INSFIXTURE in order to avoid situations where DESFIXT is only slightly different than INSFIXTURE, i.e. Type A vs Type A
		#		   Alternatively, validation can take place when creating the domains.
		if (self.DESFIXT != self.INSFIXTURE) and (self.INSFIXTURE != 'Choose...' and self.INSFIXTURE is not None):
			# Update INSSTAT to "DATA ISSUE"
			if self.INSSTAT is None:
				self.INSSTAT = "DATA ISSUE"
			else: 
				self.INSSTAT = self.INSSTAT + "; DATA ISSUE"
			# log note: "RCID <RCID VALUE>: Design calls for <DESFIXT> to be installed; installer indicated <INSFIXTURE> was installed."
			disc_note = 'Design calls for ' + self.DESFIXT + ' to be installed; installer indicated ' + self.INSFIXTURE + ' was installed.'
			self.createNote(disc_note)

	def analyze_Voltage(self):
		# Check to see if a fixture is high VOLTAGE:
			# if INSVOLTAGE > 120
		try:
			if self.INSVOLTAGE and self.INSVOLTAGE != 'Choose...' and self.INSVOLTAGE != 'Less than 120': #check for empty strings and default answer. will eval to False if the string is empty
				volts = int(self.INSVOLTAGE)
				if  volts > self.voltage_threshold:
					# Update INSSTAT to "DATA ISSUE"
					if self.INSSTAT is None:
						self.INSSTAT = "FIELD ISSUE"
					else: 
						self.INSSTAT = self.INSSTAT + "; FIELD ISSUE"
					# log note: "RCID <RCID VALUE>: Installer indicated fixture has voltage of <INSVOLTAGE VALUE>. Verify whether or not this is a high voltage fixture."
					hv_note = 'Installer indicated fixture has voltage of ' + self.INSVOLTAGE + '. Verify whether or not this is a high voltage fixture.'
					self.createNote(hv_note)
					# Check for comments not related to issues or skips:	
			elif self.INSVOLTAGE == 'Less than 120': 
				if self.INSSTAT is None:
					self.INSSTAT = "FIELD ISSUE"
				else: 
					self.INSSTAT = self.INSSTAT + "; FIELD ISSUE"
				lv_note = 'Installer indicated fixture has a voltage of <120V. Verify whether or not this fixture has power'
				self.createNote(lv_note)
			else:
				return None
		except ValueError:
			return None

	
	def analyze_commentsOnly(self):
		if self.INSCOMMENT is not None and self.INSCOMMENT != "" :
			# UPDATE INSSTAT to "REVIEW"
			if self.INSSTAT is None:
				self.INSSTAT = "REVIEW"
				#Note the comment
			try:
				comment_note = 'Installer commented, "' + self.INSCOMMENT + '."'
			except:
				print("the comment:", self.INSCOMMENT, "will not print")	
			self.createNote(comment_note)
		elif (self.INSSTAT is not None and self.INSSTAT != 'DATA ISSUE') and self.INSCOMMENT is None: #####################################
			comment_note = "No installer comment."
			self.createNote(comment_note)
		else:
			pass

	def analyze_remainingRecords(self):	
		#if insstat is none and inscomplet  DNE not yet installed
		if self.INSSTAT is None and self.INSCOMPLET != 'Not Yet Installed':
			self.INSSTAT = 'COMPLETE'
		if self.INSNOTE is not None:
			Note = "Tanko ID " + self.TANKO_ID +': ' + self.INSNOTE
			self.write_log_note(Note)

	#assemble notes
	def createNote(self, NOTE):
		if self.INSNOTE is None:
			self.INSNOTE = NOTE
		else:
			self.INSNOTE = self.INSNOTE + '; ' + NOTE

	def write_log_note(self,note):
		note = note.encode('utf-8')
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
			self.INSSTAT = other.INSSTAT 
			if self.INSNOTE is not None:# and other.INSNOTE is not None:
				if other.INSNOTE is not None:
					self.INSNOTE = other.INSNOTE + '; ' + self.INSNOTE
				else:
					pass # do not change the note
			else:
				self.INSNOTE =  other.INSNOTE
			self.INSBY = other.INSBY
			self.INSDATE = other.INSDATE
			self.updateDate = datetime.datetime.now()
			self.updateFlag = 'U'
			self.note_file.write("\n Tanko ID " + self.TANKO_ID + " updated at " + str(self.updateDate))
		elif self.updateFlag == 'P':
			self.INST_ATTRIBUTES = other.INST_ATTRIBUTES
			self.INSSTAT = other.INSSTAT 
			if self.INSNOTE is not None:# and other.INSNOTE is not None:
				if other.INSNOTE is not None:
					self.INSNOTE = other.INSNOTE + '; ' + self.INSNOTE
				else:
					pass # do not change the note
			else:
				self.INSNOTE =  other.INSNOTE
			self.updateDate = datetime.datetime.now()
			self.updateFlag = 'U'
			self.note_file.write("\n Tanko ID " + self.TANKO_ID + " updated at " + str(self.updateDate))
		else:
			pass	# do nothing, in the future there may be other updateFlags.


