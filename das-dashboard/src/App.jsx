import { ToastProvider } from './components/global_providers/ToastProvider.jsx'
import { ConfigurationProvider } from './components/global_providers/ConfigurationProvider.jsx'
import { BrowserRouter, Route, Routes } from 'react-router'

import './App.css'

import { Box } from "@mui/material"
import Navbar from "./components/top_nav_bar/NavBar.jsx"
import SetupDasPage from './pages/setup_das/SetupDas.jsx'
import DashboardPage from './pages/dashboard/Dashboard.jsx'
import DashboardContextProvider from './components/global_providers/DashboardContextProvider.jsx'
import ProfilePage from './pages/profile/ProfilePage.jsx'
import { DialogProvider } from './components/global_providers/DialogProvider.jsx'


function App() {

  return (
    <>
      <BrowserRouter>
        <Box sx={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
          <Navbar />
          <Box component="main" sx={{ flex: 1, minHeight: 0, overflow: "hidden" }}>
            <Routes>
                  <Route path='/configuration' element={
                    <DialogProvider>
                      <ToastProvider>
                        <ConfigurationProvider>
                          <SetupDasPage/>
                        </ConfigurationProvider>
                      </ToastProvider>
                    </DialogProvider>
                  }/>
                  <Route path='/profiles' element={
                    <DialogProvider>
                      <ToastProvider>
                        <ProfilePage />
                      </ToastProvider>
                    </DialogProvider>
                  }/>
                  <Route path='/dashboard' element={
                    <DialogProvider>
                      <ToastProvider>
                        <DashboardContextProvider>
                          <DashboardPage />
                        </DashboardContextProvider>
                      </ToastProvider>
                    </DialogProvider>
                  }/>
            </Routes>
          </Box>
        </Box>
      </BrowserRouter>
    </>
  )
  
}

export default App
