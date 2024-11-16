import { ForceGraph3D } from "react-force-graph";

import { useEffect, useState, useRef } from "react";
import GraphData from "../utils/models";

const NpmVisualGraph3d = ({ graphData }: { graphData?: GraphData }) => {
  const graphRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setWindowSize(getCurrentSize);
  }, []);
  const getCurrentSize = () => {
    if (graphRef?.current) {
      const current = {
        width: graphRef.current?.clientWidth,
        height: graphRef.current?.clientHeight,
      };
      console.log(current);
      return current;
    } else return { width: 100, height: 100 };
  };

  const [windowSize, setWindowSize] = useState(getCurrentSize);
  // we use the useEffect hook to listen to the window resize event
  useEffect(() => {
    window.onresize = () => {
      console.log(graphRef.current?.clientWidth);
      return setWindowSize(getCurrentSize);
    };
  }, []);
  return (
    <div ref={graphRef} className="force-graph-inner-container">
      <ForceGraph3D
        width={windowSize.width}
        height={windowSize.height}
        graphData={graphData}
      />
    </div>
  );
};

export default NpmVisualGraph3d;
