import React, { Component, Fragment } from 'react';
import axios from 'axios';

axios.defaults.withCredentials = true;

class Loginpage extends Component
{
	login_procedure()
	{
		var b1 = document.getElementById("username");
		var b2 = document.getElementById("password");
		
		if(b1.value!=="" && b2.value!=="")
		{
			var details = {"username": b1.value, "password": b2.value};
			//alert(details);
			axios.post("http://127.0.0.1:8000/users/login", {"username": b1.value, "password": b2.value}, { withCredentials: false })
			.then(function(response){
				console.log(response)});
		}
		
		else
		{
			alert("Please make sure all fields are filled");
		}
	}
	
	render()
	{
		return(
			<Fragment>
			<div id="pagetitle">Treebase</div>
			<div id="div1" className="field">
			<div className="fieldname">Username</div>
			<input type="text" name="username" id="username" className="inputfield"/>
			</div>
			<div id="div2" className="field">
			<div className="fieldname">Password</div>
			<input type="text" name="password" id="password" className="inputfield"/>
			</div>
			<div id="loginbutton" onClick={this.login_procedure}>Log in</div>
			</Fragment>
		);
	}
}

export default Loginpage;