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
	const [packageName, setPackageName] = useState("");

	const onPackageChanged = (packageName: string) => {
		setPackageName(packageName);
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

	useEffect(() => {
		if (packageName != "") {
			console.log("setting axios call");
			let url;
			if (packageName == "getPopularNetwork") url = "/api/getPopularNetworks";
			else if (packageName == "getAllDBNetworks") url = "/api/getAllDBNetworks";
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

	console.log("graphData", graphData);

	return (
		<>
			<div className="page">
				<Crudbar onSelect={onPackageChanged} />
				<h1>{packageName}</h1>
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
