Use Cases
=========

Use Case 1: Plant-Wide Analysis of Control Loop Data
----------------------------------------------------
The **Constraint Detection Add-on** is suited for plant-wide analysis of control loop data. In this example, an asset tree with 111 controllers was analysed. Every controller has 4 signals assigned to it (Controller Output, 
Process Variable, Setpoint and Mode) which results in a total of 444 signals. The plant is divided into 2 sections where both sections have 6 units each. The structure of the asset tree and the number of controllers per unit is shown
below.

.. figure:: /images/asset_structure_use_case_1.png
   :scale: 80%
   
   Figure 1: Structure of the asset tree for use case 1

The asset tree was analysed over a period of one week and the Add-on looked for constraints/saturation in all controller outputs, process variables and setpoints. The copy of the asset tree was named "Plant Constraint Detection Results".
The thresholds were set to their default values 50% and 10%. No short capsules or gaps were specified.

.. figure:: /images/user_interface_use_case_1.png
   
   Figure 2: UI for use case 1

After the Add-on has finished the analysis, the table in the user interface is populated with the Top 30 of the most constrained/saturated signals in descending order. The table gives you a signal name and path, so that signals with high 
indices can be found easier in the treemap in the workbench. In addition, the table can be sorted by every column which gives you the option to target specific signal types or plant sections.

.. figure:: /images/table_use_case_1.png
   
   Figure 3: Index table for use case 1

The new "Plant Constraint Detection Results" asset tree can be found in the Data panel in the workbench. For every analysed signal, there are now 2 additional signals and 2 additional conditions:

	* Analysed Signal
	* Constraint/Saturation Signal
	* Constraint/Saturation Index
	* Medium Constraint/Saturation Condition
	* High Constraint/Saturation Condition

Based on the new signals and conditions, further analysis can be executed using the tools in the workbench.

.. figure:: /images/asset_tree_use_case_1.png
   
   Figure 4: Signals and conditions in the "Plant Constraint Detection Results" asset tree for use case 1

In the workbench, a new worksheet called "Constraint Detection Treemap View" has appeared. The treemap is coloured according to the thresholds which were set previously in the user interface. The thresholds give you the possibility to
prioritize control loops and to visualize your priorities. The constraint/saturation index was selected as a statistic to be displayed in the treemap to facilitate the interpretation of the analysis results.

.. figure:: /images/treemap_use_case_1.png
   
   Figure 5: OP treemap for use case 1

From the treemap, it is easy to get to the trend view by clicking on a controller panel. In trend view, the constrained/saturated periods can be investigated in more detail and underlying causes for constraints/saturation can be 
identified.

.. figure:: /images/trend_view_use_case_1.png
   
   Figure 6: Trendview for use case 1



Use Case 2: Identifying Bad Actors
----------------------------------
For the second use case, the asset tree from use case 1 was used again to identify bad actors. For this purpose, the thresholds for the treemap were adjusted. The red threshold and the yellow threshold were both set to 80%. 
Therefore, only red and green panels will appear in the treemap which makes it easier to find signals with a very a high constraint/saturation index. This use case shows how the threshold settings in the user interface can be used to
get a treemap visualization which is tailored to the user's requirements.

.. figure:: /images/user_interface_use_case_2.png
   :scale: 110%

   Figure 7: UI for use case 2

The analysis was performed over period of one week and the new asset tree was named 'Plant Bad Actors'. Figure 7 shows how the signal table got populated after the analysis was finished. In addition, the 'Export table to CSV' button got
enabled so that the table can be downloaded. In the treemap, the controller outputs with very high saturation indices stand out and are easy to find, as can be seen below for controller 44 in Section A >> Unit 3.

.. figure:: /images/treemap_use_case_2.png
   
   Figure 8: OP treemap for use case 2

If a bad actor is identified, the trend view for the corresponding controller can be investigated by clicking on the controller panel.

.. figure:: /images/trend_view_use_case_2.png
   
   Figure 9: Trendview for use case 2





