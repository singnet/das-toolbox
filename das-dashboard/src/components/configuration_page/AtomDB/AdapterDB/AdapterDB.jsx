import { Checkbox, FormControlLabel, TextField, Typography, Divider, MenuItem, Button } from "@mui/material"
import { useEffect, useRef, useState } from "react"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { useToast } from "../../../global_providers/ToastProvider"
import { getWorkspacePaths, uploadContextMappingFile } from "../../../../api/ConfigAPI"
import { initAdapterBackend } from "../../configFormUtils"
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
  const { updateField, getAtomdbTemplate } = useConfig()
  const { showToast } = useToast()

  const template = getAtomdbTemplate("adapterdb") || {}
  const defaultBackendType = template.atomdb_backend?.type || "morkdb"

  const form = useRef({
    atomdb_type: "adapterdb",
    adapter_type: template.adapter_type || "postgres",
    adapter_endpoint: template.adapter_endpoint || "localhost",
    adapter_port: template.adapter_port ?? 40023,
    db_host: template.db_host || "",
    db_port: template.db_port ?? 5432,
    db_name: template.db_name || "",
    db_username: template.db_username || "",
    db_password: template.db_password || "",
    context_mapping_path: template.context_mapping_path || "",
    export_metta_enabled: template.export_metta_enabled ?? true,
    export_metta_output_dir: template.export_metta_output_dir || "",
    persistence_reuse_mongodb: template.persistence_reuse_mongodb ?? true
  })

  const [adapterType, setAdapterType] = useState(form.current.adapter_type)
  const [backendType, setBackendType] = useState(defaultBackendType)
  const [contextMappingPath, setContextMappingPath] = useState(form.current.context_mapping_path)
  const backendRef = useRef(initAdapterBackend(template, defaultBackendType))

  useEffect(() => {
    async function loadWorkspacePaths() {
      try {
        const response = await getWorkspacePaths()
        const paths = response.content || {}

        if (!form.current.export_metta_output_dir && paths.metta_output) {
          form.current.export_metta_output_dir = paths.metta_output
        }
      } catch (error) {
        console.error(error)
      }
    }

    loadWorkspacePaths()
  }, [])

  const handleBackendTypeChange = (nextType) => {
    setBackendType(nextType)
    backendRef.current = initAdapterBackend(getAtomdbTemplate("adapterdb") || {}, nextType)
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
        <Button variant="outlined" component="label" size="small">
          Upload Context Mapping File
          <input
            hidden
            type="file"
            accept=".sql,.json,.csv,.txt"
            onChange={async (event) => {
              const file = event.target.files?.[0]
              if (!file) return

              try {
                const response = await uploadContextMappingFile(file)
                form.current.context_mapping_path = response.saved_path
                setContextMappingPath(response.saved_path)
                showToast({ message: "Context mapping file uploaded", severity: "success" })
              } catch (error) {
                console.error(error)
                showToast({ message: "Failed to upload context mapping file", severity: "error" })
              } finally {
                event.target.value = ""
              }
            }}
          />
        </Button>
      </GridSpan12>

      <GridSpan12>
        <TextField
          fullWidth
          label="Context Mapping Path"
          size="small"
          value={contextMappingPath}
          InputProps={{ readOnly: true }}
          helperText="Stored under /opt/web-das/.das/workspace — same path on host and container."
        />
      </GridSpan12>

      <GridSpan12>
        <TextField
          fullWidth
          label="MeTTa Output Directory"
          size="small"
          defaultValue={form.current.export_metta_output_dir}
          helperText="Default: /opt/web-das/.das/workspace/mapped_metta (shared mount)."
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
