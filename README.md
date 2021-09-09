# Carbon Aware API Project
<sup>*Draft, In Progress*</sup>

<a href="#Carbon Aware API">Overview</a><br>
<a href="#Tool Architecture">Architecture</a><br>
<a href="#Tool Methodology">Tool Methodology</a><br>
<a href="#Tool Validation">Tool Validation</a><br>
<a href="#Case Studies">Case Studies</a><br>
<a href="#Tool Recommendations">Recommendations</a><br>

## Terminology 
| Term | Definition   |
| :------------- | :---------- | 
| **Carbon Intensity** | Carbon per energy unit. |
| **Grid-based carbon intensity**   | All entities who operate on a shared electrical grid share a common emissions rate. | 
| **Carbon delta**   | The difference in emissions between carbon aware and unaware actions. | 
| **Carbon counterfactual**   | The *carbon delta* had the carbon aware action been different.| 

Other definitions for the Carbon Awareness found at: <br>
<a href = "https://github.com/Green-Software-Foundation/Dictionary/blob/dev/Dictionary/Dictionary.md">Green Software Foundation Dictionary</a>

<br><br>

<img width="1035" alt="mountain" src="https://user-images.githubusercontent.com/80305894/132602354-e0c41d0e-1a83-4fd8-a435-ba2332694d10.png">

<br>
<a name="Carbon Aware API"></a>

## Carbon Aware API

To enable organizations to make smart decisions about their environmental impact and carbon footprint, we have created the Carbon Aware API to minimize the carbon emissions of computational workflows. A few key features of the API are: 

* Utilizes marginal carbon emission from WattTime to identify carbon intensity per region 

* Generates a retrospective carbon emission analysis 

* Provides forecasted demand shifting suggestions 

* Supplies regional carbon intensity information over different scopes  

**Marginal Carbon Emissions:** This grid-responsive metric with finer granularity than average emissions, allows for seasonality/diurnal trends captured in demand shifting (source). 

**Retrospective Analysis:** Time series evaluation to assess the carbon emissions for a given energy profile. Also provides counterfactual analysis to expose the potential emissions of if the run had been shifted. 

**Demand Shifting**: Recommends region and/or time which would yield a less carbon intensive run.  

* Temporal: Identifies the window of minimum carbon intensity for a specified run duration within a chosen region from a 24-hour forecast.  

* Geographic: Finds the region with the current lowest average carbon intensity for an immediate run of a specified duration. Can filters available regions by available SKU and migration laws for workspaces with protected data.  

**Regional Carbon Intensity:** Provides the carbon intensity for each data center supported by a WattTime- tracked balancing authority.  The possible scopes are historic intensities (time series for prior 24-hours, week, and month), real-time marginal intensity, and forecast (mean intensity for upcoming user- defined window). 


<br>
<a name="Tool Architecture"></a>

## Architecture

*Diagram*
<br>
<sup>Diagram Images Coming Soon</sup>

[wsgi.py](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Carbon_Aware_API/wsgi.py)<br>
[utils.py](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Carbon_Aware_API/app/utils.py)<br>
[data.py](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Carbon_Aware_API/app/data.py)<br>
[ci_data.py](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Carbon_Aware_API/app/routes/ci_data.py)<br>
[shift.py](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Carbon_Aware_API/app/routes/shift.py)<br>



<br>
<a name="Tool Methodology"></a>

## Tool Methodology

**Retrospective Analysis**: By mapping grid-based marginal carbon intensity measurements to energy consumption profiles, the carbon footprint of cloud workloads is identified and evaluated.  Part of this evaluation is to find carbon counterfactual emissions of if carbon aware scheduling was used, reporting possible outcomes of temporal and geographic shifts.  


Given the following:
<br>
<img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;C_i&space;=&space;&space;\sum_{j=0}^{\left\|&space;\textbf{t}\right\|}&space;M_i(t_j)*E(t_j)&space;" title="\bg_white C_i = \sum_{j=0}^{\left\| \textbf{t}\right\|} M_i(t_j)*E(t_j) " />

Where:

* **t** = discrete time vector<br>
* M(t) = marginal operating emission rate (MOER) for a given region (i) at a certain point in time (j)<br>
* C<sub><i>i</i></sub> = carbon emitted for a given region and time window (C<sub><i>0</i></sub> is the result from the M(t) for when and where the run was executed)
* **C** = vector of carbon emissions resultant of different initial conditions for M(t) <br>

Using **C** the carbon couterfactuals can be identified because each value is the outcome of a different potential workload shift.    

**Demand Shifting**: Combining carbon intensity forecasts from a certified provider with anticipated workload constraints such as runtime, governance, and needed hardware, a green window can be found in the forecasted time span. 

Given the following:
<br>
<img src="https://latex.codecogs.com/png.image?\dpi{100}&space;\bg_white&space;CI_i&space;=&space;\frac{1}{\left\|&space;\textbf{t}\right\|}&space;\sum_{j=0}^{\left\|&space;\textbf{t}\right\|}&space;F_i(t_j)&space;" title="\bg_white CI_i = \frac{1}{\left\| \textbf{t}\right\|} \sum_{j=0}^{\left\| \textbf{t}\right\|} F_i(t_j) " />

Where:

* **t** = discrete time vector<br>
* F(t) = forecasted marginal operating emission rate (MOER) for a given region (i) at a certain point in time (j)<br>
* <span style="text-decoration:overline">CI</span><sub><i>i</i></sub> = mean forecasted carbon intensity for a given region and time window 
* **<span style="text-decoration:overline">CI</span>** = vector of mean forecasted carbon intensities  <br>

<img src="https://latex.codecogs.com/png.image?\dpi{110}&space;\bg_white&space;G&space;=&space;argmin(\textbf{CI})" title="\bg_white G = argmin(\textbf{CI})" />

The green suggestion (G) is the time period in the forcast span at a specific data center that yields the minimum mean forecasted carbon intensity. The goal of the Carbon Aware API is to find which start time (t<sub>0</sub>) and/or location that would result in the least carbon to be emitted.  

For each permitted data center all possible windows in the forecast span are searched to find the lowest average emitter. 
* Time-shifting: no data center variation permitted. Sliding search to find best start time for the green window.
* Geographic-shifting: no start time variation. Evaluates permitted data centers to find the greenest location for an immediate start.
* Complete Shifting: data center and start time variation. Sliding search to find best start time for the green window across all permitted data centers. 

For complete and geographic shifting, permitted data centers can be filtered based on regional data governance laws or which GPU SKU's are available. 
<br>
<a name="Tool Validation"></a>

## Tool Validation

#### Methodolgy 

#### Results

<br>
<a name="Case Studies"></a>

## Case Studies

#### Demand Shifting at Scale of Organizational Operations 

Details:

Results:

#### Demand Shifting at Scale of Individual Users 

Details:

Results:

#### Bulk Workload Shifting for Data Centers

Details:

Results:


<br>
<a name="Tool Recommendations"></a>

## Recommendations
