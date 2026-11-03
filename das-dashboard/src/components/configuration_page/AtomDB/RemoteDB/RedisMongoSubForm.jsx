import { TextField } from "@mui/material"
import { useEffect, useEffectEvent, useRef, useState } from "react"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { initRedisMongoConnection, parsePortValue } from "../../configFormUtils"
import { portField } from "../../formValidation"
import { credentialPasswordField, credentialUsernameField, disableAutofillField } from "../../../../utils/credentialFieldProps"
import { GridSpan3, GridSpan9 } from "../AtomDBStyled"

export function RedisMongoSubForm({ onChange, category, initialValues }) {
  const { getAtomdbTemplate } = useConfig()

  const [initialForm] = useState(() => ({
    type: "redismongodb",
    ...initRedisMongoConnection(initialValues || getAtomdbTemplate("redismongodb"))
  }))
  const form = useRef({ ...initialForm })

  const notifyChange = () => {
    onChange(structuredClone(form.current), category)
  }

  const notifyInitialChange = useEffectEvent(notifyChange)
  useEffect(() => { notifyInitialChange() }, [])

  return (
    <>
      <GridSpan9>
        <TextField
          fullWidth
          label="Redis Endpoint"
          size="small"
          required
          {...disableAutofillField}
          defaultValue={initialForm.redis_endpoint}
          onChange={(e) => {
            form.current.redis_endpoint = e.target.value
            notifyChange()
          }}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="Redis Port"
          size="small"
          type="number"
          required
          defaultValue={initialForm.redis_port}
          onChange={(e) => {
            form.current.redis_port = parsePortValue(e.target.value)
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
          defaultValue={initialForm.mongo_endpoint}
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
          defaultValue={initialForm.mongo_port}
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
          defaultValue={initialForm.mongo_username}
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
          required
          {...credentialPasswordField}
          defaultValue={initialForm.mongo_password}
          onChange={(e) => {
            form.current.mongo_password = e.target.value
            notifyChange()
          }}
        />
      </GridSpan3>
    </>
  )
}
