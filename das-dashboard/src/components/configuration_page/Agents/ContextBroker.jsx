    import { useRef } from "react"
    import { TextField } from "@mui/material"
    import { useConfig } from "../../global_providers/ConfigurationProvider"
    import { useToast } from "../../global_providers/ToastProvider"
    import { getAgentByKey, AGENT_COMPONENTS } from "./agentRegistry"
    import {
    AgentContent,
    AgentContentHeader,
    AgentTitle,
    ConfigSection,
    ConfigSectionTitle,
    FieldGrid,
    SaveButton
    } from "./Agents.styled"

export default function ContextBrokerPanel() {
    const { updateField, getDefault } = useConfig()
    const { showToast } = useToast()
    const agent = getAgentByKey("context")

    const form = useRef((() => {
        const prefix = "agents.context.params."
        const fullEndpoint = getDefault("agents.context.endpoint") || "0.0.0.0:40000"
        const fullRange = getDefault("agents.context.ports_range") || "42000:42999"

        return {
        endpoint_ip: fullEndpoint.split(":")[0] || "0.0.0.0",
        endpoint_port: Number(fullEndpoint.split(":")[1]) || 40000,
        ports_range_start: Number(fullRange.split(":")[0]) || 42000,
        ports_range_end: Number(fullRange.split(":")[1]) || 42999,
        context: getDefault(`${prefix}context`) || "context",
        initial_rent_rate: getDefault(`${prefix}initial_rent_rate`) ?? 0.75,
        initial_spreading_rate_lowerbound: getDefault(`${prefix}initial_spreading_rate_lowerbound`) ?? 0.1,
        initial_spreading_rate_upperbound: getDefault(`${prefix}initial_spreading_rate_upperbound`) ?? 0.1,
        use_cache: getDefault(`${prefix}use_cache`) ?? true,
        enforce_cache_recreation: getDefault(`${prefix}enforce_cache_recreation`) ?? false
        }
    })())

    const handleSave = () => {
        updateField("agents.context", {
            endpoint: `${form.current.endpoint_ip}:${form.current.endpoint_port}`,
            ports_range: `${form.current.ports_range_start}:${form.current.ports_range_end}`,
            ...Object.fromEntries(
            Object.entries(form.current).filter(
                ([key]) =>
                ![
                    "endpoint_ip",
                    "endpoint_port",
                    "ports_range_start",
                    "ports_range_end"
                ].includes(key)
            )
            )
        })

        showToast({
            message: `${agent.label} settings applied`,
            severity: "success"
        })
    }

    const SpecificParamComponent = AGENT_COMPONENTS[agent.paramsKey]

    return (
        <AgentContent>
        <AgentContentHeader>
            <AgentTitle>{agent.label}</AgentTitle>
        </AgentContentHeader>

        <ConfigSection>
            <ConfigSectionTitle>Connection</ConfigSectionTitle>
            <FieldGrid>
            <TextField
                label="IP Address"
                fullWidth
                size="small"
                defaultValue={form.current.endpoint_ip}
                onChange={(e) => { form.current.endpoint_ip = e.target.value }}
            />
            <TextField
                label="Port"
                fullWidth
                type="number"
                size="small"
                defaultValue={form.current.endpoint_port}
                onChange={(e) => { form.current.endpoint_port = Number(e.target.value) }}
            />
            </FieldGrid>

            <FieldGrid sx={{ mt: 2 }}>
            <TextField
                label="Port range start"
                fullWidth
                type="number"
                size="small"
                defaultValue={form.current.ports_range_start}
                onChange={(e) => { form.current.ports_range_start = Number(e.target.value) }}
            />
            <TextField
                label="Port range end"
                fullWidth
                type="number"
                size="small"
                defaultValue={form.current.ports_range_end}
                onChange={(e) => { form.current.ports_range_end = Number(e.target.value) }}
            />
            </FieldGrid>
        </ConfigSection>

        {SpecificParamComponent && (
            <ConfigSection>
            <ConfigSectionTitle>Parameters</ConfigSectionTitle>
            <SpecificParamComponent formRef={form} />
            </ConfigSection>
        )}

        <SaveButton variant="contained" color="success" onClick={handleSave}>
            Apply {agent.label} settings
        </SaveButton>
        </AgentContent>
    )
    }