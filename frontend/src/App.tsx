import { useState } from "react";
import { GraphData } from "./utils/models";
import Crudbar from "./components/Crudbar";
import BackendTools from "./components/BackendTools";
import NpmVisualGraph3d from "./components/NpmVisualGraph3d";

const App = () => {
	const onResponseChanged = (data: GraphData) => {
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
		<div className="flex flex-col w-full h-full justify-between">
			<Crudbar onResponse={onResponseChanged} />
			<div className="grow shrink">
				<NpmVisualGraph3d graphData={graphData}></NpmVisualGraph3d>
			</div>
			<BackendTools></BackendTools>
		</div>
	);
};

export default App;
