import './App.css'
import GraphDiagram from "./components/GraphDiagram"
import Crudbar from './components/Crudbar'
import { useState } from 'react'

function App() {

  const [packageName, setPackageName] = useState("express")

  const onPackageChanged = (packageName: string) => {
    setPackageName(packageName)
  }

  return (
    <>
      <p>{packageName}</p>
      <Crudbar onSelect={onPackageChanged} />
      <GraphDiagram packageName={packageName} />
    </>
  )
}

export default App
