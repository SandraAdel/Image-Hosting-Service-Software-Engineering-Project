// import { router } from 'json-server';
import React from 'react';
import {
  BrowserRouter as Router, Route, Switch,
} from 'react-router-dom';
import StartPage from './Components/StartPage/StartPage';
import FormSignup from './Components/StartPage/SingUP/FormSignup';
// import './App.css';
// import Addv from './Components/Addv';
import Home from './Components/HomePage/Home';
import NavBar from './Components/NavBar/NavBar';
import About from './Components/NavBar/About';

// import Button from "react-bootstrap/Button";

function App() {
  return (
    <Router>
      <div className="App">
        <NavBar />
        <Switch>
          <Route path="/Home" exact component={Home} title="Home | Flickr" />
          <Route path="/" exact component={StartPage} title="Find your inspiration. | Flickr" />

          <Route path="/SignUp" exact component={FormSignup} title="Flickr Login" />

          <Route path="/SignUp" exact>
            <FormSignup />
          </Route>
          <Route path="/about" component={About} />
        </Switch>
      </div>
    </Router>

  );
}

export default App;
