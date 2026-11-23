import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import { NotFound } from './components/Status.jsx'
import StageDetail from './pages/StageDetail.jsx'
import MindMap from './pages/MindMap.jsx'

// Old /mindmap, /roadmap and /resources links now land on Home, keeping ?track=.
function HomeRedirect() {
  const { search } = useLocation()
  return <Navigate to={{ pathname: '/', search }} replace />
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<MindMap />} />
        <Route path="stages/:stageId" element={<StageDetail />} />
        <Route path="mindmap" element={<HomeRedirect />} />
        <Route path="roadmap" element={<HomeRedirect />} />
        <Route path="resources" element={<HomeRedirect />} />
        <Route path="about" element={<Navigate to="/" replace />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
