import React from 'react';
import './Deck.css'

const Deck = () => {

    return(    
        <div className="doc">
            <div className="doc-content">
                <div className="xs-extra-space">
                    <br />
                </div> 

                <h1 className="slide-title mt-5">Project Slide Decks</h1>

                <div className="container mb-5">

                    <h3 className="text-center">Project Checkpoint Slide Deck</h3>
                    <div className="row">
                        <iframe src="https://onedrive.live.com/embed?resid=7A76240357EBCACD%21181676&amp;authkey=%21AH9D0RgrvzH-JlQ&amp;em=2&amp;wdAr=1.7777777777777777" width="962px" height="565px" frameBorder="0">This is an embedded <a target="_blank" href="https://office.com">Microsoft Office</a> presentation, powered by <a target="_blank" href="https://office.com/webapps">Office</a>.</iframe>
                    </div>

                    <p className="main_content">Slide deck for the halfway checkpoint of the project.  Covers motivation for using marginal emissions as a metric and high-level architecture of the API.  At this time, construction was beginning for load shifting features and calculating Azure emissions using WattTime grid records.</p>

                    <br />

                    <div className="pt-1">
                        <br />
                    </div>

                    <h3 className="text-center">Project Conclusion Slide Deck</h3>
                    <div className="row">
                        <iframe src="https://onedrive.live.com/embed?cid=7A76240357EBCACD&amp;resid=7A76240357EBCACD%21181975&amp;authkey=AI7W9-6I8kPbjU0&amp;em=2&amp;wdAr=1.7777777777777777" width="962px" height="565px" frameBorder="0">This is an embedded <a target="_blank" href="https://office.com">Microsoft Office</a> presentation, powered by <a target="_blank" href="https://office.com/webapps"></a></iframe>
                    </div>

                    <p className="main_content">Slide deck for the end of the project. Brief recap of project space and use of marginal emission metrics, followed by an outline of the project tools and methods.  Ends with an exposition of the features Carbon Intensity API offers, recommended use cases, and an outline of work to take the project forward.  At this stage, the Carbon Intensity API can deliver and analyze WattTime data, provide emissions profiles for energy profiles, and offer load shifting suggestions across regions or time.</p>
                </div>
                <div className="xs-extra-space">
                    <br />
                </div> 
            </div>
       </div>
    );
}

export default Deck; 