import React, { useState, useEffect } from 'react';
import { Animator, ScrollContainer, ScrollPage, batch, Fade, FadeIn, Move, MoveIn, MoveOut, Sticky, StickyIn, ZoomIn } from "react-scroll-motion";

import intensityImg from '../../img/intensity.jpg'

// Tooltip library
import ReactTooltip from "react-tooltip";
import { BsFillQuestionCircleFill } from "react-icons/bs";

// Loading spinner library
import HashLoader from "react-spinners/HashLoader";
import { css } from "@emotion/react";

import './CarbonIntensity.css'

const CarbonIntensity = () => {

    const [display, setDisplay] = useState("initial_page");
    const [resultData, setResultData] = useState(undefined);

    const FadeUp = batch(Fade(), Move(), Sticky());


    // Return the Explore page
    return(    
        <div className="intensity">
            <ScrollContainer>
                <ScrollPage page={0}>
                    {/* Website title section */}
                    <div className="intensity-title-container">
                        <img className="intensity-title-image" src={intensityImg}/>
                        <h1 className="intensity-website-title">Carbon Intensity</h1>
                    </div>
                </ScrollPage>

                {/* Ask for user input */}
                <ScrollPage page={1}>
                    <Animator animation={FadeUp}>
                        <p className="question-title mt-5">Choose a Job Scope</p>
                        <div className="d-flex">
                            <div className="card mb-3 mt-2">
                                <div className="card-body">
                                    <form method="POST" action="/chooser" encType="multipart/form-data">

                                        {/* Step One */}
                                        <span className="steps green"><strong>Step One: </strong></span>
                                        <label><b> Pick an Azure Region or WattTime Balancing Authority</b></label>

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

                                        <label htmlFor="data_ba" className="mt-2 ml-5">Balancing Authority:</label>
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
                                            <option value="France">France</option>
                                            <option value="Hydro Quebec">Hydro Quebec</option>
                                            <option value="Germany and Luxembourg">Germany and Luxembourg</option>
                                            <option value="PacifiCorp East">PacifiCorp East</option>
                                            <option value="Arizona Public Service Co">Arizona Public Service Co</option>
                                        </select>

                                        <div className="space">
                                            <br />
                                        </div>  

                                        {/* Step Two */}
                                        <span className="steps green"><strong>Step Two: </strong></span>
                                        <label><b> Select an Output and Type</b></label>

                                        &nbsp;&nbsp;

                                        <BsFillQuestionCircleFill data-tip data-for="intensity-output" className="mb-1 blue"/>   
                                        <ReactTooltip id='intensity-output' aria-haspopup='true' role='example'>
                                            <h2 className="tooltip-title">Carbon Intensity:</h2>
                                            <p className="tooltip-desc"><strong>Grid Data:</strong> Obtain historical marginal emissions for a given area. Omitting the starttime and endtime parameters will return generated data updates for the region. </p>

                                            <p className="tooltip-desc">
                                                <strong>Historical Data: </strong>Obtain a zip file containing the MOER values and timestamps for a given region for (up to) the past two years.  Historical data will be updated on the 2nd of each month at midnight UTC for the previous month. 
                                            </p>
                                            <p className="tooltip-desc">
                                                <strong>Real-Time Data:</strong> Provides a real-time signal indicating the carbon intensity on the local grid in that moment (typically updated every 5 minutes). The current emissions rate of the grid is returned as a raw Marginal Operating Emissions Rate (MOER)
                                            </p>
                                            <p className="tooltip-desc">
                                                <strong>Forecast Data:</strong> Obtain Margial Operating Emission Rate forecasts for a given region. Omitting the starttime and endtime parameters will return recently generated forecast for a given region.
                                            </p>
                                        </ReactTooltip>   

                                        <br />

                                        <label htmlFor="data" className="mt-4">Carbon Intensity Output:</label>
                                        <select name="data" id="data" className="box-input">
                                            <option value="nada">  </option>
                                            <option value="grid">Grid Data</option>
                                            <option value="historical">Historical Data Zipfile</option>
                                            <option value="index">Real-Time Data</option>
                                            <option value="forecast">Forecast Data</option>
                                        </select>

                                        <div className="space">
                                            <br />
                                        </div>  

                                        {/* Step Three */}
                                        <span className="steps green"><strong>Step Three: </strong></span>
                                        <label><b> Enter WattTime User Information</b></label>

                                        <br />

                                        <div className="form-group row mt-3 ml-1">
                                            <div>
                                                <label htmlFor="data">Username:</label>
                                                <input type="text" className="box-input" name = "user_name" />&emsp;&emsp;

                                                <label htmlFor="data">Password:</label>
                                                <input type="password" className="box-input" id="password_input" name="pass_word" />&emsp;&emsp;
                                            </div>
                                                
                                        </div>

                                        <div className="space">
                                            <br />
                                        </div>  

                                        {/* Step Four */}
                                        <span className="steps green"><strong>Step Four: </strong></span>
                                        <label><b> Enter a Time Window</b> <span className="grey">(Optional input for grid data and forecast data)</span></label>

                                        <p className="mt-2">Example: 7/16/2021 5:30:00 PM PST</p>
                                        <div className="form-group row mt-4 ml-1">
                                            <div>
                                                <label htmlFor="data" className="form-label">Start Time:</label>
                                                <input type="text" className="box-input" name = "starttime" />&emsp;&emsp;

                                                <label htmlFor="data" className="form=label">End Time:</label>
                                                <input type="text" className="box-input" name="endtime" />&emsp;&emsp;
                                            </div>
                                            
                                        </div>
                                    
                                        <div className="text-center mt-5">
                                            <input className="findButton btn-success btn mb-5 mt-3" type = "submit" value="Query carbon intensity data"/>
                                        </div>

                                    </form>
                                </div>
                            </div>
                        </div>
                    </Animator>
                </ScrollPage>
            </ScrollContainer>
        </div>
    );
}

export default CarbonIntensity; 
