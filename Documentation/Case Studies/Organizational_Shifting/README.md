# Demand Shifting at Scale of Organizational Operations


## Abstract

<br><br><br>





## Assumptions:
1. Energy consumption is independent of time and location of the compute.
2. VM performance does not vary between specific devices. 
3. Unless an energy profile is available, energy consumption is considered uniform over a run's duration.


<br>

## Methods
The first step was to create an operating dataset from submitted runs with the following schema:

| Data Center | VM | Submit Time | Start Time | End Time | Delay | Run Duration |
| :-------------: | :----------: | :-------------: | :----------: | :----------: | :----------: | :----------: |
| #### | #### | #### | #### | #### | #### | #### |

With each row being an observation of a ML job, the counterfactual demand shifting potential was able to be found. 

For geographic shifting, the search for potential green regions were given the parameters of VM type, current workspace location, and run duration.  This using the VM type works to limit the potential regions to data centers that offer that VM.  This avoids a migration to a datacenter which could not meet a run’s hardware requirement. Furthermore, using the workspace region as a parameter allowed two types of counterfactual evaluations, *locked* and *open*. 

**Locked**: Restricted by VM and region.  Only data centers in the US were able to be considered for being a green region. <br>
**Open**: Only restricted by VM.  Any region globally which offers this hardware was allowed to be considered for being a green region.

Due to the energy profile being unavailable for these runs, the following is used to evaluate the redutions via demand shifting: 

![CodeCogsEqn (5)](https://user-images.githubusercontent.com/80305894/136124876-89a750bc-de33-4a06-88fb-db34183dbf16.png)

* **t** = discrete time vector<br>
* M(t) = historical marginal operating emission rate (MOER) for a given region (i) at a certain point in time (j) for J number of timestamps over the run duration.<br>
* <b>CI</b><sub><i>i</i></sub> = mean carbon intensity for a given region and time window 
* **<span style="text-decoration:overline">CI</span>** = vector of mean forecasted carbon intensities  <br>

![CodeCogsEqn (7)](https://user-images.githubusercontent.com/80305894/136124994-f57763ed-88bf-4322-8f79-d3625342eea0.png)

The green suggestion (G) is the time period in the evaluation span at a specific data center that yields the minimum mean carbon intensity



<br>

## Considerations
As a result of WattTime providing data at 5-minute intervals, the input data had to be formatted to fit this.  To do this, the end times were rounded to the nearest 5-minutes, so short runs were able to return a carbon intensity value.  The issue with this is that sometimes the nearest 5-minutes was before the run start.

*Example*  <br>
*Recorded run start time = 13:46:22* <br>
*Recorded run end time  = 13:46:37* <br>
*Rounded run end time =  13:45:00* <br>

When this happened and a negative run duration created, a bad response is returned.  This resulted in the observation being tagged for later removal.


<br>

## Results



<br><br>


## Discussion
