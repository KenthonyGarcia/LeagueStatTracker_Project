import React from 'react';
import './App.css';
import video from "./register.mp4"


function register(){
    return(
        <body>
            <h1 class = "title-text">RiftTracker</h1>
            <br/><br/><br/><br/>
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
            <div>
                <div align="center" class="border2">
                    <div class="header">
                        <h1 class="word">Register</h1>
                    </div><br/><br/><br/>
                    <h2 class="word">
                        <div class = "form">
                            <input id="username" name="username" type="text" class="textbox" autocomplete="off" required/>
                            <label for = "name" class = "label-name">
                                <span class = "content-name">Username</span>
                            </label>
                        </div>
                        <br/><br/>
                        <div class = "form">
                            <input id="SummonerName" name="SummonerName" type="text"  class="textbox" autocomplete="off" required/>
                            <label for = "SummonerName" class = "label-name">
                                <span class = "content-name2">Summoner Name</span>
                            </label>
                        </div>
                        <br/><br/>
                        <div class = "form">
                            <input id="password" name="password" type="password" class="textbox" autocomplete="off" required/>
                            <label for = "name" class = "label-name">
                                <span class = "content-name">Password</span>
                            </label>
                        </div>
                        <br/><br/>
                        <div class = "form">
                            <input id="email" name="email" type="text" class="textbox" autocomplete="off" required/>
                            <label for = "SummonerName" class = "label-name">
                                <span class = "content-name3">Valid Email-Address</span>
                            </label>
                        </div>
                        <br/><br/><br/>
                        <input type="submit" class="btn" value="Sign Up"></input><br/><br/>
                    </h2>
                    <p class="bottom">Already have an account?  <a class="bottom" href="{{url_for('login')}}"> Sign In here</a></p>
                </div>
            </div>
        </body>
    );
}

export default register;
