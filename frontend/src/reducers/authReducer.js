import {SET_CURRENT_USER, LOGOUT_USER} from '../actions/types';
import isEmpty from '../utils/isEmpty';

const initial_state = {
    isAuthenticated: false,
    token: "",
    user_id: ""
}

export default function(state = initial_state, action) {
    switch(action.type){
        case SET_CURRENT_USER:
            return {
                ...state,
                isAuthenticated: !isEmpty(action.payload.token),
                user_id: action.payload.user_id,
                token: action.payload.token
            };
        case LOGOUT_USER:
            return initial_state;
        default:
            return state
    }
}