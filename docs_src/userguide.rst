User Guide
==========

Asset Tree for Constraint Detection Add-on
------------------------------------------
The Constraint Detection Add-on analyses a complete asset structure of control signals. In order for the Add-on to recognize which signals belong to which controller and which signal type is involved, the asset tree must be available in 
a specific structure. Each control signal must be assigned to a controller and must be named according to its signal type. This is necessary so that the results can be displayed correctly in the treemap. Accepted names for the control 
signals are only "Controller Output", "Setpoint", "Process Variable", "Manipulated Variable" and "Mode". No specific naming is required for the higher-level controllers. The controller can be named "Controller 1" or "FIC 1" or 
completely different. Template code for generating the required asset tree in Seeq Data Lab can be found here.

.. figure:: /images/template_asset_tree.png

   Figure 1: Example for an asset tree in the required structure

Workflow
--------
1. Open **Constraint Detection** from Seeq's Add-on menu in the Tools panel.
2. Select a start and end time for the analysis. By default, the Add-on will insert the start and end of the display range in the active worksheet. 
3. Select the signal types you want to analyse. For example, if only the controller output signals are to be analysed, only the checkbox for 'Controller Output' must be activated.
4. Enter the name of the asset tree you want to analyse. 
5. (Optional) Enter a name for the asset tree copy. The Add-on generates a copy of the asset tree in the analysis time interval. After the analysis, the asset tree copy with the specified name will show up in the Data panel in the workbench. If the text field is left empty, the word 'Copy' will be appended to the asset tree name. For example, if the asset tree name is "Example", the new asset tree will be named "Example Copy".
6. Enter threshold values for the treemap visualization. 

	* If the constraint/saturation index lies below the yellow threshold, the corresponding controller will have a green colour in the treemap. 
	* If the constraint/saturation index lies between the yellow and the red threshold, the corresponding controller will have a yellow colour in the treemap. 
	* If the constraint/saturation index lies above the red threshold, the corresponding controller will have a red colour in the treemap.

7. (Optional) If short capsules or gaps should be ignored during periods where the analysed signal is constrained/saturated, then short capsules and short gaps can be specified in the expansion panel.
8. Run the analysis by clicking the 'Execute' button. A progress bar will appear and the user interface will be disabled while the Add-on is executing the analysis. If your asset tree contains several hundred signals and you want to execute the analysis for a large time span, then the analysis can take around 15 minutes.
9. Wait for the user interface to be enabled again. The analysis is now complete. The table will show a Top 30 of the signals with the highest constraint/saturation indices. The table can be downloaded by clicking the 'Export table to CSV' button.
10. Return to the workbench and refresh the web page. Then move to the worksheet with the name 'Constraint Detection Treemap View'. The new asset tree is shown in treemap view for one signal type. For additional insights, the constraint index or saturation index can be selected as a statistic.
11. Explore the treemap and use the table in the user interface as guidance. 
12. Close the Add-on window.

.. figure:: /images/user_interface_guide.png

   Figure 2: Worflow in the UI

Causes for Constraints and Saturation
-------------------------------------
Causes for Controller Output Saturation:

	* Intended way of operation
	* External disturbances
	* Inappropriate actuator dimensioning
	* Integral wind-up
	* The system is operated away from its original design specifications

Causes for Process Variable Constraints:

	* The actual process variable lies outside of the sensor's measuring range 
	* The sensor is damaged

Causes for Setpoint Constraints:

	* Constrained MPC is applied
	* Cascade control with constraints is applied

Causes for Manipulated Variable Constraints:

	* Intended way of operation
	* Inappropriate actuator dimensioning


Video: User Guide
-----------------



