import { TextField, FormControlLabel, Checkbox, Button } from "@mui/material"
import { useState, useRef } from "react"
import { ClusterForm } from "./ClusterForm"
import { useConfig } from "../../global_components/ConfigurationProvider"
import { useToast } from "../../global_components/ToastProvider"

export function RedisMongoOptions() {

  const { updateSection, getDefault } = useConfig()
  const { showToast } = useToast()

  const defaults = getDefault().atomdb || {}

  const section = useRef({
    type: "redismongodb",
    redis: {
      endpoint: defaults?.redis?.endpoint || "localhost:40020",
      cluster: defaults?.redis?.cluster || false,
      nodes: defaults?.redis?.nodes || []
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

  const [showRedis, setShowRedis] = useState(section.current.redis.cluster)
  const [showMongo, setShowMongo] = useState(section.current.mongodb.cluster)

  return (
    <>
      <TextField
        fullWidth
        label="Redis Port"
        type="number"
        margin="normal"
        defaultValue={section.current.redis.endpoint.split(":")[1]}
        onChange={(e) =>
          section.current.redis.endpoint = `localhost:${e.target.value}`
        }
      />

      <TextField
        fullWidth
        label="Mongo Port"
        type="number"
        margin="normal"
        defaultValue={section.current.mongodb.endpoint.split(":")[1]}
        onChange={(e) =>
          section.current.mongodb.endpoint = `localhost:${e.target.value}`
        }
      />

      <TextField
        fullWidth
        label="MongoDB Username"
        margin="normal"
        defaultValue={section.current.mongodb.username}
        onChange={(e) =>
          section.current.mongodb.username = e.target.value
        }
      />

      <TextField
        fullWidth
        label="MongoDB Password"
        type="password"
        margin="normal"
        defaultValue={section.current.mongodb.password}
        onChange={(e) =>
          section.current.mongodb.password = e.target.value
        }
      />

      <FormControlLabel
        label="Mongo Cluster - (Won't work on das-cli currently)"
        control={
          <Checkbox
            defaultChecked={section.current.mongodb.cluster}
            onChange={(e) => {
              section.current.mongodb.cluster = e.target.checked
              setShowMongo(e.target.checked)
            }}
          />
        }
      />

      <FormControlLabel
        label="Redis Cluster - (Won't work on das-cli currently)"
        control={
          <Checkbox
            defaultChecked={section.current.redis.cluster}
            onChange={(e) => {
              section.current.redis.cluster = e.target.checked
              setShowRedis(e.target.checked)
            }}
          />
        }
      />

      {showRedis && (
        <ClusterForm
          onChange={(nodes) => (section.current.redis.nodes = nodes)}
        />
      )}

      {showMongo && (
        <ClusterForm
          onChange={(nodes) => (section.current.mongodb.nodes = nodes)}
        />
      )}

      <Button
        variant="contained"
        color="success"
        onClick={() => {
          updateSection("atomdb", structuredClone(section.current))
          showToast("AtomDB saved successfully!")
        }}
        sx={{ mt: 2 }}
      >
        Save AtomDB Section
      </Button>
    </>
  )
}