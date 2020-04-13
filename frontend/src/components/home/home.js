import React from 'react';
import axios from 'axios';
// import {Link, Redirect} from 'react-router-dom';
import {loginUser, logoutUser} from '../../actions/authActions';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';
import { ToastsContainer, ToastsStore } from 'react-toasts';
import MapComponent from '../mappage/map.js';
import { transform } from 'ol/proj';
import '../../styles/styling.css';

class Home extends React.Component {
    constructor() {
        super();
        this.state = {
            username: '',
            password: '',
            name: '',
            isLogin: false,
            loading: false,
            isLoggedIn: false
        }
        this.onLogin = this.onLogin.bind(this);
        this.onSignUp = this.onSignUp.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.onLogout = this.onLogout.bind(this);
        this.logginIn = this.logginIn.bind(this);
        this.signingUp = this.signingUp.bind(this);
        this.validateUser = this.validateUser.bind(this);
        this.setValidationCaller = null;
        this.callValidation = this.callValidation.bind(this);
		this.onPlant = this.onPlant.bind(this);
		
		this.MapRef = React.createRef();
    }

    handleChange(event) {
        event.preventDefault()
        this.setState({ [event.target.name]: event.target.value })
    }

    callValidation() {
        this.setValidationCaller = setInterval(this.validateUser, 4000);
    }

