import React from 'react';
import './ApiUse.css'

const ApiUse = () => {

    return(    
        <div className="doc">
            <div className="doc-content">
                <div className="xs-extra-space">
                    <br />
                </div> 

                <div className="body">
                    <h1 className="mt-5 doc-title">Carbon API Report</h1>
                    <p className="mt-3"><strong><em>Graduate Students</em></strong> - <em>Taylor Prewitt, Shivang Dalal, Amruta Jadhav, Thet Noe, Maxwell Weil</em></p>
                    <p><strong><em>Undergraduate Students</em></strong> - <em>Larry Tian, Kevin Yip, Maynard Maynard-Zhang, Divij Satija</em></p>

                    <h2 className="mt-3">Introduction</h2>
                    <p>
                        In this report, our team explains the front and back end work of our current Carbon API design. 
                        We discuss the various information provided through each route and page, as well as a general 
                        idea of how each element connects to others. We hope that this paperserves as a relatively 
                        straightforward method for understanding the different aspects that our API has to offer.
                    </p>

                    <h2 id="routes" className="mt-3">Contents</h2>
                    <ul>
                        <li><a href="#routes">Routes</a></li>
                        <li><a href="#htmlPages">HTML Pages</a></li>
                        <li><a href="#functionsUsed">Functions Used</a></li>
                    </ul>
                    
                    <h2 id="login" className="mt-3">Routes</h2>
                    <h4 id="home">/login</h4>
                    <p>Front page of API. Requests credentials from the user to allow access to the rest of the API using the <a href="#auth_required">auth_required</a> function. WattTime licensed login information is automatically provided during searching using <a href="#get_token">get_token</a>, so initial credentials are necessary to protect this from unauthenticated users. Upon successful login, redirects to <a href="#home">/home</a>.</p>
                    <h4 id="docs_page">/home</h4>
                    <p>Home page for API displayed by <a href="#starthtml">start.html</a>. Provides basic background information and description of the project. Contains links to <a href="#home">/docs_page</a> and <a href="#protected">/protected</a>.</p>
                    <h4 id="swagger">/docs_page</h4>
                    <p>Documentation page displayed by <a href="#ba_errorhtml">docs_page.html</a>. Contains external links to <u><a href="https://github.com/TeamAPI-2021">GitHub repository</a></u> with relevant code and <u><a href="https://miro.com/app/board/o9J_lPfzVuM=/">Miro board</a></u> outlining the flow diagram. Also links to Swagger documentation stored at <a href="#swagger">/swagger</a>.</p>
                    <h4 id="protected">/swagger</h4>
                    <p>Swagger documentation built with the OpenAPI Swagger UI schematic. This page allows for testing of routes using various HTTP methods. Provides descriptions of routes, parameters, and outputs.</p>
                    <h4 id="getloc">/protected</h4>
                    <p>Search page for obtaining Azure region specific WattTime information. Displayed by <a href="#htmlPages">az_find.html</a>. Allows users to obtain carbon emissions data for a region using either an Azure region name, a known location (given by geocoordinates), or a WattTime balancing authority name. Each search method redirects to a different route to determine which WattTime region carbon emissions data should be drawn from. Can redirect to <a href="#getloc">/getloc</a>, <a href="#get_region">/get_region</a>, or <a href="#from_ba">/from_ba</a>.</p>
                    <h4 id="get_region">/getloc</h4>
                    <p>Route that takes in an Azure region name and finds the corresponding WattTime balancing authority. A drop-down menu is provided with a list of Azure regions. Azure regions without an associated WattTime authority returns <a href="#htmlPages">az_error.html</a>. Upon successful association, redirects to <a href="#chooser">/chooser</a>.</p>
                    <h4 id="from_ba">/get_region</h4>
                    <p>Route that takes in decimal form geocoordinates (latitude and longitude) and finds the nearest Azure region and corresponding WattTime balancing authority. Geocoordinates outside of WattTime balancing authority boundaries will return <a href="#loc_errorhtml">loc_error.html</a>, requesting
                    the user to provide a different location. Upon successful association, redirects to <a href="#chooser">/chooser</a>.</p>
                    <h4 id="chooser">/from_ba</h4>
                    <p>Route that takes in a WattTime balancing authority and finds the corresponding Azure region. A drop-down menu is provided to only accept valid WattTime balancing 
                    authority names. If there is no Azure region in the chosen balancing authority, the page will return
                    <a href="#az_findhtml">ba_error.html</a>. Upon successful association, redirects to <a href="#chooser">/chooser</a>.</p>
                    <h4 id="get_grid_data">/chooser</h4>
                    <p>Data searching page displayed by <a href="#ba_errorhtml">datachoice.html</a>. Provides selected WattTime balancing authority and Azure region information so users can see where they will be pulling data from. Also gives overview of different data types that can be chosen. Upon inputting a given data type from the drop-down 
                    menu as well as start and end times, will
                    redirect to either <a href="#get_grid_data">/get_grid_data</a>, <a href="#get_index_data">/get_index_data</a>, <a href="#get_historical_data">/get_historical_data</a>, or <a href="#get_forecast_data">/get_forecast_data</a> depending on data type. Note that times are currently accepted in <em>MM-DD-YYYY HH:MM AM/PM TZ</em> or <em>HH:MM AM/PM TZ MM-DD-YYYY</em> formats, where TZ is the timezone abbreviation (PST or PT for Pacific timezone, EST or ET for Eastern timezone, etc.). Improperly entered data will return <a href="#data_errorhtml">data_error.html</a>.</p>
                    <h4 id="get_index_data">/get_grid_data</h4>
                    <p>Obtains historical marginal emissions data from WattTime balancing authority of interest over a given time period. Returned in JSON format. Additional WattTime documentation for grid data can be found externally <u><a href="https://www.watttime.org/api-documentation/#grid-data">here</a></u>.</p>
                    <h4 id="get_historical_data">/get_index_data</h4>
                    <p>Obtains real-time emissions data from WattTime balancing authority of interest over a given time period. Returned in JSON format. WattTime documentation for real-time emissions data can be found externally <u><a href="https://www.watttime.org/api-documentation/#realtime-emissions">here</a></u>.</p>
                    <h4 id="get_forecast_data">/get_historical_data</h4>
                    <p>Obtains historical marginal emissions data from WattTime balancing authority of interest for (up to) the past two years. Returned as a zip file. WattTime documentation for historical data can be found externally <u><a href="https://www.watttime.org/api-documentation/#historical-emissions">here</a></u>.</p>
                    <h4 id="htmlPages">/get_forecast_data</h4>
                    <p>Obtains historical forecasted marginal emissions data from WattTime balancing authority of interest from a given time period. If no time period is provided, then 
                    the most recent forecasted data is returned. Returned in JSON format. WattTime documentation
                    for forecasted emissions data can be found externally <u><a href="https://www.watttime.org/api-documentation/#marginal-emissions-forecast">here</a></u>.</p>

                    <h2 id="az_errorhtml" className="mt-5">HTML Pages</h2>
                    <h4 id="az_findhtml">az_error.html</h4>
                    <p>404 error page that is triggered if a chosen Azure region has no associated WattTime balancing authority in <a href="#getloc">/getloc</a>.</p>
                    <h4 id="ba_errorhtml">az_find.html</h4>
                    <p>Page for displaying the region searching information from <a href="#protected">/protected</a>.</p>
                    <h4 id="datachoicehtml">ba_error.html</h4>
                    <p>404 error page that is triggered if a chosen WattTime balancing authority has no associated Azure region in <a href="#from_ba">/from_ba</a>.</p>
                    <h4 id="docs_pagehtml">datachoice.html</h4>
                    <p>Page for displaying the data information from <a href="#chooser">/chooser</a>.</p>
                    <h4 id="loc_errorhtml">docs_page.html</h4>
                    <p>Page for displaying documentation links from <a href="#home">/docs_page</a>.</p>
                    <h4>loc_error.html</h4>
                    <p>404 error page that is triggered if geocoordinates given to <a href="#get_region">/get_region</a> result in an Azure region with no associated WattTime balancing 
                    authority.</p>
                    <h4 id="starthtml">miro.html</h4>
                    <p>Contains an embedded version of the Miro board flow diagram and team process.</p>
                    <h4 id="data_errorhtml">start.html</h4>
                    <p>Page for displaying the information from <a href="#home">/home</a>.</p>
                    <h4 id="functionsUsed">data_error.html</h4>
                    <p>404 error page that is triggered if data search parameters are incorrect. This can happen for a number of reasons, such as when start/end time is not provided, if the end time is before the start time, or if the data is not available from WattTime.</p>

                    <h2 id="auth_required" className="mt-5">Functions Used</h2>
                    <h4 id="get_token">auth_required</h4>
                    <p>Basic login functionality to prevent API access from unauthorized users. Used in <a href="#routes">/login</a> for initial access to API home page.</p>
                    <h4 id="user_distance_to_az">get_token</h4>
                    <p>Obtains privileged WattTime login information from stored JSON file. Called when access to WattTime is needed to prevent 30 minute timeout. Used in <a href="#getloc">/getloc</a>, <a href="#get_grid_data">/get_grid_data</a>, <a href="#get_index_data">/get_index_data</a>, <a href="#get_historical_data">/get_historical_data</a>, and <a href="#get_forecast_data">/get_forecast_data</a>.</p>
                    <h4 id="nearest_az_region">user_distance_to_az</h4>
                    <p>Determines the distance between two sets of geocoordinates using the <u><a href="https://en.wikipedia.org/wiki/Haversine_formula">Haversine formula</a></u> (links externally). Is called by <a href="#nearest_az_region">nearest_az_region</a>.</p>
                    <h4>nearest_az_region</h4>
                    <p>Finds the nearest Azure region data center for a given set of geocoordinates. Uses Azure region location information given from the Azure CLI command:</p>        
                    <p><code>az account list-locations</code></p>
                    <p>Calls <a href="#user_distance_to_az">user_distance_to_az</a> to find distance from user to all Azure region locations, and returns the closest one. Used in <a href="#get_region">/get_region</a>.</p>
                </div>  

                <div className="xs-extra-space">
                    <br />
                </div>     
            </div>
        </div>
    );
}

export default ApiUse; 