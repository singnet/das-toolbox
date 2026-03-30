import { TextField, Box } from "@mui/material"
import { useRef, useEffect } from "react"

export function MorkMongoSubForm({ onChange, category }) {
  const data = useRef({
    morkPort: "40022",
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
        type: "morkmongodb",
        mongodb: {
          endpoint: `localhost:${data.current.mongoPort}`,
          username: data.current.user,
          password: data.current.pass,
          cluster: false,
          cluster_secret_key: "None",
          nodes: node
        },
        morkdb: {
          endpoint: `localhost:${data.current.morkPort}`
        }
      },
      category
    )
  }

  return (
    <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1.5, mt: 1 }}>
      <TextField label="MorkDB Port" size="small" defaultValue="40022" onChange={e => update("morkPort", e.target.value)} />
      <TextField label="Mongo Port" size="small" defaultValue="40021" onChange={e => update("mongoPort", e.target.value)} />
      <TextField label="Mongo User" size="small" defaultValue="admin" onChange={e => update("user", e.target.value)} />
      <TextField label="Mongo Pass" size="small" type="password" defaultValue="admin" onChange={e => update("pass", e.target.value)} />
    </Box>
  )
}