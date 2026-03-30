import { TextField, Box } from "@mui/material"
import { useRef, useEffect } from "react"

export function RedisMongoSubForm({ onChange, category }) {
  const data = useRef({
    redisPort: "40020",
    mongoPort: "40021",
    user: "admin",
    pass: "admin"
  })

  useEffect(() => {
    update()
  }, [])

  const update = (field, value) => {
    if (field) data.current[field] = value

    const node = [
      { context: "default", ip: "localhost", username: "root" }
    ]

    onChange(
      {
        type: "redismongodb",
        redis: {
          endpoint: `localhost:${data.current.redisPort}`,
          cluster: false,
          nodes: node
        },
        mongodb: {
          endpoint: `localhost:${data.current.mongoPort}`,
          username: data.current.user,
          password: data.current.pass,
          cluster: false,
          cluster_secret_key: "None",
          nodes: node
        }
      },
      category
    )
  }

  return (
    <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1.5, mt: 1 }}>
      <TextField label="Redis Port" size="small" defaultValue="40020" onChange={e => update("redisPort", e.target.value)} />
      <TextField label="Mongo Port" size="small" defaultValue="40021" onChange={e => update("mongoPort", e.target.value)} />
      <TextField label="Mongo User" size="small" defaultValue="admin" onChange={e => update("user", e.target.value)} />
      <TextField label="Mongo Pass" size="small" type="password" defaultValue="admin" onChange={e => update("pass", e.target.value)} />
    </Box>
  )
}