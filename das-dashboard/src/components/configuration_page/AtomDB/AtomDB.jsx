import { Box, TextField, MenuItem, Menu } from "@mui/material"
import { RedisMongoOptions } from "./RedisMongo/RedisMongo"
import { MorkMongoOptions } from "./MorkMongo/MorkMongo"
import { useState } from "react"
import { InMemoryOptions } from "./InMemory/InMemory"
import { RemoteDBOptions } from "./RemoteDB/RemoteDB"
import { useConfig } from "../../global_providers/ConfigurationProvider"
import { AtomDBConnectionForm, AtomDBFormBox } from "./AtomDBStyled"
import { AdapterDBOptions } from "./AdapterDB/AdapterDB"

export default function AtomDBForm({ onSectionSave }) {

  const { getDefault } = useConfig()
  const atomDB = getDefault["atomdb.type"] || "redismongodb"
  const [type, setType] = useState(atomDB.type)

  return (
    <AtomDBFormBox>
    
      <TextField
        select
        fullWidth
        label="Database Type"
        value={type}
        onChange={(e) => setType(e.target.value)}
      >
        <MenuItem value="redismongodb">Redis + MongoDB</MenuItem>
        <MenuItem value="morkdb">Mork + MongoDB</MenuItem>
        <MenuItem value="inmemorydb">In Memory</MenuItem>
        <MenuItem value="remotedb">Remote DB (Multi-Peer)</MenuItem>
        <MenuItem value="adapterdb">AdapterDB</MenuItem>
      </TextField>


        {type === "redismongodb" && (
          <AtomDBConnectionForm>
            <RedisMongoOptions/>
          </AtomDBConnectionForm>
        )}

        {type === "morkdb" && (
          <AtomDBConnectionForm>
            <MorkMongoOptions/>
          </AtomDBConnectionForm>
        )}

        {type === "inmemorydb" && (
          <AtomDBConnectionForm>
            <InMemoryOptions/>
          </AtomDBConnectionForm>
        )}

        {type === "remotedb" && (
          <AtomDBConnectionForm>
            <RemoteDBOptions/>
          </AtomDBConnectionForm>
        )}

        {type === "adapterdb" && (
          <AtomDBConnectionForm>
            <AdapterDBOptions/>
          </AtomDBConnectionForm>
        )}


    </AtomDBFormBox>
  )
}