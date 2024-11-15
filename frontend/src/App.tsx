import "./App.css";
import GraphDiagram from "./components/GraphDiagram";
import Crudbar from "./components/Crudbar";
import { useState } from "react";

function App() {
  const [packageName, setPackageName] = useState("");

  const onPackageChanged = (packageName: string) => {
    setPackageName(packageName);
  };

  return (
    <>
      <Crudbar onSelect={onPackageChanged} />
      <div className="page">
        <GraphDiagram packageName={packageName} />
      </div>
    </>
  );
}

export default App;
