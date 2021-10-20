# Tool Methodology

## Sections

<ol>
  <li><a href="#RetrospectiveAnalysis">Retrospective Analysis</a></li>
  <li><a href="#DemandShiftingScheduler">Demand Shifting Scheduler</a></li>
  <li><a href="#GreenRegionPicker">Green Region Picker</a></li>
</ol>

<br>

<a name="RetrospectiveAnalysis"></a>

## Retrospective Analysis
By mapping grid-based marginal carbon intensity measurements to energy consumption profiles, the carbon footprint of cloud workloads is identified and evaluated.  Part of this evaluation is to find carbon counterfactual emissions of if carbon aware scheduling was used, reporting possible outcomes of temporal and geographic shifts.  



Given the following:
<br>

![CodeCogsEqn (1)](https://user-images.githubusercontent.com/80305894/133733435-c8532304-3a4a-4140-9dbd-cc449758f423.png)

Where:

* **t** = discrete time vector<br>
* M(t) = marginal operating emission rate (MOER) for a given region (i) at a certain point in time (j) for J number of timestamps.<br>
* E(t) = energy consumed per time interval
* C<sub><i>i</i></sub> = carbon emitted for a given region and time window (C<sub><i>0</i></sub> is the result from the M(t) for when and where the run was executed)
* **C** = vector of carbon emissions resultant of different initial conditions for M(t) <br>

Using **C** the carbon couterfactuals can be identified because each value is the outcome of a different potential workload shift. 

<br><br>


<a name="DemandShiftingScheduler"></a>

## Demand Shifting
Combining carbon intensity forecasts from a certified provider, with anticipated workload constraints such as runtime, governance, and needed hardware, a green window can be found in the forecasted time span. 



<br>

### Temporal Shifting
The start time (t<sub>0</sub>) is allowed to vary conducting a sliding search to find best start time for the green window in the time span. 
the best window in the searched span is defined by:

![CodeCogsEqn (11)](https://user-images.githubusercontent.com/80305894/138178628-18e09a6a-d67a-4f4a-81a7-6abf852f5122.png)

* **t** = discrete time vector<br>
* F(t) = forecasted marginal operating emission rate (MOER) for a possible shift (k) at a certain point in time (j) for J number of timestampes.<br>
* ∆t = duration between point times, defined by the granularity of source.  
* <span style="text-decoration:overline">CI</span><sub><i>k</i></sub> = mean forecasted carbon intensity for a given region and time window 
* **<span style="text-decoration:overline">CI</span>** = vector of mean forecasted carbon intensities   

Where k is defined by the following:<br>
![CodeCogsEqn (16)](https://user-images.githubusercontent.com/80305894/138184564-b3fd6516-8a04-4320-8940-41fe9c44989f.png)


This is slides over the next 24 hours of forecast data looking for at each possible start time to determine the best point time.  Once the all values of k have been tested, the best start time is determined with the following:

![CodeCogsEqn (17)](https://user-images.githubusercontent.com/80305894/138184717-8a0dca3a-c4c9-48b2-9d7a-34cfdcb92d3c.png)


The best window and green suggestion (G) is the start time (t<sub>0</sub> + k∆t) that would result in the least carbon to be emitted.  


<br>

### Geograpic Shifting 
to determine data center eligibility, locations can be intially filtered by regional data governance laws and resource availability. 

The best eligible region is then determined using the following:

![CodeCogsEqn (14)](https://user-images.githubusercontent.com/80305894/138180056-defd0fa3-f2a9-420b-adb2-5eed13acd577.png)

* **t** = discrete time vector<br>
* F(t) = forecasted marginal operating emission rate (MOER) for a given region (i) at a certain point in time (j) for J number of timestampes.<br>
* <span style="text-decoration:overline">CI</span><sub><i>i</i></sub> = mean forecasted carbon intensity for a given region and time window 
* **<span style="text-decoration:overline">CI</span>** = vector of mean forecasted carbon intensities  <br>

<br>

Having a vector of expected mean carbon intesities over the upcoming window, each potential shift is rated to incorporate other metrics into data center selection

![CodeCogsEqn (9)](https://user-images.githubusercontent.com/80305894/138165359-6dd5adad-41c5-4a0b-8f89-206f4be4dd82.png)


* R<sub>i</sub> : Rating of the desirability for data center (i).
* W<sub>n</sub> : Input value used to weight the metric importance to the workspace. Default is optimized to reduce operational emissions (W<sub>1</sub>=1, W<sub>2</sub>=0, W<sub>3</sub>=0). <br>
* I<sub><i>i</i></sub> : Grid self-rating that describes the real-time marginal emissions at data center (i) relative to the last 2 weeks of its history. <br>
* I<sub>max</sub> : Maximum grid self-rating amongst all eligible data centers. <br>
* CI<sub><i>i</i></sub> : Mean marginal operating emissions rate of the grid at data center (i) over the input duration.<br>
* CI<sub>max</sub> : Maximum mean marginal operating emissions rate amongst all eligible data centers.<br>
* P<sub><i>i</i></sub> : Price of the service at data center (i). <br>
* P<sub>max</sub> : Maximum price of the service out of all eligible data centers.<br>
* L<sub><i>i</i></sub> : Round trip latency between current data center and data center (i). <br>
* L<sub>max</sub> : Maximum round trip latency between current data center and all eligible data centers.<br>





For complete and geographic shifting, permitted data centers can be filtered based on regional data governance laws or which GPU SKU's are available. 



<br><br>

<a name="GreenRegionPicker"></a>

## Green Region Picker
Entering a desired cloud service provider to define a list of eligible data centers, the green region picker will choose the grid with the best marginal carbon intensity efficiency, price rate, and latency. 

Each eligible data center is rated by the following: 

![CodeCogsEqn (6)](https://user-images.githubusercontent.com/80305894/138162105-de1b3289-eaa9-4b12-a9d2-ef312140ce79.png)


* R<sub>i</sub> : Rating of the desirability for data center (i).
* W<sub>n</sub> : Input value used to weight the metric importance to the workspace.<br>
* C<sub><i>i</i></sub> : Mean marginal operating emissions rate of the grid at data center (i) over the input duration.<br>
* C<sub>max</sub> : Maximum mean marginal operating emissions rate amongst all eligible data centers.<br>
* P<sub><i>i</i></sub> : Price of the service at data center (i). <br>
* P<sub>max</sub> : Maximum price of the service out of all eligible data centers.<br>
* L<sub><i>i</i></sub> : Round trip latency between current data center and data center (i). <br>
* L<sub>max</sub> : Maximum round trip latency between current data center and all eligible data centers.<br>



