import { Checkbox, FormControlLabel, TextField } from "@mui/material"
import { useState } from "react"
import { ClusterForm } from "../ClusterForm"
import { parsePortValue } from "../../configFormUtils"
import { portField } from "../../formValidation"
import {
  GridSpan9,
  GridSpan3,
  GridSpan6,
  CheckboxContainer,
  ClusterGridContainer
} from "../AtomDBStyled"

export function AdapterBackendOptions({ backendType, backendRef }) {
  const form = backendRef

  const [showRedis, setShowRedis] = useState(form.current.redis_cluster ?? false)
  const [showMongo, setShowMongo] = useState(form.current.mongo_cluster ?? false)

  if (backendType === "inmemorydb") {
    return null
  }

  if (backendType === "redismongodb") {
    return (
      <>
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
              key="adapter-redis-cluster"
              type="redis"
              initialNodes={form.current.redis_nodes}
              onChange={(nodes) => {
                form.current.redis_nodes = nodes
              }}
            />
          )}

          {showMongo && (
            <ClusterForm
              key="adapter-mongo-cluster"
              type="mongo"
              initialNodes={form.current.mongo_nodes}
              onChange={(nodes) => {
                form.current.mongo_nodes = nodes
              }}
            />
          )}
        </ClusterGridContainer>
      </>
    )
  }

  if (backendType === "morkdb") {
    return (
      <>
        <GridSpan9>
          <TextField
            fullWidth
            label="MorkDB Endpoint"
            size="small"
            required
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
        </CheckboxContainer>

        <ClusterGridContainer>
          {showMongo && (
            <ClusterForm
              key="adapter-mork-mongo-cluster"
              type="mongo"
              initialNodes={form.current.mongo_nodes}
              onChange={(nodes) => {
                form.current.mongo_nodes = nodes
              }}
            />
          )}
        </ClusterGridContainer>
      </>
    )
  }

  return null
}
