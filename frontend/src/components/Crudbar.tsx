import axios from "axios";
// import useFetchGraphData from "../hooks/useFetch";
import "./Crudbar.css";
import { useState } from "react";
import { Query } from "@/query";
import { Button } from "./ui/button";
import { Input } from "./ui/input";

function Crudbar({ onSelect }: { onSelect: any }) {
	const [query, setQuery] = useState<Query>(new Query());
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
