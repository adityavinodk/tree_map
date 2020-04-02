import React from 'react'
import {render} from 'react-dom';
import {
    BrowserRouter as Router,
    Route,
    Switch
} from 'react-router-dom'
// import PrivateRoute from './components/common/PrivateRoute';
import {store} from './store/store';
import App from './components/app/app';
import Home from './components/home/home';
import {Provider} from 'react-redux';
import './styles/index.css';

render((
    <Provider store={store}>
        <Router>
            <App>
                <div className = 'container'>
                    <Switch>
                        <Route exact path='/' component={Home} />
                    </Switch>
                </div>
            </App>
        </Router>
    </Provider>
), document.getElementById('root'))