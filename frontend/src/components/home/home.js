import React from 'react';
import axios from 'axios';
// import {Link, Redirect} from 'react-router-dom';
import {loginUser, logoutUser} from '../../actions/authActions';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';
import { ToastsContainer, ToastsStore } from 'react-toasts';

class Home extends React.Component {
    constructor() {
        super();
        this.state = {
            username: '',
            password: '',
            name: '',
            isLogin: false,
            loading: false
        }

        this.onLogin = this.onLogin.bind(this);
        this.onSignUp = this.onSignUp.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.onLogout = this.onLogout.bind(this);
        this.logginIn = this.logginIn.bind(this);
        this.signingUp = this.signingUp.bind(this);
    }

    handleChange(event) {
        event.preventDefault()
        this.setState({ [event.target.name]: event.target.value })
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
                this.props.loginUser(res.data);
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
        
        const user_details = {
            username: this.state.username,
            password: this.state.password,
            location: [0,0]
        };

        axios.post("http://127.0.0.1:8000/api/users/signup", user_details, {
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then((res)=>{
            if(res.data.success){
                this.props.loginUser(res.data);
                ToastsStore.success(res.data.message);
            }
        })
        .catch(err => {
            console.log(err);
            if(err.response.status === 409){
                ToastsStore.error('User already exists')
            }
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
                    password: ''
                })
            }
        })
        .catch(err => {
            console.log(err);
        })
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
        var content;

        var loginFormContent = (
            <div>
                <div>
                    <div className='container w-50 mb-5 display-4'>
                        Login
                    </div>
                </div>

                <form className='container w-50' onSubmit={this.onLogin}>
                    <div className='form-group'>
                        <label className='form-inline'>
                            Username
                        </label>
                        <input
                            type='text'
                            id='username'
                            className='form-control'
                            name='username'
                            value={this.state.username}
                            onChange={this.handleChange}
                            required
                        />
                    </div>
                
                    <div className='form-group'>
                        <label className='form-inline'>
                            Password
                        </label>
                        <input
                            type='text'
                            id='password'
                            className='form-control'
                            name='password'
                            value={this.state.password}
                            onChange={this.handleChange}
                            required
                        />
                    </div>

                    <button
                        type='submit'
                        className='btn btn-success'
                        disabled={this.state.loading}
                    >Login</button>

                    <br/><br/>

                    <button
                        onClick={this.signingUp}
                        className='btn btn-primary'
                    >Signup instead?</button>
                </form>
            </div>
        )

        var signUpFormContent = (
            <div>
                <div>
                    <div className='container w-50 mb-5 display-4'>
                        Signup
                    </div>
                </div>

                <form className='container w-50' onSubmit={this.onSignUp}>
                    <div className='form-group'>
                        <label className='form-inline'>
                            Username
                        </label>
                        <input
                            type='text'
                            id='username'
                            className='form-control'
                            name='username'
                            value={this.state.username}
                            onChange={this.handleChange}
                            required
                        />
                    </div>
                
                    <div className='form-group'>
                        <label className='form-inline'>
                            Password
                        </label>
                        <input
                            type='text'
                            id='password'
                            className='form-control'
                            name='password'
                            value={this.state.password}
                            onChange={this.handleChange}
                            required
                        />
                    </div>

                    <button
                        type='submit'
                        className='btn btn-success'
                        disabled={this.state.loading}
                    >Signup</button>
                    
                    <br/><br/>

                    <button
                        onClick={this.logginIn}
                        className='btn btn-primary'
                    >Login instead?</button>
                </form>
            </div>
        )

        var homeContent = (
            <div className='text-center'>
                <h1>Welcome!</h1>
                <button
                    onClick={this.onLogout}
                    className='btn btn-success'
                    disabled={this.state.loading}
                >Logout</button>
            </div>
        )

        if(isAuthenticated) content = homeContent;
        else if(isLogin) content = loginFormContent;
        else content = signUpFormContent;

        return (
            <div>
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