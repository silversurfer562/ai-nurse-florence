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

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="clinical-trials" element={<ClinicalTrials />} />
        <Route path="disease-info" element={<DiseaseInfo />} />
        <Route path="literature" element={<LiteratureSearch />} />
        <Route path="drug-interactions" element={<DrugInteractions />} />
        <Route path="patient-education" element={<PatientEducation />} />
        <Route path="medical-glossary" element={<MedicalGlossary />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App