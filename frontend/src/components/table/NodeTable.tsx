import {
  ColumnDef,
  flexRender,
  Table as ReactTable,
} from "@tanstack/react-table"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table-scrollable";
import React from "react";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  table: ReactTable<TData>
}

export function NodeTable<TData, TValue>({
  columns,
  table,
}: DataTableProps<TData, TValue>) {
  const tableBodyRef = React.useRef<HTMLDivElement>(null)
  const wrapperRef = React.useRef<HTMLTableSectionElement>(null)

  const setHeight = () => {
    console.log("setHeight()")
    if (wrapperRef?.current && tableBodyRef?.current) {
      console.log("wrapperRef:  " + wrapperRef.current?.clientHeight)
      console.log("tableBodyRef: " + tableBodyRef.current?.clientHeight)
      tableBodyRef.current.style.height = wrapperRef.current.clientHeight + 'px'
      console.log(tableBodyRef.current.style.height)
    }
  }

  React.useEffect(() => {
    // console.log(ref)
    setHeight()
    const resizeObserver = new ResizeObserver(() => {
      setHeight()
    })
    console.log(tableBodyRef)
    if (wrapperRef?.current && tableBodyRef?.current) {
      console.log("tableBodyRef exists")
      resizeObserver.observe(wrapperRef.current)
    }
    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  return (
    <div ref={wrapperRef} className="rounded-md border grow">
      <Table ref={tableBodyRef} wrapperClassName="">
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}
                  </TableHead>
                );
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-state={row.getIsSelected() && "selected"}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
