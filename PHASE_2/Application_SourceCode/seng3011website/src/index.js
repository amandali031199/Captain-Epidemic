import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';
import { BrowserRouter as Router, Route } from "react-router-dom";
import SignUp from './Signup.js';
import Login from './Login.js';
import MapContainer from './Map.js';

const routing = (
  <Router>
    <div>
      <Route exact path = "/" component = {App}/>
      <Route path = "/login" component = {Login}/>
      <Route path = "/signup" component = {SignUp}/>
      <Route path = "/map" component = {MapContainer}/>
    </div>
  </Router>
)

ReactDOM.render(
  routing,
  document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
