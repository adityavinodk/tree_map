import React, { Component, Fragment } from 'react';
import logo from './logo.svg';
//import './home.css';
//import './login.css';
import './signup.css';
import Homepage from './components/homepage.js';
import Loginpage from "./components/loginpage.js";
import Signuppage from "./components/signuppage.js";

function App() {
  return (
    <div className="App">
		<Signuppage />
    </div>
  );
}

export default App;
