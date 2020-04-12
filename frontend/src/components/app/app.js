import React from 'react';
import '../../styles/App.css';
// import Link from 'react-router-dom';
import Header from '../layout/header';
import Footer from '../layout/footer';

const App = ({ children }) => (
    <div className="app-wrapper">
    
          <main
            style={{
              overflow: 'hidden',
              display: 'block',
              position: 'relative',
			  height: '100%'
            }}
          >
            {children}
          </main>
		  
    </div>
  );
  
  export default App;