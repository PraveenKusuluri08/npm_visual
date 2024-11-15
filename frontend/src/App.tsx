import "./App.css";
import { ForceGraph3D } from "react-force-graph";
import GraphData from "./utils/models";
import { useEffect } from "react";
import GraphDiagram from "./components/GraphDiagram";
import Crudbar from "./components/Crudbar";
import { useState } from "react";
import { getCache } from "./utils/cache";
import axios from "axios";

function App() {
  const [packageName, setPackageName] = useState("");

  const onPackageChanged = (packageName: string) => {
    setPackageName(packageName);
  };

  const [graphData, setGraphData] = useState<GraphData>();
  useEffect(() => {
    if (packageName != "") {
      console.log("setting axios call");
      let url;
      if (packageName == "getPopularNetwork") url = "/api/getPopularNetworks";
      else url = `/api/getNetwork/${packageName}`;
      // Prevent many calls to the same API.
      const apiCache = getCache();
      if (!apiCache.doesCallExist(url)) {
        apiCache.addCall(url);
        axios
          .get(url)
          .then((data) => {
            console.log("setting package data");
            setGraphData(data.data);
            console.log("graph data set" + data.data);
          })
          .catch((error) => {
            console.log("Error fetching data", error);
          })
          .finally(() => {
            apiCache.removeCall(url);
          });
      } else {
        console.log(
          `did not sent request to ${url}, request already in progress`,
        );
      }
    }
  }, [packageName]);

  return (
    <>
      <Crudbar onSelect={onPackageChanged} />
      <div className="page">
        <GraphDiagram graphData={graphData} />
        <ForceGraph3D graphData={graphData} />
      </div>
    </>
  );
}

export default App;