    onLogin(event) {
        event.preventDefault();
        
        const user_details = {
            username: this.state.username,
            password: this.state.password
        };

        axios.post("http://127.0.0.1:8000/api/users/login", user_details, {
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then((res)=>{
            if(res.data.success){
                ToastsStore.success(res.data.message);
				console.log(res);
                this.props.loginUser(res.data);
                this.setState({
                    isLoggedIn: true
                })
                setTimeout(this.callValidation, 5000);
            }
        })
        .catch(err => {
            console.log(err);
            if(err.response.status === 404){
                ToastsStore.error('User not found')
            }
            else if(err.response.status === 400){
                ToastsStore.error('Invalid credentials')
            }
        })
    }    

    onSignUp(event) {
        event.preventDefault();
		var onSignUpState = this;
		navigator.geolocation.getCurrentPosition(function(position){
            var user_loc = transform([position.coords.latitude, position.coords.longitude], 'EPSG:4326','EPSG:3857');
        
            const user_details = {
                username: onSignUpState.state.username,
                password: onSignUpState.state.password,
                location: user_loc
            };

            axios.post("http://127.0.0.1:8000/api/users/signup", user_details, {
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then((res)=>{
                if(res.data.success){
                    onSignUpState.props.loginUser(res.data);
                    ToastsStore.success(res.data.message);
                    onSignUpState.setState({
                        isLoggedIn: true
                    })
                    setTimeout(this.callValidation, 5000);
                }
            })
            .catch(err => {
                console.log(err);
                if(err.response.status === 409){
                    ToastsStore.error('User already exists')
                }
            });
        });
    }

    validateUser() {
        axios.get("http://127.0.0.1:8000/api/users/validate", {
            headers: {
                'token': this.props.auth.token,
                'Content-Type': 'application/json'
            }
        })
        .catch(err => {
            console.log(err);
            this.props.logoutUser();
            this.setState({
                username: '',
                password: '',
                isLoggedIn: false
            })
            clearInterval(this.setValidationCaller);
            ToastsStore.error("Token error, login again")
        })
    }
	
    onLogout(event) {
        event.preventDefault();
        axios.post("http://127.0.0.1:8000/api/users/logout", null, {
            headers: {
                'Content-Type': 'application/json',
                'token': this.props.auth.token
            }
        })
        .then((res)=>{
            if(res.data.success){
                this.props.logoutUser();
                this.setState({
                    username: '',
                    password: '',
                    isLoggedIn: false
                })
                clearInterval(this.setValidationCaller);
            }
        })
        .catch(err => {
            console.log(err);
        })
    }
	
	onPlant(event)
	{		
		event.preventDefault();
		var onPlantState = this;
		
		//this.renderMap();
		
		if(navigator.geolocation)
		{
			navigator.geolocation.getCurrentPosition(function(position){
                var MercatorLocation;

                // Uncomment below line to take user's location
                MercatorLocation = transform([position.coords.latitude, position.coords.longitude], 'EPSG:4326','EPSG:3857');
    
                // randomizing code to avoid skewed clusters
                // comment below line to take user location
				
				//alert(MercatorLocation);
				
				MercatorLocation = [Math.random() * (8649411 - 8628627) + 8628627, Math.random() * (1464905 - 1449195) + 1449195];
				
				var loc_json = {"location": MercatorLocation};
				
				axios.post('http://127.0.0.1:8000/api/tree/plant', loc_json, {
					headers: {
						'Content-Type': 'application/json',
						'token': onPlantState.props.auth.token
					}
				})
				.then(function(response){
                    
					console.log(response);
					//onPlantState.MapRef.current.setState({flag: onPlantState.MapRef.current.flag + 1});
					
					//alert("Hoola");
					
					console.log(loc_json);
					onPlantState.MapRef.current.rerender();
					ToastsStore.success('Well Done! You have planted a tree!');
					
				}).catch(err => {console.log(err)});
			});
		}
	}

    logginIn(event){
        event.preventDefault();
        this.setState({
            isLogin: true,
            username: '',
            password: ''
        })
    }

    signingUp(event){
        event.preventDefault();
        this.setState({
            isLogin: false,
            username: '',
            password: ''
        })
    }

    render(){
        var isAuthenticated = this.props.auth.isAuthenticated;
        var isLogin = this.state.isLogin;
        var isLoggedIn = this.state.isLoggedIn;
        var content;

        var loginFormContent = (
			<div className="wrapper">
				<div className="formDiv">
					<div className="titleDiv">
					<a className="pageTitle" href="/">
						TREEBASE
					</a>
					<br/>
					<br/>
					</div>
					<div className="formHeading">
						<div>
							Log in
						</div>
					</div>
					<br/>
					<br/>
					<br/>
					<form onSubmit={this.onLogin}>
						<div className='form-group'>
							<div className="divDiv">
								Username
							</div>
							<br/>
							<input
								type='text'
								id='username'
								className='formImput'
								name='username'
								value={this.state.username}
								onChange={this.handleChange}
								required
							/>
						</div>
						<br/>
						<br/>
						<div className='form-group'>
							<div className="divDiv">
								Password
							</div>
							<br/>
							<input
								type='text'
								id='password'
								className='formInput'
								name='password'
								value={this.state.password}
								onChange={this.handleChange}
								required
							/>
						</div>
						<br/>
						<br/>
						<br/>
						<button
							type='submit'
							className='mainButton'
							disabled={this.state.loading}
						>Log in!</button>

						<br/><br/>

						<button
							onClick={this.signingUp}
							className='smallButton'
						>Signup instead?</button>
					</form>
				</div>
				<MapComponent ref={this.MapRef}/>
			</div>
        )

        var signUpFormContent = (
			<div className="wrapper">
				<div className="formDiv">
					<div className="titleDiv">
					<a className="pageTitle" href="/">
						TREEBASE
					</a>
					</div>
					<br/>
					<div className="formHeading">
						<div>
							Sign up
						</div>
					</div>
					<br/>
					<br/>
					<br/>
					<br/>
					<form onSubmit={this.onSignUp}>
						<div className='form-group'>
							<div className="divDiv">
								Username
							</div>
							<br/>
							<input
								type='text'
								id='username'
								className='formInput'
								name='username'
								value={this.state.username}
								onChange={this.handleChange}
								required
							/>
						</div>
						<br/>
						<br/>
						<div className='form-group'>
							<div className="divDiv">
								Password
							</div>
							<br/>
							<input
								type='text'
								id='password'
								className='formInput'
								name='password'
								value={this.state.password}
								onChange={this.handleChange}
								required
							/>
						</div>
						<br/>
						<br/>
						<br/>
						<br/>
						<button
							type='submit'
							className='btn btn-success mainButton'
							disabled={this.state.loading}
						>Sign up!</button>
						
						<br/><br/>

						<button
							onClick={this.logginIn}
							className='btn btn-primary smallButton'
						>Login instead?</button>
					</form>
				</div>
				<MapComponent ref={this.MapRef}/>
			</div>
        )
		
		const style = {
			position: 'absolute',
			top: '0px',
			left: '25%',
            width: '75%',
            height: '100%',
            backgroundColor: '#cccccc',
        }

        var homeContent = (
			<div>
				<div className='formDiv'>
					<h1>Welcome!</h1>
					<p>Plant a tree at your current location</p>
					<button
						onClick={this.onPlant}
						className="mainButton"
					>Planted!</button>
					<br/>
					<button
						onClick={this.onLogout}
						className='btn btn-success smallButton'
						disabled={this.state.loading}
					>Logout</button>
				</div>
				<MapComponent ref={this.MapRef}/>
			</div>
        )

        if(isAuthenticated) {content = homeContent;}
        else if(isLogin) {content = loginFormContent;}
        else {content = signUpFormContent;}

        return (
            <div id="motherDiv">
				<link href="https://fonts.googleapis.com/css2?family=Space+Mono&display=swap" rel="stylesheet"></link>
				<link href="https://fonts.googleapis.com/css2?family=Scope+One&display=swap" rel="stylesheet"></link>
				<link href="https://fonts.googleapis.com/css2?family=Comfortaa&display=swap" rel="stylesheet"></link>
				<link href="https://fonts.googleapis.com/css2?family=Anton&display=swap" rel="stylesheet"></link>
				<link href="https://fonts.googleapis.com/css2?family=Montserrat&display=swap" rel="stylesheet"></link>
				<link href="https://fonts.googleapis.com/css2?family=Lato&display=swap" rel="stylesheet"></link>
                {content}
                <ToastsContainer store={ToastsStore} />
            </div>
        )
    }
}

Home.propTypes = {
    auth: PropTypes.object.isRequired,
    loginUser: PropTypes.func.isRequired,
    logoutUser: PropTypes.func.isRequired
}

const mapStateToProps = state => ({
    auth: state.auth,
});

export default connect(mapStateToProps, { loginUser, logoutUser })(Home);