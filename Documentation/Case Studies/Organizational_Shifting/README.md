# Carbon Optimized Demand Shifting at Scale

## Introduction
Investigates potential operational carbon footprint reductions for shifting ML computes geographically and temporally. 

<br>

## Data Source
![image](https://user-images.githubusercontent.com/80305894/140415441-815d96c4-cd09-4c6e-94ed-297a736e52e1.png)

WattTime has the most coverage for Azure data centers globally compared to other providers.  Choosing WattTime as the data source for this case study enabled a more inclusive demand shifting experiment. 

<br>

## Data Centers

![image](https://user-images.githubusercontent.com/80305894/140415396-d8e5252c-90de-49ad-b82b-5d7f4ff3e774.png)

The data centers considered in this case study are Azure data centers which are governed by a WattTime tracked balancing authority (9 data centers in the US and 24 data centers globally).  For a full list of the data centers considered in the case studies, see [Appendix 6](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Documentation/Appendices.md#Appendix%206).

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
An operating dataset of submitted runs was created with this schema:

| Data Center | VM | Submit Time | Start Time | End Time | Delay | Run Duration |
| :-------------: | :----------: | :-------------: | :----------: | :----------: | :----------: | :----------: |
| #### | #### | #### | #### | #### | #### | #### |

With each row being an observation of a ML job, an approximate carbon counterfactual for demand shifting was able to be found.


![CodeCogsEqn (1)](https://user-images.githubusercontent.com/80305894/140418465-4b85cd1e-5945-4e95-a89e-47965990c6b4.png)


<ul>
  <li>t = Discrete time vector.
  <li>M(t) = Historical MOER for a given region (i) at a point time (j) for J number of timestamps over the run duration for a given time shift (k).
  <li>CI<sub><i>i,k</i></sub> = Mean carbon intensity for a given region (i) and time window (k).
  <li>CI = Vector of mean historic carbon intensities.
</ul>


**GEOGRAPHIC SHIFTING** searched for potential green regions with the parameters of VM type, current workspace location, and run duration.  These searches were carbon optimized shifts which did not include latency or price as shifting metrics. Furthermore, because these were strictly retrospective runs, the real-time grid self-rating was also unable to be used, as these are not included in historic logs from the source API. This caused the maximum rating used in real time geographic shifting to be equivalent to the region with the minimum average MOER over the runtime window.

Using the VM type worked to limit the potential regions to data centers that offer that VM available as a service. This avoids an issue of migrating to a datacenter which could not meet a run’s hardware requirement. Furthermore, using the data center as a parameter allowed two types of counterfactual evaluations: *locked* and *open*.
**Locked**: Restricted by VM and region. Only data centers in the within the governing boundaries of the cluster region were able to be considered for being a green region. <br>
**Open**: Only restricted by VM. Any data center globally which offers this hardware was eligible to be a green region.

**TIME SHIFTING** used the same input parameters as geographic shifting (VM, location, duration) and searched up to 24-hours after the run start time to find the period of minimum average operating emissions. The maximum of 24-hours was set to simulate the limitations of forecasting. 



<br>


## Results

### Figure 1
![image](https://user-images.githubusercontent.com/80305894/140416307-eb3b41cc-c81e-4cd1-98fb-5c8dec50a145.png)

<sup><i>Figure 1 shows the results for a carbon counterfactual evaluation for geographic shifting across the Azure data centers which are supported by a WattTime balancing authority but constrained by migration barriers. 5783 runs ranging between 7/28/2021 to 9/3/2021 were included in the evaluation. These runs used one of three VM SKU’s: NC24RS_V3, NC24S_V3, and ND40RS_V2 and were executed at one of the following data centers: East US, South Central US, West Europe, or West US 2. Plot shows the distribution of best geographic shifting carbon counterfactuals over all considered runs where the x-axis is percent change, and the y-axis is the count per bin.</i></sup>

Locked shifting considers data migration governance based on the cluster region to simulate geographic shifting for workspaces with sensitive data.  For example, if the cluster region is a US-based data center, only data centers located in the US could be considered for the shift.  This was also done for any workload executed in the EU to simulate concepts such as General Data Protection Regulation (GDPR) compliance.  Shown in Figure 1, while limiting the number of eligible data centers due to regional data governance, geographic shifting still saw an average of 26.35% reduction in operational emissions.  West US was the champion data center. As shown in [Appendix 4](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Documentation/Appendices.md#Appendix%204), West US has a large supply of renewable energy during the day which aligned with when most observed runs were conducted.

<br>

### Figure 2
![image](https://user-images.githubusercontent.com/80305894/140416534-66c09b15-d26f-4fa5-9a16-2d0224d8d390.png)

<sup><i>Figure 2 shows the results for a carbon counterfactual evaluation for geographic shifting across all Azure data centers which are supported by a WattTime balancing authority. 5783 runs ranging between 7/28/2021 to 9/3/2021 were included in the evaluation. These runs used one of three VM SKU’s: NC24RS_V3, NC24S_V3, and ND40RS_V2 and were executed at one of the following data centers: East US, South Central US, West Europe, or West US 2. Plot shows the distribution of best geographic shifting carbon counterfactuals over all considered runs where the x-axis is percent change, and the y-axis is the count per bin.</i></sup>
<br>

Open shifting did not consider data migration governance restrictions to simulate runs not working with sensitive data.  In this scenario where data had no applicable regional data governance laws, carbon optimized geographic shifting had an average of 48.04% reduction in operational carbon emissions.  In this experiment, France Central and West US were the champion data centers which were most frequent in seeing workloads shifted to them. 

<br>


### Figure 3
![image](https://user-images.githubusercontent.com/80305894/140416810-f15f7866-7ffe-4b80-946e-d7e6e125c352.png)

<sup><i>Figure 3 shows the results for a carbon counterfactual evaluation for temporally shifting runs shifting without changing the cluster location. Job run durations range from 0 to 672 hours with an average of 4-hour duration, and all ran between the 7/28/2021 to 9/3/2021.  These runs used one of three VM SKU’s: NC24RS_V3, NC24S_V3, and ND40RS_V2 and were executed at one of the following data centers: East US, South Central US, West Europe, or West US 2. Runs had a start delay ranging between 0 to 112 hours from the time of job submission and then a carbon aware temporal shift from the start could be added ranging from 0 to 24 hours. Plot shows the distribution of best geographic shifting carbon counterfactuals over all considered runs where the x-axis is percent change, and the y-axis is the count per bin.</i></sup>

As shown in Figure 3, temporal shifting had an average of 11.48% reduction in carbon emissions across all runs and VM SKU’s and data centers with an average delay of 12.89 hours until the run would start.  This factored in both the start delay (already occurring time delta between job submissions and start) and the time shift required for a carbon aware run (time delta from real start time and carbon aware start time). 
Investigating further, several notable observations were made considering all regions:
1.	The longer the run duration, the lower the reduction in carbon emissions via time shifting. 
2.	Not all runs can be deferred by 24 hours. Restraining to the upcoming 12 hours saw a 10.84% carbon reduction and an average total delay (start delay + time shift) of 6.55 hours. 
3.	Not all runs are deferrable.  The average start delay was 40 minutes.  Excluding any run with a start delay of less 1-hour (already being delayed an hour suggests lower priority, and therefore eligible for time-shifting) saw a mean 6.99% carbon reduction using up to a 24-hour time shift.  For runs of this nature, if constrained to the upcoming 12 hours, the time shifted runs had a 5.86% mean carbon reduction. 
Another key observation is that the effectiveness of time shifting varied across regions as shown in Table 1.
### Table 1: Mean Carbon % Reduction per Azure Data Center

|   | East US | South Central US | West Europe | West US 2 | 
| :-------------: | :----------: | :-------------: | :----------: | :----------: |
| Mean Reduction (%) | 6.80 | 3.60 | 16.86 | 20.53 |

<sup><i>Table 1 shows the mean carbon counterfactual reduction for each region using a 24-hour search.</i></sup>


## Discussion

GEOGRAPHIC SHIFTING saw the best improvement in carbon emissions, but it also requires the most consideration for executing.  During trials, ‘champion’ data centers were observed where runs were seen being shifted to most.  This has potential downstream consequences for these grids.  While the marginal unit is responsive to load changes, without an additional metric beyond grid intensity, the emissions will still be driven up until becoming equivalent to other grids as result of workloads being transferred to them at scale.  This reinforces the importance of using the grid self-rating in to help the distribution of workloads in geographic shifting.  This value helps balance the real-time status of a grid with the expected MOER over the upcoming time window to not drive net regional emissions up substantially.  If a grid invested in clean energy to have lower net carbon intensity, shifting workloads to those regions would exceed the capacity of the clean energy supply, resulting in dirtier supply stacks being used anyways.  Without compensation or remedy, this negates a grid’s incentive to expand and invest in green energy supply.  
Even when limited in shifting options, geographic demand shifting has the potential to significantly reduce the operational emissions of cloud computes.  There are complexities which need to be considered to execute this method effectively and ethically, but the overall changes needed to the infrastructure of the cloud is small.  This method uses the same hardware and resource performance, same instance start and runtime, but with a lower carbon footprint.

TEMPORAL SHIFTING is a solution to help reduce operational emissions, which is easier to implement with minimal changes to current practices, but unlike geographic shifting it is highly dependent on the operation time of the compute instance.  Referring to [Appendix 4](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Documentation/Appendices.md#Appendix%204) and [Appendix 5](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Documentation/Appendices.md#Appendix%205), the supply and demand of power varies throughout a day, and as a result the emissions do as well. These trends are the key aspects that temporal shifting captures, enabling a carbon aware choice to result in reduced carbon emissions.   If a compute instance is longer than the mean off-peak emission duration of a grid, then temporal shifting has fewer carbon aware options which can produce a different result than a carbon unaware action because the net result of any shift is approximately the same.  Future work may be able to investigate if there is a relationship which allows longer runs to still be effective for time shifting by building off the idea that minimal net reductions occur at multiples of 24 hours and not just for runs longer than 24 hours. For example, a 36-hour run may still be able to achieve greater reductions in its carbon emissions than a 24-hour run. This suggests that time shifting effectiveness is not explicitly dependent on run duration, but on the number of off-peak to peak periods captured during the runtime.  This would also require a new CI data source as at the time of this study, WattTime only generates a 24-hour MOER forecast per region at most.  Work to extend the forecast would be needed to accommodate runs longer than 24-hours.

Currently, carbon aware scheduling an instance has limits due to the range of MOER forecasts, but within that range the diurnal trends (however large or small) of regions can be used to lower net operational emissions. Computes which are not time-sensitive and not long-running can be scheduled such that their footprint is minimized.  This method could be deployed today to provide carbon aware cloud resources, and as shown in Table 1 could a have substantial impact on the operational emissions in regions that exhibit high daily variation. 
