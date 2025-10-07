import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ClinicalTrials from './pages/ClinicalTrials'
import DiseaseInfo from './pages/DiseaseInfo'
import LiteratureSearch from './pages/LiteratureSearch'
import DrugInteractions from './pages/DrugInteractions'
import PatientEducation from './pages/PatientEducation'
import MedicalGlossary from './pages/MedicalGlossary'
import Settings from './pages/Settings'

// Wizards
import SbarReport from './pages/SbarReport'
import DischargeInstructions from './pages/DischargeInstructions'
import MedicationGuide from './pages/MedicationGuide'
import IncidentReport from './pages/IncidentReport'

// Public Pages (No Auth Required)
import LandingPage from './pages/LandingPage'
import AboutUs from './pages/AboutUs'
import PublicDrugInteractions from './pages/PublicDrugInteractions'
import DrugInteractionDemo from './pages/DrugInteractionDemo'
import MedicationInteractionChecker from './pages/MedicationInteractionChecker'

function App() {
  return (
    <Routes>
      {/* Public Routes (No Authentication Required) */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/about" element={<AboutUs />} />
      <Route path="/drug-checker" element={<PublicDrugInteractions />} />
      <Route path="/demo-interactions" element={<DrugInteractionDemo />} />
      <Route path="/medication-checker" element={<MedicationInteractionChecker />} />

      {/* Authenticated Routes */}
      <Route path="/app" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="clinical-trials" element={<ClinicalTrials />} />
        <Route path="disease-info" element={<DiseaseInfo />} />
        <Route path="literature" element={<LiteratureSearch />} />
        <Route path="drug-interactions" element={<DrugInteractions />} />
        <Route path="patient-education" element={<PatientEducation />} />
        <Route path="medical-glossary" element={<MedicalGlossary />} />
        <Route path="settings" element={<Settings />} />

        {/* Clinical Wizards */}
        <Route path="sbar-report" element={<SbarReport />} />
        <Route path="discharge-instructions" element={<DischargeInstructions />} />
        <Route path="medication-guide" element={<MedicationGuide />} />
        <Route path="incident-report" element={<IncidentReport />} />
      </Route>

      {/* Legacy auth routes - redirect to /app */}
      <Route path="/login" element={<LandingPage />} />
      <Route path="/register" element={<LandingPage />} />
    </Routes>
  )
}

export default App