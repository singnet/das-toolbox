import { TextField } from "@mui/material"
import { useEffect, useRef } from "react"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { initMorkMongoConnection } from "../../configFormUtils"
import { GridSpan3, GridSpan9 } from "../AtomDBStyled"

export function MorkMongoSubForm({ onChange, category }) {
  const { getDefault } = useConfig()

  const form = useRef({
    type: "morkdb",
    ...initMorkMongoConnection(getDefault)
  })

  const notifyChange = () => {
    onChange(structuredClone(form.current), category)
  }

  useEffect(() => {
    notifyChange()
  }, [])

  return (
    <>
      <GridSpan9>
        <TextField
          fullWidth
          label="MorkDB Endpoint"
          size="small"
          defaultValue={form.current.mork_endpoint}
          onChange={(e) => {
            form.current.mork_endpoint = e.target.value
            notifyChange()
          }}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="MorkDB Port"
          size="small"
          type="number"
          defaultValue={form.current.mork_port}
          onChange={(e) => {
            form.current.mork_port = Number(e.target.value)
            notifyChange()
          }}
        />
      </GridSpan3>

      <GridSpan9>
        <TextField
          fullWidth
          label="MongoDB Endpoint"
          size="small"
          defaultValue={form.current.mongo_endpoint}
          onChange={(e) => {
            form.current.mongo_endpoint = e.target.value
            notifyChange()
          }}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="MongoDB Port"
          size="small"
          type="number"
          defaultValue={form.current.mongo_port}
          onChange={(e) => {
            form.current.mongo_port = Number(e.target.value)
            notifyChange()
          }}
        />
      </GridSpan3>

      <GridSpan3>
        <TextField
          fullWidth
          label="Mongo User"
          size="small"
          defaultValue={form.current.mongo_username}
          onChange={(e) => {
            form.current.mongo_username = e.target.value
            notifyChange()
          }}
        />
      </GridSpan3>

      <GridSpan3>
        <TextField
          fullWidth
          label="Mongo Pass"
          size="small"
          type="password"
          defaultValue={form.current.mongo_password}
          onChange={(e) => {
            form.current.mongo_password = e.target.value
            notifyChange()
          }}
        />
      </GridSpan3>
    </>
  )
}
