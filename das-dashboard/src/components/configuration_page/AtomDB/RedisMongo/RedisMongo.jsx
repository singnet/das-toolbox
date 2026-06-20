import { TextField, FormControlLabel, Checkbox } from "@mui/material"
import { useState, useRef } from "react"
import { ClusterForm } from "../ClusterForm"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { useToast } from "../../../global_providers/ToastProvider"
import { initRedisMongoConnection } from "../../configFormUtils"
import {
  GridSpan9,
  GridSpan3,
  GridSpan6,
  CheckboxContainer,
  ClusterGridContainer,
  ActionButtonContainer
} from "../AtomDBStyled"
import { SaveButton } from "../../Agents/Agents.styled"

export function RedisMongoOptions() {
  const { updateField, getDefault } = useConfig()
  const { showToast } = useToast()

  const form = useRef({
    atomdb_type: "redismongodb",
    ...initRedisMongoConnection(getDefault, "atomdb.", { withCluster: true })
  })

  const [showRedis, setShowRedis] = useState(form.current.redis_cluster)
  const [showMongo, setShowMongo] = useState(form.current.mongo_cluster)

  const handleSave = () => {
    updateField("atomdb", structuredClone(form.current))
    showToast({ message: "AtomDB settings applied", severity: "success" })
  }

  return (
    <>
      <GridSpan9>
        <TextField
          fullWidth
          label="Redis Endpoint"
          size="small"
          defaultValue={form.current.redis_endpoint}
          onChange={(e) => {
            form.current.redis_endpoint = e.target.value
          }}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="Redis Port"
          type="number"
          size="small"
          defaultValue={form.current.redis_port}
          onChange={(e) => {
            form.current.redis_port = Number(e.target.value)
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
          }}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="MongoDB Port"
          type="number"
          size="small"
          defaultValue={form.current.mongo_port}
          onChange={(e) => {
            form.current.mongo_port = Number(e.target.value)
          }}
        />
      </GridSpan3>

      <GridSpan6>
        <TextField
          fullWidth
          label="MongoDB Username"
          size="small"
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
          type="password"
          size="small"
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
        <FormControlLabel
          label="Redis Cluster"
          control={
            <Checkbox
              size="small"
              checked={showRedis}
              onChange={(e) => {
                setShowRedis(e.target.checked)
                form.current.redis_cluster = e.target.checked
              }}
            />
          }
        />
      </CheckboxContainer>

      <ClusterGridContainer>
        {showRedis && (
          <ClusterForm
            type="redis"
            onChange={(nodes) => {
              form.current.redis_nodes = nodes
            }}
          />
        )}

        {showMongo && (
          <ClusterForm
            type="mongo"
            onChange={(nodes) => {
              form.current.mongo_nodes = nodes
            }}
          />
        )}
      </ClusterGridContainer>

      <ActionButtonContainer>
        <SaveButton variant="contained" color="success" onClick={handleSave}>
          Apply AtomDB settings
        </SaveButton>
      </ActionButtonContainer>
    </>
  )
}
