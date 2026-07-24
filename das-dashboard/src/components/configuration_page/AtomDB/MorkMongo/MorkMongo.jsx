import { Checkbox, FormControlLabel, TextField } from "@mui/material"
import { useRef, useState } from "react"
import { ClusterForm } from "../ClusterForm"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { useToast } from "../../../global_providers/ToastProvider"
import { initMorkMongoConnection, parsePortValue } from "../../configFormUtils"
import { ConfigForm } from "../../ConfigForm"
import { portField } from "../../formValidation"
import { credentialPasswordField, credentialUsernameField, disableAutofillField } from "../../../../utils/credentialFieldProps"
import {
  GridSpan9,
  GridSpan3,
  GridSpan6,
  CheckboxContainer,
  ClusterGridContainer,
  ActionButtonContainer
} from "../AtomDBStyled"
import { SaveButton } from "../../Agents/Agents.styled"

export function MorkMongoOptions() {
  const { updateField, getAtomdbTemplate } = useConfig()
  const { showToast } = useToast()

  const form = useRef({
    atomdb_type: "morkdb",
    ...initMorkMongoConnection(getAtomdbTemplate("morkdb"), { withCluster: true })
  })

  const [showMongo, setShowMongo] = useState(form.current.mongo_cluster)

  const handleSave = () => {
    updateField("atomdb", structuredClone(form.current))
    showToast({ message: "AtomDB settings applied", severity: "success" })
  }

  return (
    <ConfigForm onSubmit={handleSave}>
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
          }}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="MorkDB Port"
          type="number"
          size="small"
          required
          defaultValue={form.current.mork_port}
          onChange={(e) => {
            form.current.mork_port = parsePortValue(e.target.value)
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
          }}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="MongoDB Port"
          type="number"
          size="small"
          required
          defaultValue={form.current.mongo_port}
          onChange={(e) => {
            form.current.mongo_port = parsePortValue(e.target.value)
          }}
          {...portField}
        />
      </GridSpan3>

      <GridSpan6>
        <TextField
          fullWidth
          label="MongoDB Username"
          size="small"
          required
          {...credentialUsernameField}
          defaultValue={form.current.mongo_username}
          onChange={(e) => {
            form.current.mongo_username = e.target.value
          }}
        />
      </GridSpan6>

      <GridSpan6>
        <TextField
          fullWidth
          label="MongoDB Password"
          size="small"
          required
          {...credentialPasswordField}
          defaultValue={form.current.mongo_password}
          onChange={(e) => {
            form.current.mongo_password = e.target.value
          }}
        />
      </GridSpan6>

      <CheckboxContainer>
        <FormControlLabel
          label="Mongo Cluster"
          control={
            <Checkbox
              size="small"
              checked={showMongo}
              onChange={(e) => {
                setShowMongo(e.target.checked)
                form.current.mongo_cluster = e.target.checked
              }}
            />
          }
        />
      </CheckboxContainer>

      <ClusterGridContainer>
        {showMongo && (
          <ClusterForm
            key="mork-mongo-cluster"
            type="mongo"
            initialNodes={form.current.mongo_nodes}
            onChange={(nodes) => {
              form.current.mongo_nodes = nodes
            }}
          />
        )}
      </ClusterGridContainer>

      <ActionButtonContainer>
        <SaveButton variant="contained" color="success" type="submit">
          Apply AtomDB settings
        </SaveButton>
      </ActionButtonContainer>
    </ConfigForm>
  )
}
