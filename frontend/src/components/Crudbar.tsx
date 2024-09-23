import axios from "axios";

function scrapeAll() {
  const url = "/api/scrapeAll";
  axios.get(url)
}

function Crudbar() {
  return <div><h2>Temp component to call backend routes</h2>
    <button onClick={() => scrapeAll()}>Load and Save Everything</button>
  </div>
}

export default Crudbar;
