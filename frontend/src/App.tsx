import { useState } from "react";
import { GraphData, Node } from "./utils/models";
import Crudbar from "./components/Crudbar";
import BackendTools from "./components/BackendTools";
import NpmVisualGraph3d from "./components/NpmVisualGraph3d";
import { NodeTable } from "./components/table/NodeTableContainer";
import { columns } from "./components/table/columns";

const App = () => {
  const onResponseChanged = (data: GraphData) => {
    console.log(data);
    setGraphData(data);
    setTableData(data.nodes);
  };

  const [graphData, setGraphData] = useState<GraphData>();
  const [tableData, setTableData] = useState<Node[]>([]);

  /* 
  useEffect(() => {
    if (packageName !== "") {
      const url = `/analyzeNetwork/react`;
      axios
        .get(url)
        .then((data) => console.log("analysis results", data))
        .catch((err) => {
          console.log("error fetching data", err);
        });
    }
  }, [packageName]);
  */

  return (
    <div className="flex flex-col w-full h-full justify-between">
      <Crudbar onResponse={onResponseChanged} />
      <div className="flex flex-row grow shrink overflow-hidden">
        <div className="">
          <NodeTable columns={columns} data={tableData}></NodeTable>
        </div>
        <NpmVisualGraph3d graphData={graphData}></NpmVisualGraph3d>
      </div>
      <BackendTools></BackendTools>
    </div>
  );
};

export default App;
