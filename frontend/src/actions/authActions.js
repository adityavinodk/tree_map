import {SET_CURRENT_USER, LOGOUT_USER} from './types';

// Action Creators
export const setCurrentUser = (token, user_id) => {
    return {
        type: SET_CURRENT_USER,
        payload: {
            token, user_id
        }
    }
}

export const logoutUserCreator = () => {
    return {
        type: LOGOUT_USER
    };
};

// Functions that call Action Creators
export const loginUser = user => dispatch => {
    localStorage.setItem('token', user.token);
    localStorage.setItem('user_id', user.user_id);
    dispatch(setCurrentUser(user.token, user.user_id));
}

export const logoutUser = () => dispatch => {
    localStorage.clear();
    dispatch(logoutUserCreator());
}