import React, { Component } from "react";
import Popup from '../../components/Popup'
import MyNavLink from '../../components/MyNavLink'
import axios from "axios";
import "./index.css";
import Header from '../../components/Header/'

export default class Login extends Component {
  constructor(props) {
    super();
    this.state = {
      email: "",
      password: "",
      loginMsg: "",
      tigger:false,
      isSuccess:true
    };

    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.setTiggerAlertBox = this.setTiggerAlertBox.bind(this);
  }

  setTiggerAlertBox(value){
    this.setState({
      tigger: value,
    });
  }

  handleChange(e) {
    this.setState({
      [e.target.name]: e.target.value,
    });
  }

  handleSubmit(e) {
    e.preventDefault();
    const { email, password } = this.state;
    
    axios
      .post("http://localhost:5000/login", {
        email: email,
        password: password,
      })
      .then((response) => {
        console.log(response)
        const res = response.status;
        if (res === 200) {
          localStorage.setItem("access_token", response.data.access_token);
          this.setState({
            loginMsg:response.data.message
          })
          this.props.history.push("/home")
          console.log("---------", localStorage.getItem("access_token"));
        }
        else if(res === 201){
          localStorage.setItem("access_token", response.data.access_token)
          localStorage.setItem("username", response.data.username)
          this.setState({
            loginMsg:response.data.message,
            isSuccess:true
          })
          this.props.history.push("/home")
          console.log("---------", localStorage.getItem("access_token"));
          console.log("---------", localStorage.getItem("username"));
        }
        else if(res === 203){
          this.setState({
            loginMsg:response.data.message,
            isSuccess:false
          })
        }
        this.setState({
          tigger: true,
        });
      })
      // clean the form
      this.setState({
        email:'',
        password:'',
      });
      console.log("-----",this.state)
      //this.props.history.push("/home")
  }

  render() {
    return (
      <div className="container-margin">
        <Header/>
        <div className="pagetitle">LOGIN</div>

        <Popup
          tigger={this.state.tigger}
          setTiggerAlertBox={this.setTiggerAlertBox}
          isSuccess={this.state.isSuccess}
        >
          {this.state.loginMsg}
        </Popup>

        <form onSubmit={this.handleSubmit}>
          <div className="form-floating mb-3">
            <input
              type="email"
              name="email"
              value={this.state.email}
              onChange={this.handleChange}
              className="form-control"
              id="floatingInput"
              placeholder="name@example.com"
              required
            />
            <label htmlFor="floatingInput">Email address</label>
          </div>
          <div className="form-floating">
            <input
              type="password"
              name="password"
              value={this.state.password}
              onChange={this.handleChange}
              className="form-control"
              id="floatingPassword"
              placeholder="Password"
              required
            />
            <label htmlFor="floatingPassword">Password</label>
          </div>

          <div>
            <button
              type="submit"
              className="btn btn-primary btn-lg button-position"
            >
              Login
            </button>
            <div className="word">
              <MyNavLink replace to="/register" className="bottomlink">
                Don't have an Account? Create one!
              </MyNavLink>
            </div>
          </div>
        </form>
      </div>
    );
  }
}
