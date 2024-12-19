import { Button } from "./ui/button";
import React, { useState } from "react";

const BackendTools = () => {
	const [responseMessage, setResponseMessage] = useState<string>("");

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
	return (
		<div>
			<Button disabled={true} onClick={clearCache}>
				Clear Cache
			</Button>
			<Button onClick={scrapeEverything}>Scrape Everything</Button>
			<span>{responseMessage}</span>
		</div>
	);
};

export default BackendTools;
