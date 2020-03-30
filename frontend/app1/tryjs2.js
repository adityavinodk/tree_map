import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

class Sitename extends Component {
	render()
	{
		const headerstyle = {
			position: "absolute";
			left: "600px",
			top: "45px",
			fontFamily: "Candara",
			fontStyle: "italic",
			fontSize: "95px",
			textAlign: "center",
			color: "white"
		};
		
		return (
			<p style={headerstyle}> Treebase </p>
		);
	}
}

export default Sitename;