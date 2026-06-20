import {
  Button,
  TextField,
  Typography,
  MenuItem,
  Divider,
  IconButton
} from "@mui/material"
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline"
import { useState, useRef } from "react"
import { RedisMongoSubForm } from "./RedisMongoSubForm"
import { MorkMongoSubForm } from "./MorkMongoSubForm"
import { useConfig } from "../../../global_providers/ConfigurationProvider"
import { useToast } from "../../../global_providers/ToastProvider"
import {
  GridSpan12,
  PeerCard,
  PeerHeaderContainer,
  ActionButtonContainer
} from "../AtomDBStyled"
import { SaveButton } from "../../Agents/Agents.styled"

export function RemoteDBOptions() {

  const { updateField } = useConfig()
  const { showToast } = useToast()

  const [peers, setPeers] = useState([])
  const peersRefs = useRef({})

  const addPeer = () => {
    const id = Date.now()
    const uid = `peer${peers.length + 1}`

    peersRefs.current[id] = {
      uid,
      type: "redismongodb",
      context: `remotedb_${uid}_`,
      local_persistence: { type: "inmemorydb" }
    }

    setPeers(prev => [
      ...prev,
      { id, uid, type: "redismongodb", localType: "inmemorydb" }
    ])
  }

  const removePeer = (id) => {
    delete peersRefs.current[id]
    setPeers(prev => prev.filter(p => p.id !== id))
  }

  const updatePeer = (id, subFormData, category) => {
    const base = peersRefs.current[id]
    if (!base) return

    const { type, ...connection } = subFormData

    if (category === "main") {
      peersRefs.current[id] = {
        uid: base.uid,
        context: base.context,
        type,
        local_persistence: base.local_persistence || { type: "inmemorydb" },
        ...connection
      }
      return
    }

    if (category === "local") {
      peersRefs.current[id].local_persistence = {
        type,
        context: `${base.context}local_`,
        ...connection
      }
    }
  }

  const handleSave = () => {
    const cleanedPeers = Object.values(peersRefs.current)
      .filter(peer => {
        if (!peer.type) return false
        if (peer.type === "redismongodb" && (!peer.redis_port || !peer.mongo_port)) return false
        if (peer.type === "morkdb" && (!peer.mork_port || !peer.mongo_port)) return false
        return true
      })
      .map(peer => structuredClone(peer))

    updateField("atomdb", {
      atomdb_type: "remotedb",
      remote_peers: cleanedPeers
    })

    showToast({ message: "AtomDB settings applied", severity: "success" })
  }

  return (
    <>
      <GridSpan12>
        <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
          Remote Peers List
        </Typography>
      </GridSpan12>

      {peers.map(peer => (
        <PeerCard key={peer.id} variant="outlined">
          <PeerHeaderContainer>
            <TextField
              label="Peer UID"
              size="small"
              value={peer.uid}
              disabled
              sx={{ width: "200px" }}
            />

            <TextField
              select
              label="Main Connection"
              size="small"
              value={peer.type}
              sx={{ width: "250px" }}
              onChange={e => {
                const val = e.target.value
                peersRefs.current[peer.id].type = val
                setPeers(prev =>
                  prev.map(p => p.id === peer.id ? { ...p, type: val } : p)
                )
              }}
            >
              <MenuItem value="redismongodb">Redis + Mongo</MenuItem>
              <MenuItem value="morkdb">Mork + Mongo</MenuItem>
            </TextField>

            <IconButton
              size="small"
              color="error"
              aria-label="Remove peer"
              onClick={() => removePeer(peer.id)}
            >
              <DeleteOutlineIcon fontSize="small" />
            </IconButton>
          </PeerHeaderContainer>

          {peer.type === "redismongodb" ? (
            <RedisMongoSubForm
              category="main"
              onChange={(data, cat) => updatePeer(peer.id, data, cat)}
            />
          ) : (
            <MorkMongoSubForm
              category="main"
              onChange={(data, cat) => updatePeer(peer.id, data, cat)}
            />
          )}

          <GridSpan12>
            <Divider sx={{ my: 1 }} />
          </GridSpan12>

          <GridSpan12>
            <Typography variant="caption" sx={{ fontWeight: 600, display: "block", mb: 1 }}>
              Local Persistence Type
            </Typography>
          </GridSpan12>

          <GridSpan12>
            <TextField
              select
              fullWidth
              size="small"
              value={peer.localType}
              onChange={e => {
                const val = e.target.value
                setPeers(prev =>
                  prev.map(p => p.id === peer.id ? { ...p, localType: val } : p)
                )
                if (val === "inmemorydb") {
                  peersRefs.current[peer.id].local_persistence = { type: "inmemorydb" }
                } else {
                  peersRefs.current[peer.id].local_persistence = {}
                }
              }}
            >
              <MenuItem value="inmemorydb">In Memory</MenuItem>
              <MenuItem value="redismongodb">Redis + MongoDB</MenuItem>
              <MenuItem value="morkdb">MorkDB + MongoDB</MenuItem>
            </TextField>
          </GridSpan12>

          {peer.localType === "redismongodb" && (
            <RedisMongoSubForm
              category="local"
              onChange={(data, cat) => updatePeer(peer.id, data, cat)}
            />
          )}

          {peer.localType === "morkdb" && (
            <MorkMongoSubForm
              category="local"
              onChange={(data, cat) => updatePeer(peer.id, data, cat)}
            />
          )}
        </PeerCard>
      ))}

      <GridSpan12>
        <Button variant="outlined" onClick={addPeer} fullWidth>
          + Add Peer
        </Button>
      </GridSpan12>

      <ActionButtonContainer>
        <SaveButton
          variant="contained"
          color="success"
          onClick={handleSave}
        >
          Apply AtomDB settings
        </SaveButton>
      </ActionButtonContainer>
    </>
  )
}