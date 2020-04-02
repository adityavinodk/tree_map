import React from 'react';
import '../../styles/App.css';
// import Link from 'react-router-dom';
import Header from '../layout/header';
import Footer from '../layout/footer';

const App = ({ children }) => (
    <div className="app-wrapper">
      <Header />
          <main
            style={{
              paddingTop: '100px',
              paddingBottom: '50px',
              minHeight: '90vh',
              overflow: 'hidden',
              display: 'block',
              position: 'relative'
            }}
          >
            {children}
          </main>
      <Footer />
    </div>
  );
  
  export default App;