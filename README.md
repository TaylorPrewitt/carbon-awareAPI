
# Carbon Aware API
<sup>*Draft, Project In Progress*</sup>

## Sections
<ol>
  <li><a href="#Carbon Aware API">Overview</a></li>
  <li><a href="#Tool Architecture">Architecture</a></li>
  <li><a href="#Tool Methodology">Tool Methodology</a></li>
  <li><a href="#Tool Validation">Tool Validation</a></li>
  <li><a href="#Case Studies">Case Studies</a></li>
  <li><a href="#Tool Recommendations">Recommendations</a></li>
</ol>

## Terminology 
| Term | Definition   |
| :------------- | :---------- | 
| **Carbon Intensity** | Carbon emitted per energy unit. |
| **Grid-based carbon intensity**   | All entities who operate on a shared electrical grid, share a common emission rate. | 
| **Carbon Aware** | 	Adjusted behavior in response to the *carbon intensity* of consumption.|
| **Carbon delta**   | The difference in emissions between *carbon aware* and unaware actions. | 
| **Carbon counterfactual**   | The *carbon delta* had the carbon aware action been different.| 
| **Demand Shifting**   | Selectively changing the time/location of a compute's execution, to a time/location where the energy demands are met by cleaner energy production, resulting in a lower *grid-based carbon intensity*.|

Other definitions for the Carbon Awareness found at: <br>
<a href = "https://github.com/Green-Software-Foundation/Dictionary/blob/dev/Dictionary/Dictionary.md">Green Software Foundation Dictionary</a>

<br><br>


