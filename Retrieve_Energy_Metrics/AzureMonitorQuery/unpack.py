import json
import pandas as pd


# enter the details used in query.py
    # subscription name and the resource group desired for this unpack
        # this unpacks all workspaces from 1 resource group
sub_name = ''
resourceGroup = ''

# list of workspaces to identify all files
    # this should be the same list submitted in query.py
workspace_list = ['',]


def get_data(workspace_name, resourceGroup):
    '''
    Parameters
    ----------
    workspace_name : string
        name of the workspace that hosted the run.
    resourceGroup : string
        name of the resource group that houses the run's workspace.

    Returns
    -------
    df : DataFrame
        dataframe of a run's energy profile, grouped and summed over devices.

    '''
    
    # load data in as dictionary
    dictionary = json.load(open(f"energy_profile_{sub_name}_{resourceGroup}_{workspace_name}.json"))
    
    # break data up and grab only needed components
    data_list = []
    for n in range(len(dictionary['value'][0]['timeseries'])):
        for i in range(len(dictionary['value'][0]['timeseries'][n]['data'])):
            timestamp = dictionary['value'][0]['timeseries'][n]['data'][i]['timeStamp']
            total = dictionary['value'][0]['timeseries'][n]['data'][i]['total']
            runid = dictionary['value'][0]['timeseries'][n]['metadatavalues'][1]['value']
            data_list.append({'timestamp':timestamp, 'total':total, 'runid':runid})
    
    # format into dataframe summed over devices 
    df = pd.DataFrame(data_list)
    df = df.groupby(['timestamp','runid'], as_index=False).sum()
    df['workspace'] = workspace_name
    df = df.sort_values(['runid', 'timestamp'], ascending=True)
    
    return df



def make_key_data(workspace_list, resourceGroup):
    '''
    Parameters
    ----------
    workspace_list : list
        all workspaces submited in query.py to return Az Monitor data..

    Returns
    -------
    metadata_list : list
        list to be used as key for data dataframes.
        maps runid to metadata (resource region and workspace name)

    '''
    
    metadata_list = []
    for workspace_name in workspace_list:
        dictionary = json.load(open(f"energy_profile_{sub_name}_{resourceGroup}_{workspace_name}.json"))
        region = dictionary['resourceregion']
        run_id_list = []
        
        for i in range(len(dictionary['value'][0]['timeseries'])):
            runid = dictionary['value'][0]['timeseries'][i]['metadatavalues'][1]['value']
            if runid not in run_id_list:
                run_id_list.append(runid)
                
        for run in run_id_list:
            metadata_list.append({'runid':run, 'metadata':{'region':region, 'workspace':workspace_name}})
            
    return metadata_list



def make_two_dataframes(workspace_list, resourceGroup):
    '''
    makes a dataframe of for all data. split on runsid and tagged with workspace
        sorts to group run time spans together
    
    Parameters
    ----------
    workspace_list : list
        all workspaces submited in query.py to return Az Monitor data.

    Returns
    -------
    all_run_dataframe : DataFrame
        single tabluated dataframe of all runs. 
        runs listed consecutively 
        each time interval is tagged with its runid and workspace
    multi_index_dataframe : Multi Index DataFrame
        timestamps in UTC ISO as row index.
        ['total', 'runid'] as column index.
        each column is an energy profile for the labeled run over the time span
        each value is the Joules consumed per 5 minute interval.

    '''
    all_run_dataframe = pd.DataFrame()
    for workspace in workspace_list:
        df = get_data(workspace, resourceGroup)
        all_run_dataframe = all_run_dataframe.append(df)
    multi_index_dataframe = all_run_dataframe.set_index(['timestamp', 'runid']).unstack(['runid'])
    multi_index_dataframe = multi_index_dataframe.drop('workspace', axis = 1)
        
    return all_run_dataframe, multi_index_dataframe



# execute function to make metadata key for the unpacked data
metadata_list = make_key_data(workspace_list, resourceGroup)



# build dataframes from unpacked data.  one multi-index the other is single level
all_run_dataframe, multi_index_dataframe = make_two_dataframes(workspace_list, resourceGroup)


# storing unique runid's
runid_name_index = all_run_dataframe.groupby('runid').sum()
runid_name_index = runid_name_index.reset_index()
runid_name_index = runid_name_index.drop('total', axis=1)
runid_name_index.to_csv('runid_name_index.csv')

# storing metadata list to json file
with open("metadata.json", 'w') as fp:     
    json.dump(metadata_list, fp)

# storing dataframes to files
all_run_dataframe.to_csv('all_run_data.csv')
multi_index_dataframe.to_hdf('multi_index.h5', 'runid')
