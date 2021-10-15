import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';

// images for hom page
import homeBackground from '../../img/home_title.png'
import descImg from '../../img/desc_img.jpeg'
import splitImg from '../../img/split.png'

// library for scrolling animation
import { Animator, ScrollContainer, ScrollPage, batch, Fade, FadeIn, Move, MoveIn, MoveOut, Sticky, StickyIn, ZoomIn } from "react-scroll-motion";
import './Home.css'

const Home = () => {

    const FadeUp = batch(Fade(), Move(), Sticky());

    return(
        <div className="home">
            <ScrollContainer>
                {/* Title page */}
                <ScrollPage page={0}>
                    <div className="title-container">
                        <img className="title-image" src={homeBackground}/>
                        <h1 className="microsoft-title">Microsoft Azure</h1>
                        <h1 className="project-title">Carbon Aware <span className="green">API</span></h1>
                    </div>
                </ScrollPage>

                {/* Problem Space Description */}
                <ScrollPage page={1} >
                    <Animator animation={FadeUp}>
                        <h3 className="green desc-title mt-5">A Green Solution for Energy Intensive Workloads</h3>
                    </Animator>
                </ScrollPage>

                {/* Green bar */}
                <ScrollPage page={2}>
                    <img className="split-image" src={splitImg}/>
                </ScrollPage>

                {/* Why */}
                <ScrollPage page={3}>
                    <Animator animation={FadeUp}>
                        <p className="desc-sub-title">Why...</p>

                        <p className="desc-sub fade-in">
                            The scientific consensus is clear. The world confronts an urgent
                            carbon problem. The carbon in our atmosphere has created a
                            blanket of gas that traps heat and is changing the world’s climate.
                            Already, the planet’s temperature has risen by 1 degree Celsius.
                            If we don’t curb emissions and temperatures continue to climb,
                            science tells us that the results will be catastrophic.
                            <br />
                            <a href="https://aka.ms/MSFTcarbonfactsheet">Read more from Brad Smith's blog</a>
                        </p>
                        <p className="desc-sub fade-in">
                            Microsoft has been carbon neutral across the world since 2012 and commits to being carbon negative by 2030. 
                            Our goal is to promote sustainable development and low-carbon business practices globally through our sustainable 
                            business practices and cloud-enabled technologies.
                        </p>
                    </Animator>
                </ScrollPage>

                {/* Green bar */}
                <ScrollPage page={4}>
                    <img className="split-image" src={splitImg}/>
                </ScrollPage>

                {/* How */}
                <ScrollPage page={5}>
                    <Animator animation={FadeUp}>
                        <p className="desc-sub-title">How...</p>

                        <p className="desc-sub">
                            Up until 20 years ago, a single utility would own all the power 
                            plants and transmission lines to supply electricity for a specific region. 
                            It would be responsible to dial-up or down its supply according to the 
                            demand. However, in today’s competitive business landscape, we have 
                            an energy wholesale market to meet the demands. The market does 
                            short-term demand forecast day-ahead and allows power suppliers to 
                            come online and place bids. The market brings in plants online in 
                            order of price. The market generally brings in the lowest-emission plants first. Then every five minutes 
                            throughout the day, the market would decide which plant to run to match the supply.
                        </p>
                    </Animator>
                </ScrollPage>

                {/* Microsoft solution image */}
                <img className="solution-img" src={descImg}/>

                <div className="solution-container">
                    {/* Blank space */}
                    <div className="space">
                        <br />
                    </div>
                    
                    {/* Explain the solution */}
                    <div className="solution-desc">
                        <h1 className="solution-title">Our Solution</h1>
                        <p className="solution-desc-sub">
                            Azure (AZ) customers have requested their Azure Carbon emissions footprint be available, 
                            and in response Microsoft released the Azure Sustainability Calculator. This uses yearly average 
                            emissions data to enable customers to make more informed decisions about their environmental impact. 
                            There is an opportunity to make emissions efficiency a key competitive advantage, as well as significantly 
                            reducing Azure emissions, through targeted software development.
                        </p>
                                
                        <p className="solution-desc-sub">
                            The Carbon API exists as a wrapper on top of the WattTime API. This API will take the different
                            WattTime endpoints (Grid, Real-Time, Historical, Forecasted) for Carbon Intensity (CI) data and associate them to
                            AZ regions. This includes developing a dashboard to map CI data for AZ regions and provide multiple
                            visualizations of the CI data with respect to AZ regions.
                        </p>

                        {/* Buttons link to the UI */}
                        <div className="link-container mt-5 center">
                            <ul className="horizontal-list">
                                {/* <li><Link to="/explore"><button type="button" className="btn btn-outline-primary link">Explore Emission History</button></Link></li> */}
                                <li><Link to="/shifting"><button type="button" className="btn btn-outline-primary link">Calculate Load Shifting Potential</button></Link></li>
                                {/* <li><Link to="/carbon_intensity"><button type="button" className="btn btn-outline-primary link">Query Carbon Intensity</button></Link></li> */}
                            </ul>
                        </div>

                    </div>
                </div>

            </ScrollContainer> 
        </div>   
    );
}

export default Home; 