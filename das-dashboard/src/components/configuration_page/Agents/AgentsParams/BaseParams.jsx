import {
  AgentsLayout,
  AgentNav,
  AgentNavGroupLabel,
  AgentNavItem,
  AgentContent,
  AgentContentHeader,
  AgentTitle,
  AgentDescription,
  ConfigSection,
  ConfigSectionTitle,
  FieldGrid,
  SwitchGrid,
  SaveButton
} from "../Agents.styled"

import { useRef, useState } from "react"
import {
  TextField,
  Switch,
  FormControlLabel
} from "@mui/material"

import { useConfig } from "../../../global_providers/ConfigurationProvider"