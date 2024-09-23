import axios from "axios";
// import useFetchGraphData from "../hooks/useFetch";


function Crudbar({ onSelect }: { onSelect: any }) {

  function scrapeAll() {
    const url = "/api/scrapeAll";
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

  return <div><h2>Temp component to call backend routes</h2>
    <button onClick={() => scrapeAll()}>Load and Save Everything</button>
    <form onSubmit={handleSubmit}>
      <label>
        Package to Graph:
        <input
          name="packageName"
          type="text"
          defaultValue="Express"
        />
      </label>
      <button type="submit" >Search</button>
    </form>
  </div>
}

export default Crudbar;
