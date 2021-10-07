# File Download Instructions 

## Accessing Azure Monitor UI
1. Navigate to: https://azure.microsoft.com/en-us/
2. Login to your Portal
3. In the search bar at the top center, search "Monitor"
4. In the top left under the 'Overview' title, search "Metrics" in the search bar
    1. If this menu is not available, click the >> icon under “Monitor|Overview”
5. Select Metrics


## Define Resource Scope
1. Click the checkbox next to the subscription which contains the workspace which hosted the compute
    1. If this subscription is not visible, select it in the subscription dropdown and then select for the scope
2. Select the resource type 'Machine Learning' in the 'Resource Type' drop down menu.
3. Select the workspace that executed the compute in the 'Machine Learning' drop down menu to specify the exact resource used.
    1. Selecting this will auto populate the Location
4. Click apply


## Set Evaluation Metric
1. 'Scope' and 'Metric Namespace' will auto populate
2. Select "GpuEnergyJoules" in the 'Metric' drop down.
3. 'Aggregation' should then default to 'Sum', but if not, select this.


## Define Granularity
1. In the top right click the Time icon
2. Select "5 minutes" for 'Time granularity' in the dropdown
3. Define the start and end times, round to the nearest 5 min times which fully encapsulate the compute.
    1. *Note, this will be all runs from workspace during this time window*
4. Click apply


## Filtering Metric Output (optional)
1. Click 'Add filter'
2. Select a 'Property' to filter on, such as "RunId"
3. Using this and selecting a specific run(s) under 'Values' can limit the energy profile to specific instances


## Downloading Data
1. Click the 'Share' button at the top right of the plot​
2. Click 'Click Download to Excel'

