import React from 'react';
import './ApiDocs.css'

const ApiDocs = () => {

    return(    
        <div className="doc">
            <div className="doc-content">
                <div className="xs-extra-space">
                    <br />
                </div> 

                <div className="body">
                    <h1 className="mt-5 doc-title">Accepted Input Formats for Timestamps</h1>

                    <div className="mainInfo mt-5">
                        <h4 className="infoTitle"><strong>Preconfigured as ISO format preferred</strong></h4>
                        <p className="mt-5"><strong>Easy input with the following constraints:</strong></p>
                        <ul>
                        <li>Possible value separators:</li>
                            <ul className="subBullet">
                            <li>Spaces, Dashes, Backslashes</li>
                            </ul>
                        </ul>

                        <br />
                        <br />

                        <h4>Date:</h4>
                        <li>If Month is written in english</li>
                
                        <ul className="subBullet">
                            <li>month-day-year    &emsp;&emsp;&emsp; ex: July 24 2020</li>
                            <li>year-month-day    &emsp;&emsp;&emsp;  ex: 2020 July 24</li>
                            <li>month-year-day &emsp;&emsp;&emsp;   ex: July 2020 24</li>
                            <li>day-year-month    &emsp;&emsp;&emsp;  ex: 24 2020 July</li>
                            <li>year-day-month   &emsp;&emsp;&emsp;   ex: 2020 24 July</li>
                        </ul>
                        <li>If month is numeric representation, day and month need to be connected with month preceding day</li>
                        <ul className="subBullet">
                            <li>month-day-year   &emsp;&emsp;&emsp; ex: 7/24/2020</li>
                            <li>year-month-day &emsp;&emsp;&emsp;  ex: 2020/7/24</li>
                        </ul>

                        <br />

                        <h4>Time:</h4> 
                        <li>Accepts both 12 and 24-hour clocks formats</li>

                        <ul className="subBullet">
                            <li>Default input is 24-hour clock</li>
                            <li>12-hour am/pm designations accepted</li>
                        </ul>

                        <br />

                        <h4>Precision Designation:</h4>
                        <br />
                        <ul className="subBullet">
                            <li>Needs only 1 digit in hour position</li>
                            <li>Must use colons to separate time precision levels</li>
                            <li>Can specify time to only 2 digits of precision for each time position, down to seconds marker</li>
                                <ul className="subBullet">
                                    <li>Time precision format HH:MM:SS</li>
                                    <li>Ex: If 1 is input, it assumes 01:00:00</li>
                                    <li>Ex: If 1pm in input, it assumes 13:00:00</li>
                                </ul>
                        </ul>

                        <br />
                        <br />

                        <h4>Time Zone:</h4>
                        <li>Input with a ISO numeric offset</li>
                        <ul className="subBullet">
                        <li>Ex: Time input as: 13:00:00-0800</li>
                        </ul>
                        <li>If not preconfigured ISO:</li>
                        <ul className="subBullet">
                            <li>A space is needed between datetime and time zone</li>
                            <li>Explicitly designate time zone via standard abbreviation</li>
                            <ul className="subBullet">
                                <li>Ex: PST, CST, PDT, etc.</li>
                            </ul>
                            <li>Time zone is an optional time input</li>
                            <li>If none designated, default assumption is UTC</li>
                        </ul>

                        <p>If no given datetime stamp is given for an endpoint that requires one as a parameter, defaults to current datetime as input.</p>
                    </div>
                </div>

                <div className="xs-extra-space">
                        <br />
                </div>

            </div>
        </div>
    );
}

export default ApiDocs; 