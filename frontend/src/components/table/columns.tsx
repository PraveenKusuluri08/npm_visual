import { ColumnDef } from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import { ArrowUpDown } from "lucide-react"


export const columns: ColumnDef<Node>[] = [
  {
    accessorKey: "id",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Name
          <ArrowUpDown />
        </Button>
      )
    },
  },
  {
    accessorKey: "outDegree",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          out Degree
          <ArrowUpDown />
        </Button>
      )
    },
  },
  {
    accessorKey: "betweennessCentrality",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Betweenness Centrality
          <ArrowUpDown />
        </Button>
      )
    },
  },
  {
    accessorKey: "inDegree",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          In Degree
          <ArrowUpDown />
        </Button>
      )
    },
  },
];
