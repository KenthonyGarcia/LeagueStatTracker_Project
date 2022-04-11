import React from 'react';
import './App.css';
import Login from './login'
import Register from './register';
import Home from './home';
import Summoner from './summoner';
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';

function App(){
  return(
    <Router>
        <Routes>
          <Route path = "/" exact element = {<Home />}/>
        </Routes>
        <Routes>
          <Route path = "/login" exact element = {<Login />}/>
        </Routes>
        <Routes>
          <Route path = "/register" exact element = {<Register />}/>
        </Routes>
        <Routes>
          <Route path = "/summoner" exact element = {<Summoner />}/>
        </Routes>
    </Router>
  )
}

export default App