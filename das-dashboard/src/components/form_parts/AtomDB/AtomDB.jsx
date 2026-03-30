import { Box, Typography, TextField, MenuItem } from "@mui/material"
import { RedisMongoOptions } from "./RedisMongo"
import { MorkMongoOptions } from "./MorkMongo"
import { useState } from "react"
import { InMemoryOptions } from "./InMemory"
import { RemoteDBOptions } from "./RemoteDB/RemoteDB"

export default function AtomDBForm({ onSectionSave }) {
  const [type, setType] = useState("")

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      
      <Typography variant="h6">
        AtomDB Configuration
      </Typography>

      <TextField
        select
        fullWidth
        label="Database Type"
        value={type}
        onChange={(e) => setType(e.target.value)}
      >
        <MenuItem value="redismongodb">Redis + MongoDB</MenuItem>
        <MenuItem value="morkmongodb">Mork + MongoDB</MenuItem>
        <MenuItem value="inmemorydb">In Memory</MenuItem>
        <MenuItem value="remotedb">Remote DB (Multi-Peer)</MenuItem>
      </TextField>

      {type === "redismongodb" && (
        <RedisMongoOptions
          onSave={(data) =>
            onSectionSave("atomdb", { type, ...data })
          }
        />
      )}

      {type === "morkmongodb" && (
        <MorkMongoOptions
          onSave={(data) =>
            onSectionSave("atomdb", { type, ...data })
          }
        />
      )}

      {type === "inmemorydb" && (
        <InMemoryOptions
          onSave={(data) =>
            onSectionSave("atomdb", { type, ...data })
          }
        />
      )}

      {type === "remotedb" && (
        <RemoteDBOptions
          onSave={(data) =>
            onSectionSave("atomdb", { type, ...data })
          }
        />
      )}

    </Box>
  )
}