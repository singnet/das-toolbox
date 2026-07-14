import { ToastProvider } from './components/global_providers/ToastProvider.jsx'
import { ConfigurationProvider } from './components/global_providers/ConfigurationProvider.jsx'
import { BrowserRouter, Route, Routes } from 'react-router'

import './App.css'

import { Box } from "@mui/material"
import NavBar from "./components/top_nav_bar/NavBar.jsx"
import SetupDasPage from './pages/setup_das/SetupDas.jsx'
import DashboardPage from './pages/dashboard/Dashboard.jsx'
import DashboardContextProvider from './components/global_providers/DashboardContextProvider.jsx'
import ProfilePage from './pages/profile/ProfilePage.jsx'
import QueryPage from './pages/query/QueryPage.jsx'
import { DialogProvider } from './components/global_providers/DialogProvider.jsx'


function App() {

  return (
    <>
      <BrowserRouter>
        <Box sx={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
          <NavBar />
          <Box component="main" sx={{ flex: 1, minHeight: 0, overflow: "hidden" }}>
            <Routes>
                  <Route path='/configuration' element={
                    <DialogProvider>
                      <ToastProvider>
                        <DashboardContextProvider>
                          <ConfigurationProvider>
                            <SetupDasPage/>
                          </ConfigurationProvider>
                        </DashboardContextProvider>
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
                        <DashboardPage />
                      </ToastProvider>
                    </DialogProvider>
                  }/>
                  <Route path='/query' element={
                    <DialogProvider>
                      <ToastProvider>
                        <QueryPage />
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
