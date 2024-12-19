import axios from "axios";
// import useFetchGraphData from "../hooks/useFetch";
// import "./Crudbar.css";
import { useState } from "react";
import { Query } from "@/query";
import { Button } from "./ui/button";
import { Input } from "./ui/input";

function Crudbar({ onSelect }: { onSelect: any }) {
	const [query, setQuery] = useState<Query>(new Query());

	const addPackage = () => {
		console.log("add Package");
	};

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
		<nav className="flex  flex-col bg-gradient-to-b from-black to-gray-800  w-full">
			<div className="flex flex-row justify-between items-center">
				<h2 className="text-white text-3xl">NPM Visual</h2>

				<Button className="button-48" onClick={() => getAllDBNetworks()}>
					<span className="text">getAllDBNetworks</span>
				</Button>
				<Button className="button-48" onClick={() => getPopularNetwork()}>
					<span className="text">getPopularNetwork</span>
				</Button>
				<div className="flex flex-row">
					<Button className="rounded-r-none border-2 border-r-0 border-black">
						Add Package:
					</Button>
					<Input
						className="grow-0 w-64 rounded-l-none border-2 border-l-0 border-black"
						defaultValue="react"
						onChange={addPackage}
					></Input>
				</div>
				<form onSubmit={handleSubmit}>
					<label>
						Package to Graph:
						<input name="packageName" type="text" defaultValue="react" />
					</label>

					<Button className="button-48" type="submit">
						Search
					</Button>
				</form>
			</div>
			<span>URL Text Here</span>
		</nav>
	);
}

export default Crudbar;
