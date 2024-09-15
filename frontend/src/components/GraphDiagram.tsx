import useFetchGraphData from "../hooks/useFetch";
import * as d3 from "d3";
import { useEffect } from "react";

const GraphDiagram = () => {
  const url = "http://192.168.1.45:8080/api/dependencies/express";
  const graphData = useFetchGraphData(url);
  console.log(graphData);

  interface GraphNode extends d3.SimulationNodeDatum {
    id: string;
  }

  interface GraphLink {
    source: string | GraphNode;
    target: string | GraphNode;
  }

  // eslint-disable-next-line react-hooks/rules-of-hooks
  useEffect(() => {
    const width = 800;
    const height = 600;
    if (graphData !== undefined) {
      const svg = d3
        .select("#d3-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("transform", "translate(100px,200px)");

        // this creates a simulation with the array of nodes
        
      const simulation = d3
        .forceSimulation<GraphNode>(graphData.nodes)
        .force(
          "link",
          d3
            .forceLink<GraphNode, GraphLink>(graphData.links)
            .id((d: GraphNode) => d.id)
        )
        .force("charge", d3.forceManyBody().strength(-400))
        .force("center", d3.forceCenter(width / 2, height / 2));

      const link = svg
        .append("g")
        .selectAll("line")
        .data(graphData.links)
        .enter()
        .append("line")
        .attr("stroke", "#999");

      const node = svg
        .append("g")
        .selectAll("circle")
        .data(graphData.nodes)
        .enter()
        .append("circle")
        .attr("r", 10)
        .attr("fill", "#69b3a2")
        .call(
          d3
            .drag<SVGCircleElement, GraphNode>()
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded)
        );

      const label = svg
        .append("g")
        .selectAll("text")
        .data(graphData.nodes)
        .enter()
        .append("text")
        .attr("dx", 15)
        .attr("dy", ".35em")
        .text((d) => d.id);

      simulation.on("tick", () => {
        link
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          .attr("x1", (d: any) => (d.source as GraphNode).x!)
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          .attr("y1", (d: any) => (d.source as GraphNode).y!)
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          .attr("x2", (d: any) => (d.target as GraphNode).x!)
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          .attr("y2", (d: any) => (d.target as GraphNode).y!);

        node
          .attr("cx", (d: GraphNode) => d.x!)
          .attr("cy", (d: GraphNode) => d.y!);

        label
          .attr("x", (d: GraphNode) => d.x!)
          .attr("y", (d: GraphNode) => d.y!);
      });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      function dragStarted(event: any, d: GraphNode) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      function dragged(event: any, d: GraphNode) {
        d.fx = event.x;
        d.fy = event.y;
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      function dragEnded(event: any, d: GraphNode) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }
    }
  }, [graphData]);
  return (
    <div>
      Graph
      <div id="d3-container"></div>
    </div>
  );
};

export default GraphDiagram;