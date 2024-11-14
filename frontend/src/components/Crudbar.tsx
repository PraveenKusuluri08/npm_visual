import axios from "axios";
// import useFetchGraphData from "../hooks/useFetch";
import "./Crudbar.css";
import { useRef, useState } from "react";
import { CopyTimestamp } from "./CopyTimestamp";

function Crudbar({ onSelect }: { onSelect: any }) {
  function scrapeAll() {
    const url = "/api/data/scrapeAll";
    axios.get(url);
  }
  function clearCache() {
    const url = "/api/clearCache";
    axios.get(url);
  }
  function getPopularNetwork() {
    onSelect("getPopularNetwork");
  }

  function apiTest(path: string) {
    axios
      .get(`/api/${path}`)
      .then((r) => {
        console.log(r);
        const message = `status: $(r.status)`;
        alert(message);
      })
      .catch((r) => {
        console.log(r);
        alert(r);
      });
  }
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const input = form.elements.namedItem("packageName") as HTMLInputElement;
    const packageName = input.value;
    onSelect(packageName);
    // alert("you want to search " + packageName)
    const url = `/api/dependencies/${packageName}`;
    // useFetchGraphData(url);
    axios.get(url);
  };
  const [apiText, setApiText] = useState("data/deletePackages");

  return (
    <nav>
      <h2>NPM Visual</h2>
      <CopyTimestamp></CopyTimestamp>
      <div className="flex flex-col">
        <button className="button-48" onClick={() => apiTest(apiText)}>
          <span className="text">Test API</span>
        </button>
        <input
          defaultValue={apiText}
          onChange={(e) => setApiText(e.target.value)}
        />
      </div>
      <button className="button-48" onClick={() => clearCache()}>
        <span className="text">Clear Cache (for development)</span>
      </button>
      <button className="button-48" onClick={() => getPopularNetwork()}>
        <span className="text">Build Big Network</span>
      </button>
      <button className="button-48" onClick={() => scrapeAll()}>
        <span className="text">Scrape Everything</span>
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
