import axios from "axios";
// import useFetchGraphData from "../hooks/useFetch";
import "./Crudbar.css";
import { CopyTimestamp } from "./CopyTimestamp";

function Crudbar({ onSelect }: { onSelect: any }) {
	function getPopularNetwork() {
		onSelect("getPopularNetwork");
	}
	function getAllDBNetworks() {
		onSelect("getAllDBNetworks");
	}

	const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		const form = e.currentTarget;
		const input = form.elements.namedItem("packageName") as HTMLInputElement;
		const packageName = input.value;
		onSelect(packageName);
		// alert("you want to search " + packageName)
		const url = `/api/getNetwork/${packageName}`;
		// useFetchGraphData(url);
		axios.get(url);
	};

	return (
		<nav>
			<h2>NPM Visual</h2>
			<CopyTimestamp></CopyTimestamp>
			<button className="button-48" onClick={() => getAllDBNetworks()}>
				<span className="text">getAllDBNetworks</span>
			</button>
			<button className="button-48" onClick={() => getPopularNetwork()}>
				<span className="text">getPopularNetwork</span>
			</button>
			<form onSubmit={handleSubmit}>
				<label>
					Package to Graph:
					<input name="packageName" type="text" defaultValue="react" />
				</label>

				<button className="button-48" type="submit">
					<span className="text">Search</span>
				</button>
			</form>
		</nav>
	);
}

export default Crudbar;
