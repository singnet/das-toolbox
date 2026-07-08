import { TableRow } from "@mui/material";
import { BodyCell } from "./servicestable.styled";

export function EmptyContent() {
  return (
    <TableRow>
      <BodyCell colSpan={9} align="center">
        No configured services for this machine
      </BodyCell>
    </TableRow>
  );
}