import { TextField } from "@mui/material"
import { useEffect, useRef } from "react"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { initMorkMongoConnection, parsePortValue } from "../../configFormUtils"
import { portField } from "../../formValidation"
import { credentialPasswordField, credentialUsernameField, disableAutofillField } from "../../../../utils/credentialFieldProps"
import { GridSpan3, GridSpan9 } from "../AtomDBStyled"

export function MorkMongoSubForm({ onChange, category }) {
  const { getAtomdbTemplate } = useConfig()

  const form = useRef({
    type: "morkdb",
    ...initMorkMongoConnection(getAtomdbTemplate("morkdb"))
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
          required
          {...disableAutofillField}
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
          required
          defaultValue={form.current.mork_port}
          onChange={(e) => {
            form.current.mork_port = parsePortValue(e.target.value)
            notifyChange()
          }}
          {...portField}
        />
      </GridSpan3>

      <GridSpan9>
        <TextField
          fullWidth
          label="MongoDB Endpoint"
          size="small"
          required
          {...disableAutofillField}
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
          required
          defaultValue={form.current.mongo_port}
          onChange={(e) => {
            form.current.mongo_port = parsePortValue(e.target.value)
            notifyChange()
          }}
          {...portField}
        />
      </GridSpan3>

      <GridSpan3>
        <TextField
          fullWidth
          label="Mongo User"
          size="small"
          required
          {...credentialUsernameField}
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
          required
          {...credentialPasswordField}
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
