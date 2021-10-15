import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import logo from '../../img/logo.png'
import logo2 from '../../img/logo2.png'

import './Nav.css';

const Nav = () => {
  // Set up to change the navbar background color
  const [navbar, setNavBar] = useState(false);

  const changeBackground = () => {
    if(window.scrollY >= 80) {
      setNavBar(true);
    } else {
      setNavBar(false);
    }
  }
  
  window.addEventListener('scroll', changeBackground);

  // Return the navbar
  return (
    <div className={navbar ? 'nav active' : 'nav'}>
      <nav className="navbar">
        <div className="navbar-container">
          <ul className="horizontal-list">
            <li className="navLink"><a className="navLink logo" href="https://azure.microsoft.com/en-us"><img className="logo" src={logo} onMouseOver={e => (e.currentTarget.src= logo2)} onMouseOut={e => (e.currentTarget.src = logo)}/></a></li>
            <li><Link className="navLink" to="/">Home</Link></li>
            {/* <li><Link className="navLink" to="/explore">Explore</Link></li> */}
            <li><Link className="navLink" to="/shifting">Shifting</Link></li>
            {/* <li><Link className="navLink" to="/carbon_intensity">Carbon Intensity</Link></li> */}
            <li><Link className="navLink" to="/documentation">Documentation</Link></li>
          </ul>
        </div>
     	</nav>
      <hr />
    </div>
  );
};

export default Nav;