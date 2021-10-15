import React from 'react';
import './Accept.css'
import acceptImg from '../../img/accept.png'
import { Link } from 'react-router-dom';

const Accept = () => {

    return(    
        <div>
            <div className="result">
                {/* Add spacing */}
                <div className="sm-extra-space">
                    <br />
                </div> 

                {/* Robot icon */}
                <div className="row center center-display mt-5">
                    <div className="icon-card">
                        <img className="icon mr-1" src={acceptImg} />
                        <br />
                    </div>
                </div>

                {/* Thank you message */}
                <h3 className="thank-you">Thank You for Thinking Green!!</h3>

                {/* Add spacing */}
                <div className="sm-extra-space">
                    <br />
                </div> 

                {/* Direct users to the main page */}
                <div className="text-center mt-5">
                    <Link to="/"><button className="btn-secondary btn btn-default btn-lg center" >Main Page</button></Link>
                </div>

                {/* Add spacing */}
                <div className="thank-space">
                    <br />
                </div> 
            </div>
        </div>
    );
}

export default Accept; 
