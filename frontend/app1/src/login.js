function login_procedure()
{
	import axios from 'axios';

	alert("Hola");
	
	axios = require('axios');	
	
	uname = document.getElementById("username");
	pwd = document.getElementById("password");
	
	var send_json = {"username": uname, "password": pwd};
	axios.get().then(function(response){
		
	});
}