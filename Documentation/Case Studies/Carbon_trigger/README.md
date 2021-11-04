# Carbon Segmented Cloud Computes


## Introduction
Explores the benefits and effects of controlling the progression of ML computes with regional marginal CI measurements.

<br>

## Motivation
In [Carbon Optimized Demand Shifting at Scale](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Documentation/Case%20Studies/Organizational_Shifting/README.md) a problem was identified where runs with a duration near a multiple of 24 hours have little ability to benefit from time shifting.  This case study seeks a different temporally carbon aware solution for jobs with this duration. 

<br>

## Data Source
![image](https://user-images.githubusercontent.com/80305894/140415441-815d96c4-cd09-4c6e-94ed-297a736e52e1.png)

WattTime has the most coverage for Azure data centers globally compared to other providers.  Choosing WattTime as the data source for this case study enabled a more inclusive demand shifting experiment. 

<br>

## Data Centers

![image](https://user-images.githubusercontent.com/80305894/140415396-d8e5252c-90de-49ad-b82b-5d7f4ff3e774.png)

The data centers considered in this case study are Azure data centers which are governed by a WattTime tracked balancing authority (9 data centers in the US and 24 data centers globally).  For a full list of the data centers considered in the case studies, see Appendix 6.

<br>

## Assumptions:
1.	Energy consumption is independent of time and location of the compute.
2.	Virtual Machine (VM) performance does not vary between specific devices.
3.	Data centers do not have capacity limitations. 
4.	Unless an energy profile is available, energy consumption is considered uniform over a run's duration.
5.	The regional MOER due to a data center with N jobs at time j is considered the same as the MOER at time j with N+1 jobs. 

<br>

## Considerations

Case studies only consider the operational carbon footprint and do not consider the embodied carbon of cloud compute instances. 

Energy consumption profiles are GPU operational energy consumption only and do not include CPU energy consumption or power required for data center infrastructure such as HVAC systems. 

<br>

## Methods
Energy metrics were retrieved from the [Azure Monitor API](https://azure.microsoft.com/en-us/services/monitor/) with the scripts found [here](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Retrieve_Energy_Metrics/AzureMonitorQuery/README.md). The energy profiles recovered included 31 runs that were conducted in one of the following Azure data centers: East US, South Central US, or West US 2.  These were GPU enabled ML jobs, and the profile is the total energy consumption of all GPUs used in each run. To determine the real and counterfactual carbon emissions, the energy profiles were used in Equation 1.

**Equation 1:**

![CodeCogsEqn (3)](https://user-images.githubusercontent.com/80305894/140424258-aa27f0b8-3cd4-4444-9c4f-e00ab567b322.png)

<ul>
  <li>t = Discrete time vector.
  <li>M(t) = Historic marginal operating emission rate (MOER) for a given region (i) at point time (j) for J number of timestamps, for a given time shift (k).
  <li>E(t) = Energy consumed per time interval at a specific time index (j).</li>
  <li>C<sub><i>i,k</i></sub> = Carbon emitted for a given region (i) and time shift window (k). 
  <li>C = Vector of carbon emissions resultant of different initial conditions for M(t).
</ul>

**TEMPORAL SHIFTING:** This is method is described by Equation 1 with no interval breaks in the time vector. 
**STATIC TRIGGER:** Used a static value as the threshold to determine progression of the ML run.  The average historic MOER was determined at the run start time and used for the duration of the compute.  Each trigger threshold averaged a different volume of historic MOER data being the previous year, month, week, or 12-hours. These values were taken forward and the job could only progress if the region the run was being conducted in had a MOER less than or equal to that threshold.  Each point time after the run’s start was compared to this threshold.  
**DYNAMIC TRIGGER:** This method was like the static trigger threshold method, expect instead of carrying the same average historic MOER value determined at the start of the run forward, new thresholds were allowed.  If the run progression remained stalled for a duration of 250 minutes a new average would be calculated to compare the subsequent timestamp against.  If the new threshold allowed the run to progress at the next timestamp and MOER measurement, it would be used thereafter until another 250-minute stall occurred. If the new average MOER still did not permit the run to progress, the process of recalculating a threshold would repeat until the run was allowed to continue.


## Results

### Figure 1
![image](https://user-images.githubusercontent.com/80305894/140424654-ac4d6bfa-d7da-41c3-b8c4-5c90ca66942a.png)

<sup><i>Figure 1 shows the mean percent of carbon reduced for each carbon aware method: dynamic carbon trigger, static carbon trigger, and temporal shifting. Each column cluster is separated based on the different trigger thresholds tested, with time shifting constant across each threshold cluster.</i></sup>

### Table 1
|   | **Year** | **Month** | **Week** | **12-Hours** | 
| :-------------: | :----------: | :-------------: | :----------: | :----------: |
| **Dynamic % Reduction** | 9.93 | 6.97 | 7.48 | 5.92 |
| **Static % Reduction** | 9.93 | 6.95 | 7.70 | 6.10 |

<sup><i>Table 1 is a numeric representation of Figure 1. *Time Shifting method had a mean of 0.50% carbon reduction </i></sup>

As seen in Figure 1, segmenting a compute based on CI allowed a ML run that would have had negligible benefits from time shifting, experience comparable reductions in its carbon footprint.  In Carbon Optimized Demand Shifting at Scale, we saw that runs had an average of 11.48% (see Figure 3 in [Carbon Optimized Demand Shifting at Scale](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Documentation/Case%20Studies/Organizational_Shifting/README.md)) reduction in their carbon emissions, whereas the static trigger saw a range of [6.10, 9.93] and the dynamic trigger had a range of [5.92, 9.93] percent reduction carbon emitted depending on the threshold type.  

<br>

### Figure 2
![image](https://user-images.githubusercontent.com/80305894/140425205-b671160d-9ca8-4865-998c-7e2be7990048.png)

### Table 2
|   | **No Change** | **Temporal Shift** | **Static Trigger** | **Dynamic Trigger** | 
| :-------------: | :----------: | :-------------: | :----------: | :----------: |
| **Dynamic % Reduction** | 48 | 63 | 89 | 87 |
| **Static % Reduction** | 0 | 0.5 | 6.10 | 5.92 |

<sup><i>Table 2 examines the effects the scaling values from the last column cluster in Figure 2 have on job runtime.</i></sup>

While both the static and dynamic triggers enabled a time-based approach to reducing emissions, this came at the cost of substantially increasing the run time.   
Reviewing the results, some key observations are made:
1.	The carbon trigger sees an inverse relationship between the mean percent of carbon reduced and total runtime including pauses. 
2.	Both trigger types experienced a diminished effectiveness at reducing carbon emissions as the threshold moved closer to real time mean expectation value.
3.	There was little observed difference between using a dynamic or static threshold with current configuration.

<br>

## Discussion

While using a carbon aware trigger to throttle workloads created a solution to the problem speculated about in [Carbon Optimized Demand Shifting at Scale](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Documentation/Case%20Studies/Organizational_Shifting/README.md), as-is neither the static nor dynamic triggers are economical solutions to this problem at scale due to the exacerbated runtimes produced.   As seen in Figure 2, the 12-hour trigger threshold nearly doubled the runtime whereas the yearly average trigger almost quadrupled it.  
Future work should focus on introducing new metrics or methods to calculate a dynamic threshold. Introducing conditions to drive run completion while remaining conscious of CI could balance the method and make it feasible for runs that are a multiple of 24 hours.  An example could be offsetting the threshold based on progression performance (i.e. where long pauses decrease the sensitivity to CI).  Additionally, testing with differing run types to determine the methods effectiveness at scale is needed. 
If a job is not sensitive to runtime and/or expected to be a compute with a short duration, this could be an additional technique to use in tandem with time shifting to further decrease the operational carbon footprint.  An example use-case would be where a run is scheduled in a forecasted green window, and then when the job starts use a threshold to throttle its progression.  Diurnal grid trends tend to split a given 24-hour period into day and night, so if a run is short (expected duration of 6 hours or less) the cost of scaling of the duration with a carbon trigger could be negated by out-of-office hours.  If a job is scheduled to run during out-of-office hours, there is little difference between a run coming to completion at 4:00 a.m. and 8:00 a.m.  What really matters in this instance is that the run is completed before returning to the office. 




