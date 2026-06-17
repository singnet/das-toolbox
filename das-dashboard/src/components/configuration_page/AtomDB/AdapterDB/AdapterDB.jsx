import { Button, Checkbox, FormControlLabel, TextField, Typography, Divider, MenuItem } from "@mui/material"
import { useRef, useState } from "react"
import { useConfig } from "../../../global_providers/ConfigurationProvider";
import { useToast } from "../../../global_providers/ToastProvider";
import { RedisMongoSubForm } from "../RemoteDB/RedisMongoSubForm"
import { MorkMongoSubForm } from "../RemoteDB/MorkMongoSubForm"
import { 
  GridSpan9, 
  GridSpan3, 
  GridSpan6, 
  GridSpan4,
  GridSpan12,
  CheckboxContainer, 
  SectionTitle,
  ActionButtonContainer, 
  GridSpan5
} from "../AtomDBStyled"

export function AdapterDBOptions() {

  const { updateSection, getDefault } = useConfig()
  const { showToast } = useToast()

  const defaults = getDefault().adapterdb || {}

  const form = useRef({
    endpoint: defaults?.endpoint || "localhost:40023",
    type: defaults?.type || "postgres",
    database_credentials: {
      host: defaults?.database_credentials?.host || "remote.database.org",
      port: defaults?.database_credentials?.port || 5432,
      username: defaults?.database_credentials?.username || "admin",
      password: defaults?.database_credentials?.password || "admin",
      database: defaults?.database_credentials?.database || "database"
    },
    context_mapping_paths: defaults?.context_mapping_paths || ["/home/levi/Downloads/context.sql"],
    export_metta_on_mapping: {
      enabled: defaults?.export_metta_on_mapping?.enabled ?? true,
      output_dir: defaults?.export_metta_on_mapping?.output_dir || "/home/levi/Downloads"
    },
    persistence: {
      reuse_mongodb: defaults?.persistence?.reuse_mongodb ?? true
    },
    atomdb_backend: defaults?.atomdb_backend || {
      type: "redismongodb"
    }
  })

  const [backendType, setBackendType] = useState(form.current.atomdb_backend.type || "redismongodb")

  const handleBackendChange = (subFormData) => {
    form.current.atomdb_backend = {
      ...form.current.atomdb_backend,
      type: subFormData.type,
      ...(subFormData.redis && { redis: subFormData.redis }),
      ...(subFormData.mongodb && { mongodb: subFormData.mongodb }),
      ...(subFormData.morkdb && { morkdb: subFormData.morkdb })
    }
  }

  return (
    <>
      <SectionTitle>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Adapter Connection</Typography>
      </SectionTitle>

      <GridSpan4>
        <TextField
            select
            fullWidth
            label="Adapter Type"
            size="small"
            value={form.current.type}
            onChange={() => {}}
        >
            <MenuItem value="postgres">PostgreSQL</MenuItem>
        </TextField>
      </GridSpan4>

      <GridSpan5>
        <TextField
          fullWidth
          label="Adapter Endpoint"
          size="small"
          defaultValue={form.current.endpoint.split(":")[0]}
          onChange={() => {}}
        />
      </GridSpan5>

      <GridSpan3>
        <TextField
          fullWidth
          label="Adapter Port"
          type="number"
          size="small"
          defaultValue={form.current.endpoint.split(":")[1]}
          onChange={() => {}}
        />
      </GridSpan3>

      <SectionTitle>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Database Credentials</Typography>
      </SectionTitle>

      <GridSpan9>
        <TextField
          fullWidth
          label="Database Host"
          size="small"
          defaultValue={form.current.database_credentials.host}
          onChange={() => {}}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="Database Port"
          type="number"
          size="small"
          defaultValue={form.current.database_credentials.port}
          onChange={() => {}}
        />
      </GridSpan3>

      <GridSpan4>
        <TextField
          fullWidth
          label="Database Name"
          size="small"
          defaultValue={form.current.database_credentials.database}
          onChange={() => {}}
        />
      </GridSpan4>

      <GridSpan4>
        <TextField
          fullWidth
          label="Username"
          size="small"
          defaultValue={form.current.database_credentials.username}
          onChange={() => {}}
        />
      </GridSpan4>

      <GridSpan4>
        <TextField
          fullWidth
          label="Password"
          type="password"
          size="small"
          defaultValue={form.current.database_credentials.password}
          onChange={() => {}}
        />
      </GridSpan4>

      <SectionTitle>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Context & Mapping</Typography>
      </SectionTitle>

      <GridSpan12>
        <TextField
          fullWidth
          label="Context Mapping Path"
          size="small"
          defaultValue={form.current.context_mapping_paths[0]}
          onChange={() => {}}
        />
      </GridSpan12>

      <GridSpan12>
        <TextField
          fullWidth
          label="MeTTa Output Directory"
          size="small"
          defaultValue={form.current.export_metta_on_mapping.output_dir}
          onChange={() => {}}
        />
      </GridSpan12>

      <CheckboxContainer>
        <FormControlLabel
          label="Export MeTTa on Mapping"
          control={
            <Checkbox
              size="small"
              defaultChecked={form.current.export_metta_on_mapping.enabled}
              onChange={() => {}}
            />
          }
        />
        <FormControlLabel
          label="Reuse MongoDB Persistence"
          control={
            <Checkbox
              size="small"
              defaultChecked={form.current.persistence.reuse_mongodb}
              onChange={() => {}}
            />
          }
        />
      </CheckboxContainer>

      <GridSpan12>
        <Divider sx={{ my: 1 }} />
      </GridSpan12>

      <SectionTitle>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>AtomDB Backend Type</Typography>
      </SectionTitle>

      <GridSpan12>
        <TextField
          select
          fullWidth
          size="small"
          value={backendType}
          onChange={e => {
            const val = e.target.value
            setBackendType(val)
            form.current.atomdb_backend.type = val
          }}
        >
          <MenuItem value="inmemorydb">In Memory</MenuItem>
          <MenuItem value="redismongodb">Redis + MongoDB</MenuItem>
          <MenuItem value="morkdb">MorkDB + MongoDB</MenuItem>
        </TextField>
      </GridSpan12>

      {backendType === "redismongodb" && (
        <RedisMongoSubForm
          category="backend"
          onChange={(data) => handleBackendChange(data)}
        />
      )}

      {backendType === "morkdb" && (
        <MorkMongoSubForm
          category="backend"
          onChange={(data) => handleBackendChange(data)}
        />
      )}

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