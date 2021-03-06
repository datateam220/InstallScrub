########                                         READ ME                                           ########
#### - Enter your feature class as described in the comments below.                                    ####
#### - The list of fields to add includes all standard install fields. 								   #### 
#### - If you require additional fields add them to the list. 										   ####
#### - This script will work for any TEXT field that you want to add. 								   ####
#### - When executing this script within ArcMap, CLOSE YOUR ATTRIBUTE TABLE: Otherwise ARC WILL CRASH! ####
#### - This script will run more quickly from the command prompt than from within ArcMap.              ####
#### - The only thing you need to change is the feature class variable: "fc" and the fields to add if  ####
####   you are not using the defaults                                                                  ####
#### - To execute from command prompt:																   ####
####        1. Hit Windows + R, type "cmd" without quotes and hit Enter/Return 						   ####
####        2. In the command prompt type, without quotes: "cd C:/Python27/ArcGIS10.5" and hit Enter.  ####
####        3. In the command prompt type, without quotes: "python"                                    ####
####        4. Your python environment should now be open. Now open a Windows Explorer window and      ####
####           navigate to where this is saved. Make a copy and paste it in a folder of your choice.   ####
####        5. Modify this file as necessary, save it, and copy the file path.                         ####
####        6. Return to your open python environment in the command prompt.                           ####
####        7. Type in, without double-quotes: "path = r'[PATH YOU COPIED]\add_install_fields.py' "    ####
####            Make sure the single-quote at the end is retained. Pres Enter.                         ####
####        8. Type in, without double-quotes: "execfile(path)" and hit Enter.                         ####
####        9. ...                                                                                     ####
####        10. Profit!                                                                                ####
#### - To execute this file from the ArcMap Python window, make modifications below, copy, and paste   ####
####   the code into the Python window. Hit Enter twice to execute.


#import arcpy package
import arcpy
#declare the feature class. You can use a raw string (r'path\goes\to\here') or regular string ('Path/goes/to/here')
#If using a raw string for the path name, ensure that an "r" is typed in front of the string and that the path delimiters are back slashes \
# like so: r'T:\BSD\1_ Municipal Projects\Rancho Cucamonga, CA\GIS\DATA\RanchoCucamonga.gdb\Utility\RC_UCSYN_PHASE_1' 

#If using a regular string for the path name, use forward slashes as path delimiters /
#like so: 'T:/BSD/1_ Municipal Projects/Rancho Cucamonga, CA/GIS/DATA/RanchoCucamonga.gdb/Utility/RC_UCSYN_PHASE_1'

fc = r'T:\BSD\1_ Municipal Projects\PATH\TO\FeatureCLass'

#fields within the feature class gathered by arcpy, AUTOGENERATED
Fields = [field.name for field in arcpy.ListFields(fc)]

#list of fields to add. If your project requires a non-standard install field set, add it to this list.
fields_to_add = ['INSOLDLAMP','INSOLDWATT','INSVOLTAGE','INSFIXTURE','INSCOMPLET','INSPCSC','INSISSUES','INSCOMMENT','INSSTAT','INSNOTE','INSBY','INSDATE','INSREPNUM','INVOICENUM']
#Parameter for populating default values. Default is True; set to False to avoid autopopulating default values.
pop_defaults = True


#iterate through the fields_to_add and add them one by one. 
for f in fields_to_add:
	try:
		if not f in Fields:
			print("Adding: " + f)
			if f in ['INSREPNUM', 'INVOICENUM']:
				arcpy.AddField_management(fc, f, 'SHORT')
			else:	
				arcpy.AddField_management(fc, f, 'TEXT',field_length = 500)
			print(f + " added." )
		else:
			print(f + " is already a field in the feature class.")
	except:
		print("An error occurred when adding " + f + " to the feature class.")
print("Done adding fields.")

#set field values to defaults
if pop_defaults:
	print("Populating default values.")
	defaults = {"INSOLDLAMP":"Choose...","INSOLDWATT":"Choose...","INSVOLTAGE":"Choose...","INSFIXTURE":"Choose...","INSCOMPLET":"Not Yet Installed","INSPCSC":"Choose...","INSISSUES":"None",'INSCOMMENT' : None,'INSSTAT' : None,'INSNOTE' : None,'INSBY' : None,'INSDATE' : None,'INSREPNUM' : None,'INVOICENUM' : None }
	with arcpy.da.UpdateCursor(fc,fields_to_add) as records:
		for record in records:
			for i in range(len(fields_to_add)):
				record[i] = defaults[fields_to_add[i]]
			records.updateRow(record)
	print("Default values populated.")

