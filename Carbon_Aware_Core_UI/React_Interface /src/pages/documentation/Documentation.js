import React from 'react';
import { Link } from 'react-router-dom';
import './Documentation.css'

const Documentation = () => {

    return(    
       <div className="documentation">

            <div className="sm-extra-space">
                <br />
            </div> 

            <div classname="doc-content">
                <h2 className="category-title">Using the API</h2>

                <section className="doc-card-section"> 

                    <Link to="/monitor">
                        <div className="doc-card">
                            <p className="doc-card-title"><strong>Data Retrieval</strong></p>
                            <p className="doc-card-desc">Walk through on pulling metric data from Azure Monitor</p>
                        </div>
                    </Link>

                    <Link to="/api_docs">
                        <div className="doc-card">
                            <p className="doc-card-title"><strong>Query Formatting</strong></p>
                            <p className="doc-card-desc">Describes formatting requirements for input parameters</p>
                        </div>
                    </Link>
                    

                    <Link to="/api_use">
                        <div className="doc-card">
                            <p className="doc-card-title"><strong>API Information</strong></p>
                            <p className="doc-card-desc">Detailed documents describing API use</p>
                        </div>
                    </Link>


                    <div className="doc-card-disabled">
                        <p className="doc-card-title"><strong>Swagger</strong></p>
                        <p className="doc-card-desc">Update in progress</p>
                    </div>

                </section>


                <h2 className="category-title mt-5">Project Information</h2>
                <section className="doc-card-section">
                    <Link to="/kb_cite">
                        <div className="doc-card">
                            <p className="doc-card-title"><strong>Knowledge Base</strong></p>
                            <p className="doc-card-desc">Project Citations</p>
                        </div>
                    </Link>
                </section>
                    {/* <li className="appendixLink"><Link to="/kb_summary"><strong>Background Summary:</strong> Problem Space and Theory for Project Motivation</Link></li> */}
                    {/* <li className="appendixLink"><Link to="case_study"><strong>Case Study:</strong> Project Overview and Recommendations</Link></li> */}


                <h2 className="category-title mt-5">Team Information and Progress</h2>
                <section className="doc-card-section">
                    <a href="https://github.com/TaylorPrewitt/carbon-awareAPI">
                        <div className="doc-card">
                            <p className="doc-card-title"><strong>GitHub Repo</strong></p>
                            <p className="doc-card-desc">GreenAI-API team GitHub</p>
                        </div>
                    </a>

                    <Link to="/deck">
                        <div className="doc-card">
                            <p className="doc-card-title"><strong>Decks</strong></p>
                            <p className="doc-card-desc">Slide decks from Vertical presentation</p>
                        </div>
                    </Link>
                </section>                    
                {/* <li className="appendixLink"><Link to="miro"><strong>Miro:</strong> Relation diagram for API and UI</Link></li> */}

            </div>

            <div className="sm-extra-space">
                <br />
            </div> 

        </div>
    );
}

export default Documentation; 