###################################### INSTALL SCRUB SCRIPT README ######################################
Last Updated: 10/26/2017 by Nick Sylva



PURPOSE:

 The Install Scrub Script accomplishes the following tasks:
 - Updating the master install data set with changes made in Collector.
 - Detects issues, including:
     - Accidentally clicked points (ignored).
     - Incomplete Surveys (reports which fields need to be completed and flags DATA ISSUE).
     - Skipped Fixtures (reports skips and includes any comments; flags SKIPPED)
     - High Voltage Fixtures (reports >120V; flags FIELD ISSUE).
     - Install Issues (reports any issues from the INSISSUES field; flags FIELD ISSUE).
     - Design vs. Install Discrepancies (reports when the designed fixture is not what the installer
       indicated as installed; flags DATA ISSUE).
     - Reports comments (flags REVIEW if no other issues take precedence).
 - Reports any attribute values that differ between datasets. Report recorded in a CSV including: TANKO_ID,
   Field Name, Old Value, New Value, and a datetime stamp of when the comparison was made.
 - Creates a log file of notes pertaining to:
 	 - Start and stop time of the session.
 	 - Issues
 	 - Previously installed records that were changed.
 	 - Updated records (regardless of issues) including ID and datetime stamp of when the update was made.



FIELDS AND DEFAULT VALUE ASSUMPTIONS:

 The script assumes that the field names in both your master dataset and your Collector dataset are
 standardized. The easiest way to ensure this is to use the add_install_fields.py script to generate your
 install fields during install preparation. The script can also set the install fields to their default
 values. Default Install fields and their values:
 	INSOLDLAMP: 'Choose...'
 	INSOLDWATT: 'Choose...'
 	INSVOLTAGE: 'Choose...'
 	INSFIXTURE: 'Choose...'
 	INSCOMPLET: 'Not Yet Installed'
 	INSPCSC: 'Choose...'
 	INSISSUES: 'None'
 	INSCOMMENT: <Null>
 	INSSTAT: <Null>
 	INSNOTE: <Null>
	INSBY: <Null>
	INSDATE: <Null>

 Some fields may differ between projects. The expected fields are below. Defaults are not applicable to these
 fields. If your project uses a field name different from these, talk to Nick Sylva for direction on how to 
 accomodate for field name discrepancies. Fields that may differ from the standard include:
 TANKO_ID: Data type should be integer.
 POLENUM: Data type should be string.
 DESFIXT: String; older projects may use PROP_FIXT 



DATA TYPE ASSUMPTIONS:

 The required input data for this script can be:
 	- Feature Class or Feature Table
 	- Shapefile

 Excel files, CSVs, JSON, etc. are not compatible with this script.



PROCEDURE:
 
 1. Copy this entire folder to you project Directory\GIS\DATA\INSTALL\Scripts. 
    If the Script folder does not exist, create it. There should be five files
    in the directory:
    	- README_InstallScrub.txt (this file)
        - README_add_install_fields.txt
    	- add_install_fields.py
    	- startScrub.py
    	- InstallScrub.py
    	- __init__.py
        - EXAMPLE
    If you have previously run this script in this folder, there will be a sixth
    file, which can be ignored:
    	- InstallScrub.pyc

 2. The only file that needs to be edited is the startScrub.py file. Open it in Notepad, Notepad++, Sublime
    Text, or whichever raw text editor you prefer. I do not recommend using Microsoft Word for this purpose
    as it sometimes handles code and raw text poorly.

 3. There are three variables that need to be adjusted:
 		- project_name
 		- Master_FC
 		- Collector_FC
 	Modify these three fields as follows:
 		- project_name: Enter the name of the project you are working on. Avoid using spaces or other special
 		  characters that you would not use for a file name. The name you enter here will be used to prefix
          log files, so keep that in mind.
 		- Master_FC: Enter the path to your master feature class for your project. If your feature class is
 		  within a feature dataset you will need to account for it in the path.
 		  Ex. r'T:\BSD\1_ Municipal Projects\Chester, CT\GIS\DATA\Chester.gdb\Audit\Chester_Audit_Master'
 		  IMPORTANT: notice the "r" prior to the single quotation mark. This indicates a raw string.
 		  If you remove the "r," the script WILL NOT WORK. The single quotes around the path itself are 
          equally important. Make sure the path is in the format of:
 		  r'PATH\TO\GDB\FEATUREDATASET\FEATURECLASS'
 		- Collector_FC: Enter the path to the feature class or feature table of you collector export of
 		  for whatever period you are scrubbing.

 4. Save the startScrub.py file.
 
 5. If your Install Scrub MXD is not already open in ArcMap, open it now.
 
 6. In ArcMap, open the Python window (Geoprocessing Menu > Python).

 7. In the Python window, right click to open the context menu and then click "Load..."

 8. Browse to the directory where you saved the script folder and double-click the startScrub.py file 
    that you edited.

 9. The code will load into the Python window. Hit the Enter/Return key twice. The code should run. 

 10. A successful run will print the following messages to the Python window:
 		>>> Install Scrub session start: [DATETIME STAMP]
 		>>> Records for dataset ID: 0 imported successfully.
 		>>> Records for dataset ID: 1 imported successfully.
 		>>> Issues found!
 		>>> Updates populated.
 		>>> Data written to feature class.
 		>>> Install Scrub session end: [DATETIME STAMP]
 
 11. Open the attribute table for your master feature class. The install fields that changed will be updated.
     INSSTAT will be populated with COMPLETE, FIELD ISSUE, DATA ISSUE, or REVIEW.
     INSNOTE will contain any notes related to the scrub.
 
 12. This script generates two log files, a .csv and a .txt file. The log files are saved in the same 
     folder as the scripts. The .csv contains any fields that were different between the two data sets.
     The .txt file contains a log of the issues the script encountered. These can be directly copied to your
     summary email.
 
 13. Verify the data in your attribute table. Anything that has an INSSTAT value other than COMPLETE should
     be reviewed. In some cases, a specific issue found by the script may not be an issue for a particular
     project. For example, in Miami Lakes, FL, there are many fixtures with a voltage higher than 120V that
     are not issues. 