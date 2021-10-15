import React, { useState, useEffect } from 'react';
import { Route, Switch, Redirect } from 'react-router-dom';
import Nav from './components/nav/Nav'
import Home from './pages/home/Home'
// import Explore from './pages/explore/Explore'
import Shifting from './pages/shifting/Shifting'
import Documentation from './pages/documentation/Documentation'
import Monitor from './pages/documentation/resources/monitor/Monitor'
import ApiDocs from './pages/documentation/resources/api_docs/ApiDocs'
import ApiUse from './pages/documentation/resources/api_use/ApiUse'
import KbSummary from './pages/documentation/resources/kb_summary/KbSummary'
import KbCite from './pages/documentation/resources/kb_cite/KbCite'
import CaseStudy from './pages/documentation/resources/case_study/CaseStudy'
import Deck from './pages/documentation/resources/deck/Deck'
import Miro from './pages/documentation/resources/miro/Miro'
import CarbonIntensity from './pages/carbon_intensity/CarbonIntensity'
import fade_in_out from './utils/fade-in-out'
import Accept from './pages/accept/Accept'
import Footer from './components/footer/Footer'
import './App.css'

const App = () => {

  useEffect(fade_in_out, [])

  return (
    <div>
      <Nav />
      <div className="content">
        <Switch>
          <Route exact path="/home" component={Home} />
          <Route exact path="/">
            <Redirect to="/home" />
          </Route>
          {/* <Route exact path="/explore" component={Explore} /> */}
          <Route exact path="/shifting" component={Shifting} />
          <Route exact path="/documentation" component={Documentation} />
          <Route exact path="/monitor" component={Monitor} />
          <Route exact path="/api_docs" component={ApiDocs} />
          <Route exact path="/api_use" component={ApiUse} />
          <Route exact path="/kb_summary" component={KbSummary} />
          <Route exact path="/kb_cite" component={KbCite} />
          <Route exact path="/case_study" component={CaseStudy} />
          <Route exact path="/deck" component={Deck} />
          <Route exact path="/miro" component={Miro} />
          <Route exact path="/carbon_intensity" component={CarbonIntensity} />
          <Route exact path="/accept" component={Accept} />
        </Switch>
      </div>
    </div>
  )
};

export default App;
