import { Button, Checkbox, FormControlLabel, TextField } from "@mui/material"
import { useRef, useState } from "react"
import { ClusterForm } from "../ClusterForm"
import { useConfig } from "../../../global_providers/ConfigurationProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { 
  GridSpan9, 
  GridSpan3, 
  GridSpan6, 
  CheckboxContainer, 
  ClusterGridContainer, 
  ActionButtonContainer 
} from "../AtomDBStyled"
import { SaveButton } from "../../Agents/Agents.styled";

export function MorkMongoOptions() {

  const { updateField, getDefault } = useConfig()
  const { showToast } = useToast()

  const section = useRef({
    atomdb_type: "morkdb",

    mork_endpoint: getDefault("atomdb.morkdb.endpoint")?.split(":")[0] || "localhost",
    mork_port: getDefault("atomdb.morkdb.endpoint")?.split(":")[1] || "40022",

    mongo_endpoint: getDefault("atomdb.mongodb.endpoint")?.split(":")[0] || "localhost",
    mongo_port: getDefault("atomdb.mongodb.endpoint")?.split(":")[1] || "40021",
    mongo_username: getDefault("atomdb.mongodb.username") || "admin",
    mongo_password: getDefault("atomdb.mongodb.password") || "admin",

    mongo_cluster: getDefault("atomdb.mongodb.cluster") || false,
    mongo_nodes: []
  })

  const [showMongo, setShowMongo] = useState(section.current.mongo_cluster)

  const handleSave = () => {
    updateField(
      "atomdb",
      structuredClone(section.current)
    )
    showToast({ message: "AtomDB settings applied", severity: "success" })
  }

  return (
    <>
      <GridSpan9>
        <TextField
          fullWidth
          label="MorkDB Endpoint"
          size="small"
          defaultValue={section.current.mork_endpoint}
          onChange={(e) => {
            section.current.mork_endpoint = e.target.value
          }}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="MorkDB Port"
          type="number"
          size="small"
          defaultValue={section.current.mork_port}
          onChange={(e) => {
            section.current.mork_port = Number(e.target.value)
          }}
        />
      </GridSpan3>

      <GridSpan9>
        <TextField
          fullWidth
          label="MongoDB Endpoint"
          size="small"
          defaultValue={section.current.mongo_endpoint}
          onChange={(e) => {
            section.current.mongo_endpoint = e.target.value
          }}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="MongoDB Port"
          type="number"
          size="small"
          defaultValue={section.current.mongo_port}
          onChange={(e) => {
            section.current.mongo_port = Number(e.target.value)
          }}
        />
      </GridSpan3>

      <GridSpan6>
        <TextField
          fullWidth
          label="MongoDB Username"
          size="small"
          defaultValue={section.current.mongo_username}
          onChange={(e) => {
            section.current.mongo_username = e.target.value
          }}
        />
      </GridSpan6>

      <GridSpan6>
        <TextField
          fullWidth
          label="MongoDB Password"
          type="password"
          size="small"
          defaultValue={section.current.mongo_password}
          onChange={(e) => {
            section.current.mongo_password = e.target.value
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
                section.current.mongo_cluster = e.target.checked
              }}
            />
          }
        />
      </CheckboxContainer>

      <ClusterGridContainer>
        {showMongo && (
          <ClusterForm
            type="mongo"
            onChange={(nodes) => {
              section.current.mongo_nodes = nodes
            }}
          />
        )}
      </ClusterGridContainer>

      <ActionButtonContainer>
        <SaveButton
          variant="contained"
          color="success"
          onClick={handleSave}
        >
          Save AtomDB Section
        </SaveButton>
      </ActionButtonContainer>
    </>
  )
}