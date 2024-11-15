type GraphData = {
  packageName: string;
  directed: boolean;
  graph: object;
  links: [
    {
      source: string;
      target: string;
    },
  ];
  multigraph: boolean;
  nodes: [{ id: string }];
};

export default GraphData;

