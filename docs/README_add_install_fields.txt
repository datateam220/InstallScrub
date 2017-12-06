########                                         READ ME                                           ########
Last Updated: 10/27/2017 by Nick Sylva
#### - Enter your feature class as described in the comments below.                                    
#### - The list of fields to add includes all standard install fields. 								   
#### - If you require additional fields add them to the list. 										   
#### - This script will automatically populate the install fields to their default values. To turn off this
####   behavior change the pop_defaults variable to "False" without quotes and case-sensitive.
#### - This script will work for any TEXT field that you want to add. 								   
#### - When executing this script within ArcMap, CLOSE YOUR ATTRIBUTE TABLE: Otherwise ARC WILL CRASH! 
#### - This script will run more quickly from the command prompt than from within ArcMap.              
#### - The only thing you need to change is the feature class variable: "fc" and the fields to add if  
####   you are not using the defaults                                                                  
#### - To execute from command prompt:																   
####        1. Hit Windows + R, type "cmd" without quotes and hit Enter/Return 				
####        2. In the command prompt type, without quotes: "cd C:/Python27/ArcGIS10.5" and hit Enter.  
####        3. In the command prompt type, without quotes: "python"                                    
####        4. Your python environment should now be open. Now open a Windows Explorer window and      
####           navigate to where this is saved. Make a copy and paste it in a folder of your choice.   
####        5. Modify this file as necessary, save it, and copy the file path.                         
####        6. Return to your open python environment in the command prompt.                           
####        7. Type in, without double-quotes: "path = r'[PATH YOU COPIED]\add_install_fields.py' "    
####            Make sure the single-quote at the end is retained. Pres Enter.                         
####        8. Type in, without double-quotes: "execfile(path)" and hit Enter.                         
####        9. ...                                                                                     
####        10. Profit!                                                                                
#### - To execute this file from the ArcMap Python window, make modifications as necessary, copy, and paste  
####   the code into the Python window. Hit Enter twice to execute.
