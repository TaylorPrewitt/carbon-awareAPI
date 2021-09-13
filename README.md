# Carbon Aware API Project
<sup>*Draft, In Progress*</sup>


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
| **Carbon Intensity** | Carbon per energy unit. |
| **Grid-based carbon intensity**   | All entities who operate on a shared electrical grid share a common emissions rate. | 
| **Carbon delta**   | The difference in emissions between carbon aware and unaware actions. | 
| **Carbon counterfactual**   | The *carbon delta* had the carbon aware action been different.| 

Other definitions for the Carbon Awareness found at: <br>
<a href = "https://github.com/Green-Software-Foundation/Dictionary/blob/dev/Dictionary/Dictionary.md">Green Software Foundation Dictionary</a>

<br><br>


![Banner](https://user-images.githubusercontent.com/80305894/132620015-b0a5007a-d605-43ca-a260-8b3bc5206b32.png)
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

![Slide1](https://user-images.githubusercontent.com/80305894/133138401-b520a104-be79-43fe-86d0-8cc8e32e801f.jpg)

![Slide2](https://user-images.githubusercontent.com/80305894/133138404-7fb91783-8bcd-4ae4-a52f-aaae3eda954a.jpg)

![Slide3](https://user-images.githubusercontent.com/80305894/133138405-820c00aa-d154-46fa-862b-40478315f393.jpg)

![Slide4](https://user-images.githubusercontent.com/80305894/133138409-a922dfd8-50ac-40f4-961a-ac9081ac3408.jpg)





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
* E(t) = energy consumed per time interval
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

Methodolgy 

Results

<br>

<a name="Case Studies"></a>

## Case Studies

#### Demand Shifting at Scale of Organizational Operations 

Details: *Geographic shifting compute instances at scale would reduce carbon by X% over the month*

Results:

#### Demand Shifting at Scale of Individual Users 

Details: *Individual users can reduce carbon by Y via time shifting.*

Results:

#### Bulk Workload Shifting for Data Centers

Details: *Shifting 1% of a data centers workload over a day would reduce overall emissions by Z.*

Results:


<br>

<a name="Tool Recommendations"></a>

## Recommendations
