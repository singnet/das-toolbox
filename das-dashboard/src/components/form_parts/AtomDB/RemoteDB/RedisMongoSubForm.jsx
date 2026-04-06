import { TextField, Box } from "@mui/material"
import { useEffect, useRef } from "react"
import { useConfig } from "../../../global_components/ConfigurationProvider"

export function RedisMongoSubForm({ onChange, category }) {

  const { getDefault } = useConfig()
  const defaults = getDefault().atomdb || {}

  const section = useRef({
    type: "redismongodb",
    redis: {
      endpoint: defaults?.redis?.endpoint || "localhost:40020",
      cluster: defaults?.redis?.cluster || false,
      nodes: defaults?.redis?.nodes || [{ context: "default", ip: "localhost", username: "root" }]
    },
    mongodb: {
      endpoint: defaults?.mongodb?.endpoint || "localhost:40021",
      username: defaults?.mongodb?.username || "admin",
      password: defaults?.mongodb?.password || "admin",
      cluster: defaults?.mongodb?.cluster || false,
      cluster_secret_key: defaults?.mongodb?.cluster_secret_key || "None",
      nodes: defaults?.mongodb?.nodes || [{ context: "default", ip: "localhost", username: "root" }]
    }
  })

  useEffect(() => {
    onChange(structuredClone(section.current), category)
  }, [])

  return (
    <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1.5, mt: 1 }}>

      <TextField
        label="Redis Port"
        size="small"
        defaultValue={section.current.redis.endpoint.split(":")[1]}
        onChange={e => {
          section.current.redis.endpoint = `localhost:${e.target.value}`
          onChange(structuredClone(section.current), category)
        }}
      />

      <TextField
        label="Mongo Port"
        size="small"
        defaultValue={section.current.mongodb.endpoint.split(":")[1]}
        onChange={e => {
          section.current.mongodb.endpoint = `localhost:${e.target.value}`
          onChange(structuredClone(section.current), category)
        }}
      />

      <TextField
        label="Mongo User"
        size="small"
        defaultValue={section.current.mongodb.username}
        onChange={e => {
          section.current.mongodb.username = e.target.value
          onChange(structuredClone(section.current), category)
        }}
      />

      <TextField
        label="Mongo Pass"
        size="small"
        type="password"
        defaultValue={section.current.mongodb.password}
        onChange={e => {
          section.current.mongodb.password = e.target.value
          onChange(structuredClone(section.current), category)
        }}
      />

    </Box>
  )
}