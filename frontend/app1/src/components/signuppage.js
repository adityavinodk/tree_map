import React, { Component, Fragment } from 'react';
import axios from 'axios';

axios.defaults.withCredentials = true;

class Signuppage extends Component
{
	signup_procedure()
	{
		var i1 = document.getElementById("signup_username").value;
		var i2 = document.getElementById("signup_password").value;
		
		if(i1!=="" && i2!=="")
		{
			var details = {"username": i1, "password": i2, "location": [1,2]};
			//alert(details);
			axios.post("http://127.0.0.1:8000/users/signup", details, { withCredentials: false })
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
			<React.Fragment>
				<div id="pagetitle">Treebase</div>
				<div id="su_input1" className="field">
				<div className="fieldname">Username</div>
				<input type="text" name="username" id="signup_username" className="inputfield"/>
				</div>
				<div id="su_input2" className="field">
				<div className="fieldname">Password</div>
				<input type="text" name="password" id="signup_password" className="inputfield"/>
				</div>
				<div id="signupbutton" onClick={this.signup_procedure}>Sign up!</div>
			</React.Fragment>
		);
	}
}

export default Signuppage;