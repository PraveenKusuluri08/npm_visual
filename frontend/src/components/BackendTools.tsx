import { Button } from "./ui/button";
import { CopyTimestamp } from "./CopyTimestamp";
import React, { useState } from "react";
import { Input } from "./ui/input";

const BackendTools = () => {
	const [responseMessage, setResponseMessage] = useState<string>("");
	const [apiText, setApiText] = useState("data/test");

	const scrapeEverything = async () => {
		try {
			const response = await fetch("/api/data/scrapeAllPackages");
			if (!response.ok) {
				const message = "Failed to scrape data";
				setResponseMessage(message);
				throw new Error(message);
			}
			const data = await response.json();
			setResponseMessage(data);
		} catch (err) {
			console.error(err);
		}
	};

	const clearCache = async () => {
		try {
			const response = await fetch("/api/clearCache");
			if (!response.ok) {
				const message = "Failed to clear Cache";
				setResponseMessage(message);
				throw new Error(message);
			}
			const data = await response.json();
			setResponseMessage(data);
		} catch (err) {
			console.error(err);
		}
	};
	const testApi = async () => {
		try {
			const url = `/api/${apiText}`;
			const response = await fetch(url);
			if (!response.ok) {
				const message = `Failed to call ${url}`;
				setResponseMessage(message);
				throw new Error(message);
			}
			const data = await response.json();
			setResponseMessage(data);
		} catch (err) {
			console.error(err);
		}
	};
	return (
		<nav className="flex  flex-row gap-4 bg-gradient-to-t from-black to-gray-800  w-full">
			<CopyTimestamp></CopyTimestamp>
			<Button disabled={true} onClick={clearCache}>
				Clear Cache
			</Button>
			<Button onClick={scrapeEverything}>Scrape Everything</Button>
			<div className="flex flex-row">
				<Button
					className="rounded-r-none border-2 border-r-0 border-black"
					onClick={testApi}
				>
					Test Api:
				</Button>
				<Input
					className="grow-0 w-64 rounded-l-none border-2 border-l-0 border-black"
					defaultValue={apiText}
					onChange={(e) => setApiText(e.target.value)}
				></Input>
			</div>
			<span>{responseMessage}</span>
		</nav>
	);
};

export default BackendTools;
