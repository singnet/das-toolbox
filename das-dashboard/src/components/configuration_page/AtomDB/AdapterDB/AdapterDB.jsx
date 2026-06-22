import {
  Box,
  Checkbox,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  TextField,
  Typography,
  Divider,
  MenuItem,
  Button
} from "@mui/material"
import { useRef, useState } from "react"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { useToast } from "../../../global_providers/ToastProvider"
import { saveContextMapping } from "../../../../api/ConfigAPI"
import { initAdapterBackend } from "../../configFormUtils"
import { AdapterBackendOptions } from "./AdapterBackendOptions"
import {
  GridSpan9,
  GridSpan3,
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
    export_metta_enabled: template.export_metta_enabled ?? true,
    export_metta_output_dir: template.export_metta_output_dir || "",
    persistence_reuse_mongodb: template.persistence_reuse_mongodb ?? true
  })

  const [adapterType, setAdapterType] = useState(form.current.adapter_type)
  const [backendType, setBackendType] = useState(defaultBackendType)
  const [contextMappingMode, setContextMappingMode] = useState("content")
  const [contextMappingContent, setContextMappingContent] = useState("")
  const [contextMappingPath, setContextMappingPath] = useState("")
  const fileInputRef = useRef(null)
  const backendRef = useRef(initAdapterBackend(template, defaultBackendType))

  const handleBackendTypeChange = (nextType) => {
    setBackendType(nextType)
    backendRef.current = initAdapterBackend(getAtomdbTemplate("adapterdb") || {}, nextType)
  }

  const handleLoadContextFile = async (event) => {
    const file = event.target.files?.[0]
    if (!file) {
      return
    }

    try {
      const text = await file.text()
      setContextMappingContent(text)
      setContextMappingMode("content")
      showToast({ message: "File loaded into editor. Click Save to upload.", severity: "info" })
    } catch (error) {
      console.error(error)
      showToast({ message: "Failed to read file", severity: "error" })
    } finally {
      event.target.value = ""
    }
  }

  const handleSaveContextMapping = async () => {
    try {
      if (contextMappingMode === "path") {
        await saveContextMapping({ path: contextMappingPath })
      } else {
        await saveContextMapping({ content: contextMappingContent })
      }

      showToast({ message: "Context mapping saved", severity: "success" })
    } catch (error) {
      console.error(error)
      showToast({ message: "Failed to save context mapping", severity: "error" })
    }
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

      <GridSpan12>
        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 1 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Context Mapping
          </Typography>
          <Button variant="contained" size="small" onClick={handleSaveContextMapping}>
            Save
          </Button>
        </Box>

        <FormControl sx={{ mb: 1 }}>
          <RadioGroup
            row
            value={contextMappingMode}
            onChange={(e) => setContextMappingMode(e.target.value)}
          >
            <FormControlLabel value="content" control={<Radio size="small" />} label="Paste content" />
            <FormControlLabel value="path" control={<Radio size="small" />} label="Use file path" />
          </RadioGroup>
          <Typography variant="subtitle2" sx={{ fontWeight: 100 }}>
            File path mode is recommended if you are going to use the configuration outside of the web environment, otherwise use 'content' mode and the server will handle pats automatically.
          </Typography>
        </FormControl>

        {contextMappingMode === "content" ? (
          <>
            <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 1 }}>
              <Button variant="outlined" size="small" onClick={() => fileInputRef.current?.click()}>
                Load from file
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".sql"
                hidden
                onChange={handleLoadContextFile}
              />
            </Box>
            <TextField
              fullWidth
              multiline
              minRows={8}
              placeholder="Paste or type the context mapping content here"
              size="small"
              value={contextMappingContent}
              onChange={(e) => setContextMappingContent(e.target.value)}
            />
          </>
        ) : (
          <TextField
            fullWidth
            label="Context Mapping File Path"
            size="small"
            placeholder=""
            value={contextMappingPath}
            onChange={(e) => setContextMappingPath(e.target.value)}
          />
        )}
      </GridSpan12>

      <GridSpan12>
        <TextField
          fullWidth
          label="MeTTa Output Path"
          size="small"
          placeholder="/opt/web-das/.das/mapped_metta"
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
