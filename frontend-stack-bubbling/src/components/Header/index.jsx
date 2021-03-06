import React, { Component } from "react";
import MyNavLink from "../MyNavLink";
import './index.css'
import MainLogo from '../Header/SBLogo.png';
import IMG_NoNotification from "../../assets/NotificationNone.png"
import IMG_Notifications from "../../assets/NotificationMultiple.png"
import axios from "axios";


export default class Header extends Component {
  constructor(props) {
    super();
    this.state = {
      isLoginUser: false,
      username: localStorage.getItem("username"),
      newNotifications: false
    };
    this.handleLogout = this.handleLogout.bind(this);
  }
  componentDidMount() {
    this.fetchNotifications();
    console.log(localStorage.getItem("access_token"));
    if (localStorage.getItem("access_token")) {
      console.log("true user logined");
      this.setState({
        isLoginUser: true,
      });
    }
  }

  handleLogout() {
    localStorage.removeItem("access_token");
    if (localStorage.getItem("access_token") == null) {
      console.log("yes the access token is removed");
    }
    window.location.reload(true)
    
  }

  fetchNotifications(){

    const token = localStorage.getItem("access_token");

    axios
    .get("http://localhost:5000/notifications",
          {
            headers: {
              'Authorization' : 'Bearer ' + token
            }
          }
        )
    .then((response) => {
      const stat = response.status
      if(stat === 200)
      {
        if(response.data.length != 0)
          this.setState({newNotifications:true})
      }
      }
    )
    .catch(error => console.log(error))
  }

  render() {
    let displaytext = 'Welcome, ' + this.state.username + '!';
    let usernamedisplay;
    if (this.state.isLoginUser)
      {
        usernamedisplay = <span className="userdisplay">
                    <h3>{displaytext}</h3>
                  </span>
      }

    return (
      <nav className="navbar navbar-expand-lg navbar-light">
        <div className="container-fluid Header">
          <div className="outer-container">
            {this.state.isLoginUser ? (
              <span className="HeaderInnerContainer">
                <ul className="navbar-nav">
                  <li >
                    <img className="HeaderLogo" src={MainLogo} width="200"/>
                  </li>
                  <li className="tab">
                    <MyNavLink replace to="/home" className="link">
                      Home
                    </MyNavLink>
                  </li>
                  <li className="tab">
                    <MyNavLink  replace to="" onClick={this.handleLogout} className="link">
                      Log Out
                    </MyNavLink>
                  </li>
                  <li className="tab">
                    <MyNavLink  replace to="/notifications" className="linkWithImage">
                      {this.state.newNotifications 
                      ? 
                      (<img className="notifImg" src={IMG_Notifications} width="25"/>) 
                      : 
                      (<img className="notifImg" src={IMG_NoNotification} width="25"/>)
                      }
                    </MyNavLink>
                  </li>
                  
                </ul>
                
              </span>
            ) : (
              <span>
                <ul className="navbar-nav">
                  <li >
                   <img className="HeaderLogo" src={MainLogo} width="200"/>
                  </li>
                  <li className="tab">
                    <MyNavLink replace to="/home" className="link">
                      Home
                    </MyNavLink>
                  </li>
                  <li className="tab">
                    <MyNavLink  replace to="/login" className="link">
                     Login
                    </MyNavLink>
                  </li>
                  <li className="tab">
                    <MyNavLink replace to="/register" className="link">
                     Register
                    </MyNavLink>
                  </li>
                </ul>
                
              </span>
              
            )}
            
          </div>
          {usernamedisplay}
        </div>
      </nav>
    );
  }
}
