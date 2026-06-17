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

export function MorkMongoOptions() {

  const { updateSection, getDefault } = useConfig()
  const { showToast } = useToast()

  const defaults = getDefault().atomdb || {}

  const section = useRef({
    type: "morkdb",
    morkdb: {
      endpoint: defaults?.morkdb?.endpoint || "localhost:40022"
    },
    mongodb: {
      endpoint: defaults?.mongodb?.endpoint || "localhost:40021",
      username: defaults?.mongodb?.username || "admin",
      password: defaults?.mongodb?.password || "admin",
      cluster: defaults?.mongodb?.cluster || false,
      cluster_secret_key: defaults?.mongodb?.cluster_secret_key || "",
      nodes: defaults?.mongodb?.nodes || []
    }
  })

  const [showMongo, setShowMongo] = useState(section.current.mongodb.cluster)

  return (
    <>
      <GridSpan9>
        <TextField
          fullWidth
          label="MorkDB Endpoint"
          size="small"
          disabled
          defaultValue="localhost"
          onChange={() => {}}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="MorkDB Port"
          type="number"
          size="small"
          defaultValue={section.current.morkdb.endpoint.split(":")[1]}
          onChange={() => {}}
        />
      </GridSpan3>

      <GridSpan9>
        <TextField
          fullWidth
          label="MongoDB Endpoint"
          size="small"
          disabled
          defaultValue="localhost"
          onChange={() => {}}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="MongoDB Port"
          type="number"
          size="small"
          defaultValue={section.current.mongodb.endpoint.split(":")[1]}
          onChange={() => {}}
        />
      </GridSpan3>

      <GridSpan6>
        <TextField
          fullWidth
          label="MongoDB Username"
          size="small"
          defaultValue={section.current.mongodb.username}
          onChange={() => {}}
        />
      </GridSpan6>

      <GridSpan6>
        <TextField
          fullWidth
          label="MongoDB Password"
          type="password"
          size="small"
          defaultValue={section.current.mongodb.password}
          onChange={() => {}}
        />
      </GridSpan6>

      <CheckboxContainer>
        <FormControlLabel
          label="Mongo Cluster"
          control={
            <Checkbox
              size="small"
              defaultChecked={section.current.mongodb.cluster}
              onChange={(e) => setShowMongo(e.target.checked)}
            />
          }
        />
      </CheckboxContainer>

      <ClusterGridContainer>
        {showMongo && (
          <ClusterForm
            type="mongo"
            onChange={() => {}}
          />
        )}
      </ClusterGridContainer>

      <ActionButtonContainer>
        <Button
          variant="contained"
          color="success"
          onClick={() => {}}
        >
          Save AtomDB Section
        </Button>
      </ActionButtonContainer>
    </>
  )
}