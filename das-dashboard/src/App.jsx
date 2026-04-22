import { useState } from 'react'
import SetupDasPage from './pages/setup_das/SetupDas.jsx'
import './App.css'
import { ToastProvider } from './components/global_components/ToastProvider.jsx'
import { ConfigurationProvider } from './components/global_components/ConfigurationProvider.jsx'

function App() {

  return (
    <>
      <ToastProvider>
        <ConfigurationProvider>
          <SetupDasPage></SetupDasPage>
        </ConfigurationProvider>
      </ToastProvider>
    </>
  )
  
}

export default App
