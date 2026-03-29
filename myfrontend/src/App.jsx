import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Projects from './pages/Projects'
import Reports from './pages/Reports'
import Budgets from './pages/Budgets'
import Team from './pages/Team'
import SignIn from './pages/Auth/SignIn'
import SignUp from './pages/Auth/SignUp'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />

        <Route path="/app" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="transactions" element={<Transactions />} />
          <Route path="projects" element={<Projects />} />
          <Route path="reports" element={<Reports />} />
          <Route path="budgets" element={<Budgets />} />
          <Route path="team" element={<Team />} />
          <Route path="settings" element={<Navigate to="/app" />} />
        </Route>
        
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
