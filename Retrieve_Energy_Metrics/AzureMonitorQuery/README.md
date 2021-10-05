# Azure Monitor

To retrieve energy consumption metrics via Azure Monitor, please follow the below steps:<br>
<ol>
  <li><a href="#Install Required Modules">Install Required Modules</a></li>
  <li><a href="#Login to the Azure SDK">Login to the Azure SDK</a></li>
  <li><a href="#Change Working Directory">Change Working Directory</a></li>
  <li><a href="#Open query.py and Define Parameters">Open query.py and Define Parameters</a></li>
  <li><a href="#Submit the Query">Submit the Query</a></li>
  <li><a href="#Open unpack.py and Define Parameters">Open unpack.py and Define Parameters</a></li>
  <li><a href="#Run the Script">Run the Script</a></li>
</ol>
<br>

<a name="Install Required Modules"></a>

## Install Required Modules
These modules are not included as part of the python standard library and are needed to execute the script to retrieve energy metrics:
1. [requests](https://docs.python-requests.org/en/latest)
2. [pandas](https://pandas.pydata.org/pandas-docs/stable/index.html)

To install them, run the following in the command line. 
`pip install <module name>` 
<br><br>

<a name="Login to the Azure SDK"></a>

## Login to the Azure SDK
Run `az login` in the terminal to login and use Azure CLI.

<sup><i>If not currently logged in, this should open a browser page to login into Azure. If not logged in and no browser page opens, navigate to https://aka.ms/devicelogin. For additional support, see https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli</i></sup>
<br><br>

<a name="Change Working Directory"></a>

## Change Working Directory 
For organization of the returned files, it is recommended to run query.py within the folder AzureMonitorQuery. <br>
i.e. `cd <path>\AzureMonitorQuery`      
<br>

<a name="Open query.py and Define Parameters"></a>

## Open query.py and Define Parameters 
<sup><i>This will query multiple resource groups and workspaces for a single subscription.</i></sup><br><br>
Within the [query.py](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Retrieve_Energy_Metrics/AzureMonitorQuery/query.py), enter the following parameters in the spaces provided:
1. Subscription Name 
2. Subscription ID
    1. 32-digit identifier 
3. Timespan
    1. Start and end timestamps for the query period in UTC ISO format.
          * e.g. YYYY-mm-ddTHH:MM:SS.000Z 
    2. Query range is limited to 30-days of run history
4. Resource Group(s)
    1. List of the resource group(s) which you would like to pull data for.
5. Workspace(s)
    1. Names of all workspaces listed across all resource groups of the query.
<br><br>

<a name="Submit the Query"></a>

## Submit the Query
With an active az login and the 5 query parameters defined, the query is ready to submit by running the script.  The query will save files within the working directory with the naming convention of: energy_profile_{sub_name}_{resourceGroup}_{workspace}.json

Each of these is JSON file which contains data for a given workspace with energy metrics split on 'runid' and 'deviceid'. 
<br><br>

<a name="Open unpack.py and Define Parameters"></a>

## Open unpack.py and Define Parameters
<sup><i>This will unpack JSON files from all workspaces queried for a given resource group and subscription.</i></sup><br><br>
Within the unpack.py, enter the following parameters in the spaces provided:
1. Subscription Name 
2. Resource Group
3. Workspace(s)
    1. Listed names of all workspaces queried within a specific Resource Group.
<br><br>
<a name="Run the Script"></a>

## Run the Script
Once the 3 parameters have been defined, [unpack.py](https://github.com/TaylorPrewitt/carbon-awareAPI/blob/main/Retrieve_Energy_Metrics/AzureMonitorQuery/unpack.py) is ready to run.  This will save the following as files with the given types:
1. all_run_data.csv
    1. All data in single index format, ordered and tagged by runid.
2. metadata.json
    1. Metadata for the queries. This maps runid to the region where the workspace is located and the deviceid's which performed the run.
3. multi_index.h5
    1. All data in a multi index format where each value is the Joules on energy consumed per 5 minute interval.
    2. Each value has an index of timstamp, runid, total

