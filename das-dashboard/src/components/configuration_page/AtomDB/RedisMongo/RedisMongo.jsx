import { TextField, FormControlLabel, Checkbox } from "@mui/material"
import { useState, useRef } from "react"
import { ClusterForm } from "../ClusterForm"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { useToast } from "../../../global_providers/ToastProvider"
import { initRedisMongoConnection, parsePortValue } from "../../configFormUtils"
import { ConfigForm } from "../../ConfigForm"
import { portField } from "../../formValidation"
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
  const { updateField, getAtomdbTemplate } = useConfig()
  const { showToast } = useToast()

  const form = useRef({
    atomdb_type: "redismongodb",
    ...initRedisMongoConnection(getAtomdbTemplate("redismongodb"), { withCluster: true })
  })

  const [showRedis, setShowRedis] = useState(form.current.redis_cluster)
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
          label="Redis Endpoint"
          size="small"
          required
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
          required
          defaultValue={form.current.redis_port}
          onChange={(e) => {
            form.current.redis_port = parsePortValue(e.target.value)
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
          required
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
            key="redis-cluster"
            type="redis"
            initialNodes={form.current.redis_nodes}
            onChange={(nodes) => {
              form.current.redis_nodes = nodes
            }}
          />
        )}

        {showMongo && (
          <ClusterForm
            key="mongo-cluster"
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
