import axios from "axios";
// import useFetchGraphData from "../hooks/useFetch";
import './Crudbar.css';

function Crudbar({ onSelect }: { onSelect: any }) {

  function scrapeAll() {
    const url = "/api/scrapeAll";
    axios.get(url)
  }
  function clearCache() {
    const url = "/api/clearCache";
    axios.get(url)
  }

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const input = form.elements.namedItem('packageName') as HTMLInputElement;
    const packageName = input.value;
    onSelect(packageName)
    // alert("you want to search " + packageName)
    // const url = `/api/dependencies/${packageName}`;
    // useFetchGraphData(url);
    // axios.get(url)
  }


  return <nav>
    <h2>NPM Visual</h2>
    <button className="button-48" onClick={() => clearCache()}>
      <span className="text">Clear Cache (for development)</span>
    </button>
    <button className="button-48" onClick={() => scrapeAll()}>
      <span className="text">Scrape Everything</span>
    </button>
    <form onSubmit={handleSubmit}>
      <label>
        Package to Graph:
        <input
          name="packageName"
          type="text"
          defaultValue="react"
        />
      </label>

      <button className="button-48" type="submit">
        <span className="text">Search</span>
      </button>
    </form>
  </nav>
}

export default Crudbar;
