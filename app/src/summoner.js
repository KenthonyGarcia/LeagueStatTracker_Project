import React from 'react';
import './App.css';
import video from "./login.mp4"

function summoner(){
    return(
        
    <body class = "bg">
        <video loop autoPlay
            style = {{
                position: "absolute",
                width: "100%",
                left: "50%",
                top: "50%",
                height: "100%",
                objectFit: "cover",
                transform: "translate(-50%, -50%)",
                zIndex: "-1"
            }}
            >
                <source src={video} type="video/mp4"/>
            </video>
        <div class= "webpage">   
            <div>
                <h1 class = "nameStyle" ></h1>
                <h1 class = "levelStyle" ></h1>
            </div>
        </div>
        <div class="dropdown">
            <button onclick="myFunction()" class="dropbtn">Full Match Stats</button>
            <div id="myDropdown" class="dropdown-content">
        </div>
        </div>
    </body>
    );
}

export default summoner;