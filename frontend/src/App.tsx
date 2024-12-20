import { useState } from "react";
import { GraphData } from "./utils/models";
import Crudbar from "./components/Crudbar";
import BackendTools from "./components/BackendTools";
import NpmVisualGraph3d from "./components/NpmVisualGraph3d";
import { NodeTable } from "./components/NodeTable";
import { columns } from "./components/columns";

const App = () => {
	const onResponseChanged = (data: GraphData) => {
		console.log(data);
		setGraphData(data);
		const deepCopy = JSON.parse(JSON.stringify(data.nodes));
		console.log(deepCopy);
		setTableData(deepCopy);
	};

	const [graphData, setGraphData] = useState<GraphData>();
	const [tableData, setTableData] = useState<Array<{ id: string }>>([]);

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
				<div className="overflow-auto">
					<NodeTable columns={columns} data={tableData}></NodeTable>
				</div>
				<NpmVisualGraph3d graphData={graphData}></NpmVisualGraph3d>
			</div>
			<BackendTools></BackendTools>
		</div>
	);
};

export default App;
