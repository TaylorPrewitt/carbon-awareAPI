import React from 'react';
import './Monitor.css'
import '../DocumentationContent.css'
import splitImg from '../../../../img/split.png'

const Monitor = () => {

    return(    
        <div className="doc">
            <div className="doc-content">
                <div className="xs-extra-space">
                    <br />
                </div> 

                <div className="body">
                    <h1 className="mt-5 doc-title">Retrieving Data from Azure Monitor</h1>

                    <h3 className="mt-5">Direct Monitor Download Through Azure Portal</h3>

                    <h4 className="mt-5">Getting to the Azure Monitor</h4>
                    <ol type = '1'>
                        <li>Click the 
                            <img className="logo2" src="https://upload.wikimedia.org/wikipedia/commons/a/a8/Microsoft_Azure_Logo.svg"></img> 
                            Logo at the top right of the screen or independently navigate to: <a href="https://azure.microsoft.com/en-us/">https://azure.microsoft.com/en-us/</a>
                        </li>
                        <li>  Login to your Portal</li>
                        <li>  In the “Azure services” selection menu, choose “Monitor” </li>
                        <li> In the navigation menu on the left, choose “Metrics”</li>
                        <ol type ='a'>
                            <li> If this menu is not available, click the >> icon under “Monitor|Overview”</li>
                        </ol>
                    </ol>

                    <h4>Finding your resource</h4>
                    <ol>
                        <li>Create scope:</li>  
                        <li> Select the <i>resource group</i> associated to the ML runs</li>
                        <li>Refine scope:</li>
                        <ol type ='i'>
                            <li>Select a esource typer, ex: “Machine Learning”</li>
                            <li>Select the location of the Azure region the workspace is associated to: ex “East US 2”</li>
                            <li>Select the resource: ex “ML_Workspace_Name”</li>
                            <li>Apply selections</li>
                        </ol>
                    </ol>

                    <h4>Aggregate GPU Energy Data</h4>
                    <ol>
                        <li>Define Scope:</li>
                        <ol type ='a'>
                            <li> Select the metric “GpuEnergyJoules”</li>
                            <li> Select the aggregation “Sum”</li>
                        </ol>
                        <li>Change granularity:</li>
                        <ol type ='a'>
                            <li> Click icon at the top right of the plot region that displays granularity information</li>
                            <ol type ='i'>
                                <li>By default, this is set to: “Local Time: Last 24 hours (Automatic)”</li>
                            </ol>
                            <li>In the Time granularity dropdown, select “5 minutes”</li>
                            <li>In the Time range selection, select “Custom”</li>
                                <ol type ='i'>
                                    <li>Enter Start and End times for run</li>
                                </ol>
                            <li>Apply changes</li>
                        </ol>
                    </ol>

                    <h4>Download the Data </h4>
                    <ol>
                        <li>In the “Share” dropdown, select download to excel file to get a .xlsx</li>
                        <p>File is ready to be uploaded into API for Carbon emission evaluation.</p>
                    </ol>

                    <div className="xs-extra-space">
                        <br />
                    </div> 

                    <h3>Data Retrieval via Response from API Request</h3>

                    <ol type = '1'>
                        <li>Login to Azure via Azure CLI</li>
                        {/* <!-- Command Line --> */}
                        <div className="python">
                            <p className="white">>> az login</p>
                        </div>
                        <li>Construct your resource URI</li>
                        <ol type ='a'>
                            <li>  subID: Azure subscription ID</li>
                            <li>resourceGroup: The Azure resource group responsible for the computation</li>
                            <li> providerService: The service provider and description</li>
                            <ol type ='i'>
                                <li>ex:Microsoft.MachineLearningServices</li>
                            </ol>
                            <li>workspace: The location of the computation</li>
                    </ol>

                    {/* <!-- Misc. --> */}
                    <div className="python">
                        <p className="white">/subscriptions/&#123;subID&#125;/resourceGroups/&#123;resourceGroup&#125;/providers/&#123;providerService&#125;/workspaces/&#123;workspace&#125;</p>
                    </div>

                    <li>Construct a request URL</li>
                    <ol type ='a'>
                        <li> Time Span needs to be entered as two ISO formatted time stamps with a ‘/’ separator</li>
                        <ol type ='i'>
                                <li>2021-05-1T19:30:00.000Z/2021-05-1T22:30:00.000Z</li>
                        </ol>
                    </ol>

                    {/* <!-- Misc. --> */}
                    <div className="python">
                        <p className="white">https://management.azure.com/&#123;resourceUri&#125;/providers/microsoft.insights/metrics?api-version=2018-01-01&#38;metricnames=GpuEnergyJoules&#38;interval=PT5M&amp;timespan=&#123;timespan&#125;&aggregation=total</p>
                    </div>

                    <li> Acquire an access token</li>
                    <ol type ='a'>
                        <li>  Use the following CLI command to get your bearer “accessToken”</li>
                        {/* <!-- Command Line --> */}
                        <div className="python">
                            <p className="white">>> az account get-access-token --subscription &#123;subID&#125;</p>
                        </div>
                        <li> Then use it to create an API request authorization header</li>
                        {/* <!-- Python --> */}
                        <div className="python">
                            <p className="white">headers = &#123;<span className="orange">'Authorization'</span>: <span className="orange">'Bearer</span><span className="blue-python"> {}</span><span className="orange">'</span>.format(accessToken)&#125;</p>
                        </div>
                    </ol>

                    <li>Send the data request to Azure Monitor</li>
                    {/* <!-- Python --> */}
                    <div className="python">
                        <p className="white">requests.get(request_URL, <span className="l-blue">headers</span>=headers)</p>
                    </div>

                    <li> Convert the get response string to a dictionary and then save as a .json</li>

                    {/* <!-- Python --> */}
                    <div className="python">
                        <p className="white"><span className="pink">with</span> <span className="yellow">open</span>(<span className="orange">"'ML_energy_profile.json"</span>, <span className="orange">"w"</span>) <span className="pink">as</span> outfile:</p>
                        <p className="white">  &emsp;&emsp;&emsp;&emsp;  json.dump(response_dict, outfile)</p>
                    </div>
                    <br />
                    <p>File is ready to be uploaded into the API for Carbon emission evaluation.</p>
                    <br />
                    </ol>
                    <p>Further Support: 
                        <a href="https://docs.microsoft.com/en-us/rest/api/monitor/">Azure Monitor Overview</a> 
                        and with <a href="https://docs.microsoft.com/en-us/rest/api/monitor/metricdefinitions/list">Metric Definitions - List</a>
                    </p>
                </div>

                <div className="xs-extra-space">
                        <br />
                </div>
            </div> 
        </div>
    );
}

export default Monitor; 