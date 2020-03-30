import React, { Fragment } from 'react';

function Homepage()
{
	return(
		<Fragment>
		<link rel="stylesheet" type="text/css" href="home.css" />
		<script src=""></script>
		<p id="sitename"> Treebase </p>
		<div id="button1" class="buttons"><a href="login.html" class="link">Login</a></div>
		<div id="button2" class="buttons"><a href="" class="link">Sign up</a></div>
		</Fragment>
	);
}

export default Homepage;