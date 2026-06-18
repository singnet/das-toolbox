import { TextField } from "@mui/material"
import { useEffect, useRef } from "react"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { GridSpan3 } from "../AtomDBStyled"

export function MorkMongoSubForm({ onChange, category }) {

  const { getDefault } = useConfig()

  const section = useRef({
    type: "morkdb",
    mork_port: Number(getDefault("atomdb.morkdb.endpoint")?.split(":")[1]) || 40022,
    mongo_port: Number(getDefault("atomdb.mongodb.endpoint")?.split(":")[1]) || 40021,
    mongo_username: getDefault("atomdb.mongodb.username") || "admin",
    mongo_password: getDefault("atomdb.mongodb.password") || "admin"
  })

  useEffect(() => {
    onChange(structuredClone(section.current), category)
  }, [])

  return (
    <>
      <GridSpan3>
        <TextField
          fullWidth
          label="MorkDB Port"
          size="small"
          type="number"
          defaultValue={section.current.mork_port}
          onChange={e => {
            section.current.mork_port = Number(e.target.value)
            onChange(structuredClone(section.current), category)
          }}
        />
      </GridSpan3>

      <GridSpan3>
        <TextField
          fullWidth
          label="Mongo Port"
          size="small"
          type="number"
          defaultValue={section.current.mongo_port}
          onChange={e => {
            section.current.mongo_port = Number(e.target.value)
            onChange(structuredClone(section.current), category)
          }}
        />
      </GridSpan3>

      <GridSpan3>
        <TextField
          fullWidth
          label="Mongo User"
          size="small"
          defaultValue={section.current.mongo_username}
          onChange={e => {
            section.current.mongo_username = e.target.value
            onChange(structuredClone(section.current), category)
          }}
        />
      </GridSpan3>

      <GridSpan3>
        <TextField
          fullWidth
          label="Mongo Pass"
          size="small"
          type="password"
          defaultValue={section.current.mongo_password}
          onChange={e => {
            section.current.mongo_password = e.target.value
            onChange(structuredClone(section.current), category)
          }}
        />
      </GridSpan3>
    </>
  )
}