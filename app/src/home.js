import React from 'react';
import './App.css';
import video from "./main.webm";
import {useNavigate} from "react-router-dom";
import Login from './login';

function home(){
    return(
            <body class = 'layer'>
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
                <button 
                    onClick ={() => {
                    useNavigate('/login')
                    }}
                class = "buttonLogin4"
                >
                        <a class = "textLogin4"> LOGIN</a>
                </button>
                <button class = "buttonRegister4" type="submit">
                    <a class = "textRegister4" href="{{url_for('register')}}"> REGISTER</a>
                </button>
                <br/><br/>
                <div class="layer"> 
                        <h1 class = "TitleName4">RiftTracker</h1>
                        <div class="form4">
                            <form action="/" method="POST" autocomplete="off">
                                <div class = 'box4'>
                                <input type="text" placeholder="Search Summoner" name="SummonerName" required/>
                                <select name="region" id="region">
                                    <option value="NA1">NA1</option>
                                    <option value="EUW1">EUW1</option>
                                    <option value="EUN1">EUN1</option>
                                    <option value="BR1">BR1</option>
                                    <option value="LA1">LA1</option>
                                    <option value="LA2">LA2</option>
                                    <option value="OCE">OCE</option>
                                    <option value="RU1">RU1</option>
                                    <option value="TR1">TR1</option>
                                    <option value="JP1">JP1</option>
                                    <option value="KR">KR</option>
                                </select>
                                <button type="submit">
                                <i class="fa fa-search" aria-hidden="true" type="submit" ></i>
                                </button>
                                </div>
                            </form>
                        </div>
                    </div>
            </body>
    );
}

export default home;
