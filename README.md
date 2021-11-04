
# Carbon Aware API
<sup>*Draft, Project In Progress*</sup>

## Navigation
<ol>
  <li><a href="#Carbon Aware API">Overview</a></li>
  <li><a href="#Case Studies">Case Studies</a></li>
  <li><a href="https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Carbon_Aware_API#api-architecture">API Architecture</a></li>
  <li><a href="https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Documentation/Methods.md">Methodology</a></li>
  <li><a href="https://carbon-aware-api.herokuapp.com">Sample User Interface</a></li>
</ol>


## Terminology 
| Term | Definition   |
| :------------- | :---------- | 
| **Carbon Intensity** | Carbon emitted per energy unit. |
| **Grid-Based Carbon Intensity**   | All entities who operate on a shared electrical grid, share a common emission rate. | 
| **Marginal Carbon Intensity**   | The emissions intensity of the marginal power plant which will be turned on when additional load is added to the grid.|
| **Carbon Aware** | 	Adjusted behavior in response to the *carbon intensity* of consumption.|
| **Carbon Delta**   | The difference in emissions between *carbon aware* and unaware actions. | 
| **Carbon Counterfactual**   | The *carbon delta* had the carbon aware action been different.| 
| **Demand Shifting**   | Selectively changing the time/location of a compute's execution, to a time/location where the energy demands are met by cleaner energy production, resulting in a lower *grid-based carbon intensity*.|
| **Operational Emissions**   | Emissions explained by the energy consumption and location-based *carbon intensity* measurement during times of operation.| 
| **Embodied Emissions**   | Carbon emissions resultant of creating the hardware, structural systems, maintanence, etc. (e.g. constructing a GPU or datacenter).| 


Other definitions and methods for the Carbon Awareness found at: [Green Software Foundation](https://github.com/Green-Software-Foundation)

<br><br>


![Banner](https://user-images.githubusercontent.com/80305894/132620015-b0a5007a-d605-43ca-a260-8b3bc5206b32.png)
<br><br>
<a name="Carbon Aware API"></a>

## Overview

To enable organizations to make smart decisions about their environmental impact and carbon footprint, we have created the Carbon Aware API to minimize the operational emissions of computational workflows. A few key features of the API are: 

* Utilizes marginal carbon emission measurements from WattTime to map carbon intensity rates to data centers. 
* Generates a retrospective carbon emission analysis 
* Provides forecasted demand shifting suggestions 
* Supplies regional carbon intensity information over different scopes  
* Hosts a green region picker for workspace configuration.

**Marginal Carbon Emissions:** This grid-responsive metric with finer granularity than average emissions, allows for seasonality/diurnal trends captured in demand shifting (source). 

**Retrospective Analysis:** Time series evaluation to assess the carbon emissions for a given energy profile. Also provides counterfactual analysis to expose the potential emissions of if the run had been shifted. 

**Demand Shifting Scheduler**: Recommends data center and/or time which would yield a less carbon intensive run.  

* Temporal: Identifies the window of minimum carbon intensity for a specified run duration within a chosen region from a 24-hour forecast.  
* Geographic: Finds the region with the current lowest average carbon intensity for an immediate run of a specified duration. Can filters available regions by available SKU and migration laws for workspaces with protected data.  

**Regional Carbon Intensity:** Provides the carbon intensity for each data center supported by a WattTime-tracked balancing authority.  The possible scopes are historic intensities (time series for prior 24-hours, week, and month), real-time marginal intensity, and forecast (mean intensity for upcoming user-defined window). 

**Green Region Picker:** Recommends the a data center to host a workspace based on expressed needs such as carbon efficiency, price, and latency.
<br>

For more information, please see the full tool description: [Carbon Aware API Details](https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Documentation/Overview)




<br>

<a name="Case Studies"></a>

## Case Studies

<sup>Carbon intensity data for case studies provided by: [WattTime](https://www.watttime.org/) </sup>



### Demand Shifting at Scale of Organizational Operations
<sup>September 2021</sup>

**Details:** *Geographically and temporally shifting compute instances at scale would reduce carbon by X%*

**Results:** Organizations can reduce their operational emissions by 48% by geographically shifting and 12% by temporally shifting ML computes. 

For more information and detailed results, please see the full case study: [Demand Shifting at Scale of Organizational Operations](https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Documentation/Case%20Studies/Organizational_Shifting)

<br>

### Carbon Segmented Cloud Computes
<sup>October 2021</sup>

**Details:** *Execute and progress cloud computes greater than 24 hours in duration during periods of low emission to reduce the carbon footprint by Y%*

**Results:** *Computes greater than 24 hours saw 0% change with standard temporal shifting, but controlling progression based on regional carbon intesity thresholds reduced operational emissions by 10%*

For more information and detailed results, please see the full case study: [Carbon Segmented Cloud Computes](https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Documentation/Case%20Studies/Carbon_trigger)






