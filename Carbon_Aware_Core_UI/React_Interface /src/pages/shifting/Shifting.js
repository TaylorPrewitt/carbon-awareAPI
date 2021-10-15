import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

// Error robot icon
import errorImg from '../../img/error.png'

// Tooltip library
import ReactTooltip from "react-tooltip";
import { BsFillQuestionCircleFill } from "react-icons/bs";

// Loading spinner library
import HashLoader from "react-spinners/HashLoader";
import { css } from "@emotion/react";

import shiftingImg from '../../img/shifting.png'
import splitImg from '../../img/split.png'

// library for scrolling animation
import { Animator, ScrollContainer, ScrollPage, batch, Fade, FadeIn, Move, MoveIn, MoveOut, Sticky, StickyIn, ZoomIn } from "react-scroll-motion";

import './Shifting.css'

const Shifting = () => {

    // Set up the states to decide what page to render
    const [display, setDisplay] = useState("");
    const [resultData, setResultData] = useState(undefined);
    const [loadingResult, setLoadingResult] = useState(false);

    // Change the loading spinner color
    const [loadColor, setLoadColor] = useState("#8EB93B");

    // Create FadeUp animation
    const FadeUp = batch(Fade(), Move(), Sticky());

    // Override css for Hash spinner loader
    const override = css`
        display: block;
        margin: 0 auto;
        border-color: red;
    `;

    // Onclick function when user submit the form
    const getResult = () => {
        // Change the content status to loading
        setLoadingResult(true);

        // fetch the data using "Post" and the form, store it
        fetch("https://azure-uw-cli-2021.azurewebsites.net/shift_predictions", { //
            method: "POST",
            body: new FormData(document.getElementById("shifting_form"))
        }).then(
            res => res.json()
        ).then(data => {
            setResultData(data)
            setLoadingResult(false);
            setDisplay("result");
        })
    }

    // Set the display to the starting page when user first opened the web
    useEffect(() => {
        setDisplay("");
    }, [])

    // Disable the form from posting when hit "submit"
    const handleSubmit = (event) => {
        event.preventDefault()
    }

    // Display page content based on the status
    let content = null;

    // If the page is loading
    if (loadingResult == true) {
        content = <div className="loading">
            {/* Add spacing */}
             <div className="extra-space">
                <br />
            </div> 
           
            {/* Display the Spinner and messages */}
            <HashLoader color={loadColor} css={override} size={150}/>
            <p className="loading-title">Trying to find the greenest start time</p>
            <p className="loading-desc">This might take a few seconds, a watched pot never boils!</p>
        </div>
    // If we are displaying the result 
    } else if (display == "result"){

        // Variable to store the result content 
        let result = null;

        // Create a function to check if the prediction is accepted
        let acceptButtonDisplay = <div>
            <div className="row btn-container mt-5 accept-button">
                <div className="col-sm-2 col-md-2 col-lg-2 col-xl-2">
                    {/* Set the display to the starting page */}
                    <button className="btn btn-secondary btn-default btn-lg" name="usage" onClick= {() => {
                        setDisplay("");
                    }}>Begin Another Search</button>
                </div>
                <div className="col-sm-2 col-md-2 col-lg-2 col-xl-2">
                    {/* Direct users to the 'thank you' page */}
                    <Link to="/accept"><button className="btn btn-success btn-default btn-lg" name="usage">Accept Suggestion</button></Link>
                </div>
            </div>
        </div>

        // If the data we fetched isn't null
        if (resultData != null) {
            // Error Page (fingers crossed this wont appear)
            if (resultData.type == "error") {
                // Store the error code and the error message
                const errorMsg = resultData.errorMessage
                const errorCode = resultData.errorCode

                // Display the error code and the error message
                result = <div className="error">
                    <div className="extra-space">
                        <br />
                    </div> 

                    <img className="error-img" src={errorImg} alt="error" />

                    <p className="error-title">Oops, something went wrong - {errorCode}</p>
                    <p className="error-desc">Please <strong>{errorMsg}</strong></p>

                    <div className="text-center mt-5">
                        {/* Button that will direct users back to the starting page */}
                        <button
                            className="btn-secondary btn btn-default btn-lg center" 
                            onClick= {() => {
                                setDisplay("");
                        }}>Back</button>
                    </div>
                </div>

            // Page with warning message
            } else if (resultData.type == "load_shift_eval_2.html") {
                // Store the warning message and the returned data
                const warningMsg = resultData.warningMessage 
                let returnData = resultData.returnData

                // Display the result using the stored data
                result = <div className="result">
                    {/* Add spacing */}
                    <div className="sm-extra-space">
                        <br />
                    </div> 

                    {/* Warning message */}
                    <center>

                        <div class="alert alert-warning" role="alert">
                            {warningMsg}
                        </div>
                        
                    </center> 

                    {/* Geo-Time shifting prediction results */}
                    <h1 className="mt-5 title text-center"><strong>Geo-Time Shifting Prediction Results</strong></h1>

                    <div className="row center center-display mt-5">
                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon-azure" src="https://databarracks.imgix.net/uploads/Logos/azure-logo.svg?w=200&q=90&auto=format&fit=crop&crop=faces,edges&fm=png" />
                            <h3 className="icon-title blue"><strong>Suggested Azure Region</strong></h3>
                            <h3 className="icon-desc">{returnData.min_moer_region}</h3>
                            <br />
                        </div>
        
                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon" src="https://image.flaticon.com/icons/png/512/99/99744.png" />
                            <h3 className="icon-title blue"><strong>Supporting Balancing Authority</strong></h3>
                            <h3 className="icon-desc">{returnData.shiftBA}</h3>
                            <br />
                        </div>
                    </div>
                    <h3 className="detail mt-5"><span className="blue"><strong>Starting Emissions:</strong></span> Reduced by <strong>{returnData.shift_perc}%</strong> if run workload shifted out of {returnData.inputRegion}</h3>

                    {acceptButtonDisplay}

                    <div className="extra-space">
                        <br />
                    </div> 
                </div>

            // Geotime page 
            } else if (resultData.type == "load_shift_eval_geotime.html") {
                // Store the returned data
                let returnData = resultData.returnData

                // Display the result using the stored data
                result = <div className="result">
                    <div className="sm-extra-space">
                        <br />
                    </div> 

                    <h1 className="mt-5 title text-center"><strong>Geo-Time Shifting Prediction Results</strong></h1>
                    <br />
                    <div className="row center center-display mt-5">
                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon" src="https://static.thenounproject.com/png/2892359-200.png" />
                            <h3 className="icon-title blue"><strong>Current Data Region</strong></h3> 
                            <h3 className="icon-desc">{returnData.current_region}</h3>
                            <br />
                        </div>

                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon" src="https://freepngimg.com/thumb/clock/5-2-clock-png-image.png" />
                            <h3 className="icon-title blue"><strong>Recommended <span className="green">Green</span> Start Time</strong></h3> 
                            <h3 className="icon-desc">{returnData.greenest_starttime} UTC </h3>
                            <br />
                        </div>


                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon" src="https://static.thenounproject.com/png/2888422-200.png" />
                            <h3 className="icon-title blue"><strong>New Data Region</strong></h3> 
                            <h3 className="icon-desc">{returnData.greenest_region}</h3>
                            <br />
                        </div>
        
                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon" src="https://image.flaticon.com/icons/png/512/99/99744.png" />
                            <h3 className="icon-title blue"><strong>Supporting Balancing Authority</strong></h3>
                            <h3 className="icon-desc">{returnData.greenest_region_BA}</h3>
                            <br />
                        </div>
                    </div>

                    <h3 className="detail mt-5"><span className="blue"><strong>Total Run Emissions:</strong></span> <span>Reduced by <strong>{returnData.percentage_decrease}%</strong> by Time Shifting with a window size of <strong>{returnData.window_size_in_minutes}</strong> minutes.</span></h3>

                    {acceptButtonDisplay}

                    <div className="extra-space">
                        <br />
                    </div> 
                </div>

            // Geographic shifting prediction
            } else if (resultData.type == "load_shift_geo_eval.html") {
                // Store the returned data
                let returnData = resultData.returnData

                // Display the result based on the returned data
                result = <div className="result">
                    <div className="sm-extra-space">
                        <br />
                    </div> 

                    <h1 className="title mt-5 text-center"><strong>Geographic Shifting Prediction Results</strong></h1>
                    <br />
                    <div className="row center center-display mt-5">
                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon-azure" src="https://databarracks.imgix.net/uploads/Logos/azure-logo.svg?w=200&q=90&auto=format&fit=crop&crop=faces,edges&fm=png" />
                            <h3 className="icon-title blue"><strong>Suggested Azure Region</strong></h3>
                            <h3 className="icon-desc">{returnData.shiftAZ}</h3>
                            <br />
                        </div>
                        
                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon" src="https://image.flaticon.com/icons/png/512/99/99744.png" />
                            <h3 className="icon-title blue"><strong>Supporting Balancing Authority</strong></h3>
                            <h3 className="icon-desc">{returnData.shiftBA}</h3>
                            <br />
                        </div>
                    </div>

                    <h3 className="detail mt-5"><span className="blue"><strong>Starting Emissions:</strong></span> Reduced by <strong>{returnData.shift_perc}%</strong> if switched from {returnData.inputRegion}  with a window size of <strong>{returnData.window_size_in_minutes}</strong> minutes.</h3>

                    {acceptButtonDisplay}

                    <div className="extra-space">
                        <br />
                    </div> 
                </div>

            // Time shifting prediction
            } else if (resultData.type == "load_shift_eval.html") {
                // Store the returned data
                let returnData = resultData.returnData

                // Display the content based on the returned data
                result = <div className="result">
                    <div className="sm-extra-space">
                        <br />
                    </div> 

                    <h1 className="mt-5 title text-center"><strong>Time Shifting Prediction Results</strong></h1>
                    <br />
                    <div className="row center center-display mt-5">
                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon" src="https://freepngimg.com/thumb/clock/5-2-clock-png-image.png" />
                            <h3 className="icon-title blue"><strong>Recommended <span className="green">Green</span> Start Time</strong></h3> 
                            <h3 className="icon-desc">{returnData.shiftTime} UTC on {returnData.shiftDate}</h3>
                            <br />
                        </div>

                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon" src="https://databarracks.imgix.net/uploads/Logos/azure-logo.svg?w=200&q=90&auto=format&fit=crop&crop=faces,edges&fm=png" />
                            <h3 className="icon-title blue"><strong>Azure Region</strong></h3> 
                            <h3 className="icon-desc">{returnData.shift_choice}</h3>
                            <br />
                        </div>
        
                        <div className="col-xl-2 col-md-2 result-card">
                            <img className="icon" src="https://image.flaticon.com/icons/png/512/99/99744.png" />
                            <h3 className="icon-title blue"><strong>Supporting Balancing Authority</strong></h3>
                            <h3 className="icon-desc">{returnData.shiftBA}</h3>
                            <br />
                        </div>
                    </div>

                    <h3 className="detail mt-5"><span className="blue"><strong>Run Emissions:</strong></span> <span>Reduced by <strong>{returnData.shift_perc}%</strong> by Time Shifting with a window size of <strong>{returnData.window_size}</strong></span></h3>
                    <h3 className="detail"><span className="blue"><strong>Time (HH:MM:SS) Until</strong></span> <strong>Greenest Start Time:</strong> {returnData.shift_delta}</h3>

                    {acceptButtonDisplay}

                    <div className="extra-space">
                        <br />
                    </div> 
                </div>

            // If nothing in the above mathces with the page state, display an error page 
            } else {
                result = <div className="error">
                {/* Add some spacing */}
                <div className="extra-space">
                    <br />
                </div> 

                <img className="error-img" src={errorImg} alt="error" />

                <p className="error-title">Sorry, we couldn't find a prediction based on your input</p>
                <p className="error-desc">Please try again</p>

                {/* Direct users back to the starting page */}
                <div className="text-center mt-5">
                    <button
                        className="btn-secondary btn btn-default btn-lg center" 
                        onClick= {() => {
                            setDisplay("");
                    }}>Back</button>
                </div>

                {/* Add some spacing */}
                <div className="extra-space">
                    <br />
                </div> 
            </div>
            }

        } 

        // Store the result in content
        content = <div>
            {result}
        </div>

    // If the page isn't the result page
    } else {
        content = <div className="shifting">
            <ScrollContainer>
                <ScrollPage page={0}>
                    {/* Website title section */}
                    <div className="shifting-title-container">
                        <img className="shifting-title-image" src={shiftingImg}/>
                        <h1 className="shifting-website-title">Carbon Aware Scheduling</h1>
                    </div>
                </ScrollPage>

                <ScrollPage page={1}>
                    {/* Form to get user input */}
                    <Animator animation={FadeUp}>
                        <p className="question-title mt-5">Choose a Job Scope</p>
                        <div className="d-flex">
                            <div className="card mb-3 mt-2">
                                <div className="card-body">
                                    <form id="shifting_form" method="POST" action="/shift_predictions"  encType="multipart/form-data" onSubmit={handleSubmit}>
                                        {/* Step One */}
                                        <span className="steps green"><strong>Step One: </strong></span>
                                        <label className="mt-4"><b> Pick a Prediction Type</b></label>

                                        &nbsp;&nbsp;

                                        {/* Tooltip */}
                                        <BsFillQuestionCircleFill data-tip data-for="type" className="mb-1 blue"/>   
                                        <ReactTooltip id='type' aria-haspopup='true' role='example'>
                                            <h2 className="tooltip-title">Load Shifting Prediction Types:</h2>
                                            {/* <br />
                                            <p className="tooltip-desc"><strong><span className="steps">Demand Shifting</span>:</strong> Carbon aware workload shifting which finds the greenest start time across all data centers permitted in the search.  This method provides the <u>best carbon reduction </u> results out of the three shifting types.</p> */}
                                            <p className="tooltip-desc"><strong>Geographic Shifting:</strong> Find a new data center for compute instances for cross region shifting to reduce the resource's carbon footprint. This shifting type assumes an immediate start time for the compute activity.</p>
                                            <p className="tooltip-desc"><strong>Time Shifting: </strong>Search for the greenest starting time in at a specified data center.  </p>
                                        </ReactTooltip>   

                                        <br/>
                                        
                                        <label htmlFor="data_az" className="mt-4">Load Shifting Type: </label>
                                        <select name="data_shifter" id="data_shifter" className="box-input">
                                            <option value="nada"> </option>
                                            {/* <option value="Geographic and Time Shift">Demand Shifting</option> */}
                                            <option value="Geographic Shift Only">Geographic Shifting</option>
                                            <option value="Time Shift Only">Time Shifting</option>
                                        </select>
                                        
                                        <div className="space">
                                            <br />
                                        </div>    

                                        {/* Step Two */}
                                        <span className="steps green"><strong>Step Two: </strong></span>
                                        <label><b> Pick an Azure region or WattTime balancing authority</b></label>
                                        <br/>
                                        <label htmlFor="data_az" className="mt-4">Azure Region:</label>
                                        <select name="data_az" id="data_az" className="box-input">
                                            <option value="nada"> </option>
                                            <option value="West US">West US</option>
                                            <option value="West US 2">West US 2</option>
                                            <option value="West Central US">West Central US</option>
                                            <option value="East US">East US</option>
                                            <option value="North Central US">North Central US</option>
                                            <option value="East US 2">East US 2</option>
                                            <option value="East US 2 EUAP">East US 2 EUAP</option>
                                            <option value="South Central US">South Central US</option>
                                            <option value="Central US EUAP">Central US EUAP</option>
                                            <option value="Central US">Central US</option>
                                            <option value="Germany West Central">Germany West Central</option>
                                            <option value="Germany North">Germany North</option>
                                            <option value="Canada Central">Canada Central</option>
                                            <option value="West Europe">West Europe</option>
                                            <option value="Australia Southeast">Australia Southeast</option>
                                            <option value="Australia Central">Australia Central</option>
                                            <option value="Australia East">Australia East</option>
                                            <option value="Australia Central 2">Australia Central 2</option>
                                            <option value="UK South">UK South</option>
                                            <option value="North Europe">North Europe</option>
                                            <option value="France Central">France Central</option>
                                            <option value="France South">France South</option>
                                            <option value="West US 3">West US 3</option>
                                            <option value="Norway East">Norway East</option>
                                            <option value="Norway West">Norway West</option>
                                            <option value="UK West">UK West</option>
                                            <option value="Switzerland North">Switzerland North</option>
                                            <option value="Canada East">Canada East</option>
                                            <option value="Switzerland West">Switzerland West</option>
                                            <option value="Korea Central">Korea Central</option>
                                            <option value="Japan East">Japan East</option>
                                            <option value="Korea South">Korea South</option>
                                            <option value="Japan West">Japan West</option>
                                            <option value="UAE North">UAE North</option>
                                            <option value="UAE Central">UAE Central</option>
                                            <option value="JIO India West">JIO India West</option>
                                            <option value="East Asia">East Asia</option>
                                            <option value="West India">West India</option>
                                            <option value="Central India">Central India</option>
                                            <option value="South India">South India</option>
                                            <option value="Southeast Asia">Southeast Asia</option>
                                            <option value="South Africa West">South Africa West</option>
                                            <option value="South Africa North">South Africa North</option>
                                            <option value="Brazil South">Brazil South</option>
                                            <option value="Brazil Southeast">Brazil Southeast</option>
                                        </select>

                                        <span className="or"><strong>or</strong></span> 

                                        <label htmlFor="data_ba" className="mt-4">Balancing Authority:</label>
                                        <select name="data_ba" id="data_ba" className="box-input">
                                            <option value="nada">  </option>
                                            <option value="PJM Roanoke">PJM Roanoke</option>
                                            <option value="PJM DC">PJM DC</option>
                                            <option value="ERCOT San Antonio">ERCOT San Antonio</option>
                                            <option value="PUD No 2 of Grant County">PUD No 2 of Grant County</option>
                                            <option value="National Electricity Market (Australia)">National Electricity Market (Australia)</option>
                                            <option value="Ireland">Ireland</option>
                                            <option value="United Kingdom">United Kingdom</option>
                                            <option value="Netherlands">Netherlands</option>
                                            <option value="MISO Madison City">MISO Madison City</option>
                                            <option value="PJM Chicago">PJM Chicago</option>
                                            <option value="California ISO Northern">California ISO Northern</option>
                                            <option value="Independent Electricity System Operator (Ontario)">Independent Electricity System Operator (Ontario)</option>
                                            <option value="Hydro Quebec">Hydro Quebec</option>
                                            <option value="France">France</option>
                                            <option value="Germany and Luxembourg">Germany and Luxembourg</option>
                                            <option value="PacifiCorp East">PacifiCorp East</option>
                                            <option value="Arizona Public Service Co">Arizona Public Service Co</option>
                                        </select>

                                        <div className="space">
                                            <br />
                                        </div>  

                                        {/* Step Three */}
                                        <span className="steps green"><strong>Step Three: </strong></span>
                                        <label><b>Run Duration</b></label>

                                        &nbsp;&nbsp;

                                        {/* Tooltip */}
                                        <BsFillQuestionCircleFill data-tip data-for="run-duration" className="mb-1 blue"/>   
                                        <ReactTooltip id='run-duration' aria-haspopup='true' role='example'>
                                            <p className="tooltip-desc"><strong>Run Duration</strong> is the expected duration of the compute. Picking a window size will return the start-time with the lowest average emissions rate for the given window size. Without a window size selected, it will return the single time of minimum emissions instead.</p>
                                        </ReactTooltip>   

                                        <br />
                                        <label htmlFor="window_size_hours" className="mt-4">Hours:</label>
                                        <input type="number" min="0" max="24" step="1" name="window_size_hours"  className="box-input" placeholder="HH"/>&emsp;&emsp;

                                        <label htmlFor="window_size_minutes">Minutes (divisible by 5):</label>
                                        <input type="number" min="0" max="60" step="5" name="window_size_minutes"  className="box-input" placeholder="MM"/>

                                        <div className="space">
                                            <br />
                                        </div>

                                        {/* Step Four */}
                                        <span className="steps green"><strong>Step Four: </strong></span>
                                        <label><b>Select GPU SKU</b></label>

                                        &nbsp;&nbsp;

                                        {/* Tooltip */}
                                        <BsFillQuestionCircleFill data-tip data-for="gpu" className="mb-1 blue"/>   
                                        <ReactTooltip id='gpu' aria-haspopup='true' role='example'>
                                            <p className="tooltip-desc"><strong>GPU SKU</strong> is the desired SKU to be used for the compute.  This limits regions in geographic shifting to data centers that can offer the selection.</p>
                                        </ReactTooltip>   
                                    
                                        <br />
                                        <label htmlFor="gpu_type" className="mt-4" >GPU SKU:</label>

                                        <select name="gpu_type" id="gpu_type" className="box-input">
                                            <option value="nada"> </option>
                                            <option value="K80">K80</option>
                                            <option value="T4">T4</option>
                                            <option value="P100">P100</option>
                                            <option value="V100">V100</option>
                                            <option value="P40">P40</option>
                                            <option value="M60">M60</option>
                                            <option value="MI25">MI25</option>
                                            <option value="A100">A100</option>
                                        </select>
                                        
                                        &nbsp;&nbsp;

                                        <div className="space">
                                            <br />
                                        </div>

                                        {/* Step Five */}
                                        <span className="steps green"><strong>Step Five: </strong></span>
                                        <label><b>Select weight factor for Carbon intensity, cost and latency</b></label>
                                        <br /><br />
                                        
                                        <p>Carbon Efficiency:</p>
                                        <input type="range" id="carbonEfficiency" name="carbonEfficiency" min="0" max="1" step="0.1"/>

                                        <p>Cost:</p>
                                        <input type="range" id="cost" name="cost" min="0" max="1" step="0.1"/>

                                        <p>Latency:</p>
                                        <input type="range" id="latency" name="latency" min="0" max="1" step="0.1"/>
                                        

                                        {/* Tooltip */}
                                        <br/>
                                        <input className="mt-3" type="checkbox" name='sensitive'/> Workspace Contains Protected Data
                                        &nbsp;&nbsp;
                                        <BsFillQuestionCircleFill data-tip data-for="protect" className="mb-1 blue"/>   
                                        <ReactTooltip id='protect' aria-haspopup='true' role='example'>
                                            <p className="tooltip-desc"><strong>Protected Data</strong> implies that the workspace contains data subject to international migration and privacy laws.  Selecting this option limits any potenial workload shift to data centers that would be compliant and not violate laws.</p>
                                        </ReactTooltip> 

                                        {/* Button to fetch the result */}
                                        <div className="text-center mt-4">
                                            <button
                                                className="btn-success btn mb-5" 
                                                type = "submit" 
                                                value="Calculate Load Shifting Potenial" 
                                                onClick= {() => {
                                                    getResult()
                                            }}>Calculate Load Shifting Potential</button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </Animator>
                </ScrollPage>
            </ScrollContainer>
        </div>
    }

    return(    
        <div>
            {content}
        </div>
    );
}

export default Shifting; 



                    
