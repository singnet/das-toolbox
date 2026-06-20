import { Checkbox, FormControlLabel, TextField, Typography, Divider, MenuItem } from "@mui/material"
import { useRef, useState } from "react"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { useToast } from "../../../global_providers/ToastProvider"
import { initAdapterBackend, splitEndpoint } from "../../configFormUtils"
import { AdapterBackendOptions } from "./AdapterBackendOptions"
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
import { SaveButton } from "../../Agents/Agents.styled"

export function AdapterDBOptions() {
  const { updateField, getDefault } = useConfig()
  const { showToast } = useToast()

  const adapter = splitEndpoint(getDefault("atomdb.adapterdb.endpoint"), "localhost", 40023)
  const defaultBackendType = getDefault("atomdb.adapterdb.atomdb_backend.type") || "morkdb"

  const form = useRef({
    atomdb_type: "adapterdb",
    adapter_type: getDefault("atomdb.adapterdb.type") || "postgres",
    adapter_endpoint: adapter.host,
    adapter_port: adapter.port,
    db_host: getDefault("atomdb.adapterdb.database_credentials.host") || "",
    db_port: getDefault("atomdb.adapterdb.database_credentials.port") || 5432,
    db_name: getDefault("atomdb.adapterdb.database_credentials.database") || "",
    db_username: getDefault("atomdb.adapterdb.database_credentials.username") || "",
    db_password: getDefault("atomdb.adapterdb.database_credentials.password") || "",
    context_mapping_path: getDefault("atomdb.adapterdb.context_mapping_paths")?.[0] || "",
    export_metta_enabled: getDefault("atomdb.adapterdb.export_metta_on_mapping.enabled") ?? true,
    export_metta_output_dir:
      getDefault("atomdb.adapterdb.export_metta_on_mapping.output_dir") || "./mapped_metta/",
    persistence_reuse_mongodb: getDefault("atomdb.adapterdb.persistence.reuse_mongodb") ?? true
  })

  const [adapterType, setAdapterType] = useState(form.current.adapter_type)
  const [backendType, setBackendType] = useState(defaultBackendType)
  const backendRef = useRef(initAdapterBackend(getDefault, defaultBackendType))

  const handleBackendTypeChange = (nextType) => {
    setBackendType(nextType)
    backendRef.current = initAdapterBackend(getDefault, nextType)
  }

  const handleSave = () => {
    updateField("atomdb", {
      ...structuredClone(form.current),
      atomdb_backend: structuredClone(backendRef.current)
    })
    showToast({ message: "AtomDB settings applied", severity: "success" })
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
          value={adapterType}
          onChange={(e) => {
            setAdapterType(e.target.value)
            form.current.adapter_type = e.target.value
          }}
        >
          <MenuItem value="postgres">PostgreSQL</MenuItem>
        </TextField>
      </GridSpan4>

      <GridSpan5>
        <TextField
          fullWidth
          label="Adapter Endpoint"
          size="small"
          defaultValue={form.current.adapter_endpoint}
          onChange={(e) => {
            form.current.adapter_endpoint = e.target.value
          }}
        />
      </GridSpan5>

      <GridSpan3>
        <TextField
          fullWidth
          label="Adapter Port"
          type="number"
          size="small"
          defaultValue={form.current.adapter_port}
          onChange={(e) => {
            form.current.adapter_port = Number(e.target.value)
          }}
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
          defaultValue={form.current.db_host}
          onChange={(e) => {
            form.current.db_host = e.target.value
          }}
        />
      </GridSpan9>

      <GridSpan3>
        <TextField
          fullWidth
          label="Database Port"
          type="number"
          size="small"
          defaultValue={form.current.db_port}
          onChange={(e) => {
            form.current.db_port = Number(e.target.value)
          }}
        />
      </GridSpan3>

      <GridSpan4>
        <TextField
          fullWidth
          label="Database Name"
          size="small"
          defaultValue={form.current.db_name}
          onChange={(e) => {
            form.current.db_name = e.target.value
          }}
        />
      </GridSpan4>

      <GridSpan4>
        <TextField
          fullWidth
          label="Username"
          size="small"
          defaultValue={form.current.db_username}
          onChange={(e) => {
            form.current.db_username = e.target.value
          }}
        />
      </GridSpan4>

      <GridSpan4>
        <TextField
          fullWidth
          label="Password"
          type="password"
          size="small"
          defaultValue={form.current.db_password}
          onChange={(e) => {
            form.current.db_password = e.target.value
          }}
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
          defaultValue={form.current.context_mapping_path}
          onChange={(e) => {
            form.current.context_mapping_path = e.target.value
          }}
        />
      </GridSpan12>

      <GridSpan12>
        <TextField
          fullWidth
          label="MeTTa Output Directory"
          size="small"
          defaultValue={form.current.export_metta_output_dir}
          onChange={(e) => {
            form.current.export_metta_output_dir = e.target.value
          }}
        />
      </GridSpan12>

      <CheckboxContainer>
        <FormControlLabel
          label="Export MeTTa on Mapping"
          control={
            <Checkbox
              size="small"
              defaultChecked={form.current.export_metta_enabled}
              onChange={(e) => {
                form.current.export_metta_enabled = e.target.checked
              }}
            />
          }
        />
        <FormControlLabel
          label="Reuse MongoDB Persistence"
          control={
            <Checkbox
              size="small"
              defaultChecked={form.current.persistence_reuse_mongodb}
              onChange={(e) => {
                form.current.persistence_reuse_mongodb = e.target.checked
              }}
            />
          }
        />
      </CheckboxContainer>

      <GridSpan12>
        <Divider sx={{ my: 1 }} />
      </GridSpan12>

      <SectionTitle>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>AtomDB Backend</Typography>
      </SectionTitle>

      <GridSpan12>
        <TextField
          select
          fullWidth
          size="small"
          label="Backend Type"
          value={backendType}
          onChange={(e) => handleBackendTypeChange(e.target.value)}
        >
          <MenuItem value="inmemorydb">In Memory</MenuItem>
          <MenuItem value="redismongodb">Redis + MongoDB</MenuItem>
          <MenuItem value="morkdb">MorkDB + MongoDB</MenuItem>
        </TextField>
      </GridSpan12>

      <AdapterBackendOptions
        key={backendType}
        backendType={backendType}
        backendRef={backendRef}
      />

      <ActionButtonContainer>
        <SaveButton variant="contained" color="success" onClick={handleSave}>
          Apply AtomDB settings
        </SaveButton>
      </ActionButtonContainer>
    </>
  )
}