![Banner](https://user-images.githubusercontent.com/80305894/132620015-b0a5007a-d605-43ca-a260-8b3bc5206b32.png)
<br><br>
<a name="Carbon Aware API"></a>

## Carbon Aware API

To enable organizations to make smart decisions about their environmental impact and carbon footprint, we have created the Carbon Aware API to minimize the carbon emissions of computational workflows. A few key features of the API are: 

* Utilizes marginal carbon emission from WattTime to identify carbon intensity per region 

* Generates a retrospective carbon emission analysis 

* Provides forecasted demand shifting suggestions 

* Supplies regional carbon intensity information over different scopes  

**Marginal Carbon Emissions:** This grid-responsive metric with finer granularity than average emissions, allows for seasonality/diurnal trends captured in demand shifting (source). 

**Retrospective Analysis:** Time series evaluation to assess the carbon emissions for a given energy profile. Also provides counterfactual analysis to expose the potential emissions of if the run had been shifted. 

**Demand Shifting Scheduler**: Recommends region and/or time which would yield a less carbon intensive run.  

* Temporal: Identifies the window of minimum carbon intensity for a specified run duration within a chosen region from a 24-hour forecast.  

* Geographic: Finds the region with the current lowest average carbon intensity for an immediate run of a specified duration. Can filters available regions by available SKU and migration laws for workspaces with protected data.  

**Regional Carbon Intensity:** Provides the carbon intensity for each data center supported by a WattTime- tracked balancing authority.  The possible scopes are historic intensities (time series for prior 24-hours, week, and month), real-time marginal intensity, and forecast (mean intensity for upcoming user- defined window). 

<br>

<a name="Tool Architecture"></a>

## Architecture



![Slide1](https://user-images.githubusercontent.com/80305894/133732784-a3cf30d2-577d-4efd-81e0-c5cc4211fc1c.jpg)
<a href = "https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Carbon_Aware_API">Carbon Aware API</a>
<br><br>


![Slide2](https://user-images.githubusercontent.com/80305894/133732786-353f6794-32ca-4049-a2ed-b0103005efb2.jpg)
<a href = "https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Carbon_Aware_API/wsgi.py">wsgi.py</a>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href = "https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Carbon_Aware_API/app">app</a>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<br><br>

![Slide3](https://user-images.githubusercontent.com/80305894/133735224-0cc694e5-61fd-4d47-8df6-2213ca32a4c3.jpg)
<a href = "https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Carbon_Aware_API/app/utils.py">utils.py</a>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href = "https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Carbon_Aware_API/app/data.py">data.py</a>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href = "https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Carbon_Aware_API/app/services">services</a>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href = "https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Carbon_Aware_API/app/routes">routes</a>
<br><br>


![Slide4](https://user-images.githubusercontent.com/80305894/133736223-e47cbe41-d5e5-4ab0-9aea-ad829763f1a9.jpg)
<a href = "https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Carbon_Aware_API/app/routes/ci_data.py">ci_data.py</a>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href = "https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Carbon_Aware_API/app/routes/shift.py">shift.py</a>
<br><br>


<a name="Tool Methodology"></a>

## Tool Methodology

**Retrospective Analysis**: By mapping grid-based marginal carbon intensity measurements to energy consumption profiles, the carbon footprint of cloud workloads is identified and evaluated.  Part of this evaluation is to find carbon counterfactual emissions of if carbon aware scheduling was used, reporting possible outcomes of temporal and geographic shifts.  



Given the following:
<br>

![CodeCogsEqn (1)](https://user-images.githubusercontent.com/80305894/133733435-c8532304-3a4a-4140-9dbd-cc449758f423.png)

Where:

* **t** = discrete time vector<br>
* M(t) = marginal operating emission rate (MOER) for a given region (i) at a certain point in time (j) for J number of timestampes.<br>
* E(t) = energy consumed per time interval
* C<sub><i>i</i></sub> = carbon emitted for a given region and time window (C<sub><i>0</i></sub> is the result from the M(t) for when and where the run was executed)
* **C** = vector of carbon emissions resultant of different initial conditions for M(t) <br>

Using **C** the carbon couterfactuals can be identified because each value is the outcome of a different potential workload shift.    

**Demand Shifting**: Combining carbon intensity forecasts from a certified provider, with anticipated workload constraints such as runtime, governance, and needed hardware, a green window can be found in the forecasted time span. 

Given the following:
<br>

![CodeCogsEqn (2)](https://user-images.githubusercontent.com/80305894/133733627-aeffbdce-4714-4b31-97aa-247123332acd.png)

Where:

* **t** = discrete time vector<br>
* F(t) = forecasted marginal operating emission rate (MOER) for a given region (i) at a certain point in time (j) for J number of timestampes.<br>
* <span style="text-decoration:overline">CI</span><sub><i>i</i></sub> = mean forecasted carbon intensity for a given region and time window 
* **<span style="text-decoration:overline">CI</span>** = vector of mean forecasted carbon intensities  <br>

Followed by:
<br><br>
![CodeCogsEqn (3)](https://user-images.githubusercontent.com/80305894/133733779-a7e25132-613c-4788-ac1a-c7ce2fa4f2f0.png)

The green suggestion (G) is the time period in the forcast span at a specific data center that yields the minimum mean forecasted carbon intensity. The goal of the Carbon Aware API is to find which start time (t<sub>0</sub>) and/or location that would result in the least carbon to be emitted.  

For each permitted data center all possible windows in the forecast span are searched to find the lowest average emitter. 
* Time-shifting: no data center variation permitted. Sliding search to find best start time for the green window.
* Geographic-shifting: no start time variation. Evaluates permitted data centers to find the greenest location for an immediate start.
* Complete Shifting: data center and start time variation. Sliding search to find best start time for the green window across all permitted data centers. 

For complete and geographic shifting, permitted data centers can be filtered based on regional data governance laws or which GPU SKU's are available. 

<br>

<a name="Tool Validation"></a>

## Tool Validation

Carbon intensity data for validation provided by: [WattTime](https://www.watttime.org/)


### Data Granularity

**Details:** 
For the purpose of demand shifting, the effectiveness of using a carbon intensity baseline is compared against using a granular search. The baselines are the annual and monthly marginal emissions rate averages for respective regions, and the data granularities used are 1-hour and 5-minutes.     

| Years Evalulated | Specific Months Evaluated for Each Year  |
| :------------- | :---------- | 
| 2020 | January |
| 2021 | April |
|  | July |
|  | October |
 
*Working Data* 
* Using the [Historical Emissions](https://www.watttime.org/api-documentation/#historical-emissions) endpoint, CI data is reported at 5-minute intervals in month batches by default for each of these regions.   
* Monthly Average Baseline: Mean MOER over the calander month 
* Annual Average Baseline: Mean of *Monthly Average Baselines* 
* 1-Hour CI Reporting Granularity: Mean of aggregated MOER values from 5-minute interval . 

**Results**
*Validation in-progress*




<br>

### Search Sensitivity

**Details:**

**Results:**
*Validation in-progress*

<br>

For more information, please see: [Tool Validation](https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Documentation/Validation)

<br>

<a name="Case Studies"></a>

## Case Studies

Carbon intensity data for case studies provided by: [WattTime](https://www.watttime.org/)

### Demand Shifting at Scale of Organizational Operations 

**Details:** *Geographic shifting compute instances at scale would reduce carbon by X% over the month*

**Results:** *Analysis in-progress*

For more information, please see the full case study: [Demand Shifting at Scale of Organizational Operations](https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Documentation/Case%20Studies/Organizational_Shifting)

### Demand Shifting at Scale of Individual Users 

**Details:** *Individual users can reduce carbon by Y via time shifting.*

**Results:** *Analysis in-progress*

For more information, please see the full case study: [Demand Shifting at Scale of Individual Users](https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Documentation/Case%20Studies/Individual_Shifting)

### Bulk Workload Shifting for Data Centers

**Details:** *Shifting 1% of a data centers workload over a day would reduce overall emissions by Z.*

**Results:** *Analysis in-progress*



For more information, please see the full case study: [Bulk Workload Shifting for Data Centers](https://github.com/TaylorPrewitt/carbon-awareAPI/tree/main/Documentation/Case%20Studies/DataCenter_Shifting)

<br>

<a name="Tool Recommendations"></a>

## Recommendations

[GSF SCI Specification](https://github.com/Green-Software-Foundation/software_carbon_intensity/blob/main/Software_Carbon_Intensity/Software_Carbon_Intensity_Specification.md)
