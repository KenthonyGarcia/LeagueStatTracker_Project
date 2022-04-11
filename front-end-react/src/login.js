import React from 'react';
import './App.css';
import video from "./login.mp4"

function login(){
    return(
        <body>
            <h1 class = "title-text">RiftTracker</h1>
            <br/><br/><br/><br/><br/><br/><br/><br/>
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
            <div align="center">
                <div align="center" class="border3">
                    <div class="header">
                        <h1 class="word">Login</h1>
                    </div><br/><br/><br/>
                    <h2 class="word">
                        <div class = "form">
                            <input id="email" name="email" type="text" class="textbox" autocomplete="off" required/>
                                <label for = "name" class = "label-name">
                                    <span class = "content-name4">Email </span>
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
                            <input id="otp_code" name="otp_code" type="text" class="textbox" autocomplete="off" required/>
                                <label for = "name" class = "label-name">
                                    <span class = "content-name3">Authentication Code</span>
                                </label>
                        </div>
                        <br/><br/><br/>
                        <input type="submit" class="btn" value="Sign In"></input><br/><br/>
                    </h2>
                    <p class="bottom">Dont't have an account?  <a class="bottom"> Sign Up here</a></p>
                </div>
            </div>
        </body>
    );
}

export default login;
