Introduction
============

Overview
--------

**seeq-constraintdetection** is an Add-on for control loop performance monitoring which is used for detecting constraints and saturation in control loop signals. A control loop consists of multiple components which are namely 
the controller, the actuator, the process, and the sensor. 

.. figure:: /images/control_loop_with_constraints.png
   
   Figure 1: Control loop with constraints

The outputs of these components are the setpoint (SP), the controller output (OP), the measurement of the process variable (PV) and the manipulated variable (MV). The setpoint, 
controller output, process variable and manipulated variable can reach constraints due to different underlying reasons. The actuator and the sensor can reach a constraint because of their physical limitations due to the actuator range 
or the measuring range. The controller output can become saturated because it is artificially limited due to actuator's input limitations (4-20 mA, 0-10 V etc.). The setpoint can meet constraints if certain control structures such as 
model predictive control (MPC) are used. When a control signal reaches a constraint, the time trend sticks to the signal minimum or maximum and only deviates from the for short time periods.

.. figure:: /images/introduction_time_trend.png
   
   Figure 2: OP signal with saturation

**seeq-constraintdetection** imports a complete asset tree consisting of control loop data and detects periods where control signals reach a constraint or become saturated. The detection results are visualized in treemap view where the 
user gets a plant-wide overview of constrained/saturated signals and can drill down to the time trend where periods of constrained operation are shown as time capsules. In addition, a constraint index is calculated as the time-percentage
a signal is constrained/saturated in the analysed time period. The Add-on provides an intuitive user interface in which the user can specify which time period and which control signals are of interest for him/her. Furthermore, thresholds can be set for the 
coloured visualization of the constraint index in the treemap.

.. figure:: /images/introduction_treemap.png

   Figure 3: Constraint detection results in treemap view

Video: Introduction to Constraint Detection
-------------------------------------------

.. video:: _static/constraint_detection_add-on_intro.mp4
   :width: 700

