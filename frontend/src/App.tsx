import { useEffect, useState } from "react";
import { getCache } from "./utils/cache";
import axios from "axios";
import NpmVisualGraph3d from "./components/NpmVisualGraph3d";
import GraphData from "./utils/models";
import Crudbar from "./components/Crudbar";
// import GraphDiagram from "./components/GraphDiagram";
import "./App.css";
import BackendTools from "./components/BackendTools";

const App = () => {
	const onResponseChanged = (data: any) => {
		console.log(data);
		setGraphData(data);
	};

	const [graphData, setGraphData] = useState<GraphData>();

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
		<>
			<div className="page">
				<Crudbar onResponse={onResponseChanged} />
				<div className="force-graph-3d-container">
					<NpmVisualGraph3d graphData={graphData}></NpmVisualGraph3d>
				</div>
				{/* <div className="force-graph-2d-container"> */}
				{/*   <GraphDiagram graphData={graphData} /> */}
				{/* </div> */}
				<BackendTools></BackendTools>
			</div>
		</>
	);
};

export default App;
