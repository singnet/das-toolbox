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
import { ConfigForm } from "../../ConfigForm"

export function RemoteDBOptions() {

  const { config, updateField, getAtomdbTemplate } = useConfig()
  const { showToast } = useToast()

  const [savedPeers] = useState(() => structuredClone(
    (config.atomdb?.atomdb_type === "remotedb"
      ? config.atomdb.remote_peers
      : getAtomdbTemplate("remotedb")?.remote_peers) || []
  ))
  const [peers, setPeers] = useState(() => savedPeers.map((peer, index) => ({
    id: index + 1,
    uid: peer.uid,
    type: peer.type,
    localType: peer.local_persistence?.type || "inmemorydb",
    initialValues: peer
  })))
  const peersRefs = useRef(Object.fromEntries(savedPeers.map((peer, index) => [index + 1, peer])))
  const nextPeerIdRef = useRef(savedPeers.length + 1)

  const addPeer = () => {
    let id = nextPeerIdRef.current++
    while (Object.values(peersRefs.current).some(peer => peer.uid === `peer${id}`)) {
      id = nextPeerIdRef.current++
    }
    const uid = `peer${id}`

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
      const savedContext = base.local_persistence?.context
      peersRefs.current[id].local_persistence = {
        ...base.local_persistence,
        ...connection,
        type,
        context: savedContext || `${base.context || ""}local_`,
      }
    }
  }

  const isValidLocalPersistence = (localPersistence) => {
    if (!localPersistence?.type) {
      return false
    }

    if (localPersistence.type === "inmemorydb") {
      return true
    }

    if (localPersistence.type === "redismongodb") {
      return Boolean(localPersistence.redis_port && localPersistence.mongo_port)
    }

    if (localPersistence.type === "morkdb") {
      return Boolean(localPersistence.mork_port && localPersistence.mongo_port)
    }

    return false
  }

  const handleSave = () => {
    const cleanedPeers = Object.values(peersRefs.current)
      .filter(peer => {
        if (!peer.type) return false
        if (peer.type === "redismongodb" && (!peer.redis_port || !peer.mongo_port)) return false
        if (peer.type === "morkdb" && (!peer.mork_port || !peer.mongo_port)) return false
        if (!isValidLocalPersistence(peer.local_persistence)) return false
        return true
      })
      .map(peer => structuredClone(peer))

    const nextAtomdb = {
      atomdb_type: "remotedb",
      remote_peers: cleanedPeers,
    }
    if (config.atomdb && "atomdb_uid" in config.atomdb) {
      nextAtomdb.atomdb_uid = config.atomdb.atomdb_uid
    }
    if (config.atomdb && "composite_type_enabled" in config.atomdb) {
      nextAtomdb.composite_type_enabled = config.atomdb.composite_type_enabled
    }

    updateField("atomdb", nextAtomdb)

    showToast({ message: "AtomDB settings applied", severity: "success" })
  }

  return (
    <ConfigForm onSubmit={handleSave}>
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
                const current = peersRefs.current[peer.id]
                current.type = val
                setPeers(prev =>
                  prev.map(p => p.id === peer.id ? {
                    ...p,
                    type: val,
                    initialValues: { ...current },
                  } : p)
                )
              }}
            >
              <MenuItem value="redismongodb">Redis + Mongo</MenuItem>
              <MenuItem value="morkdb">Mork + Mongo</MenuItem>
              <MenuItem value="inmemorydb">In Memory</MenuItem>
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

          {peer.type === "redismongodb" && (
            <RedisMongoSubForm
              key={`${peer.id}-main-redis`}
              category="main"
              initialValues={peer.initialValues}
              onChange={(data, cat) => updatePeer(peer.id, data, cat)}
            />
          )}

          {peer.type === "morkdb" && (
            <MorkMongoSubForm
              key={`${peer.id}-main-mork`}
              category="main"
              initialValues={peer.initialValues}
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
                const current = peersRefs.current[peer.id]
                const previous = current.local_persistence || {}
                const next = { ...previous, type: val }
                if (val !== "inmemorydb" && !next.context) {
                  next.context = `${current.context || ""}local_`
                }
                current.local_persistence = next
                setPeers(prev =>
                  prev.map(p => p.id === peer.id ? {
                    ...p,
                    localType: val,
                    initialValues: {
                      ...(p.initialValues || {}),
                      local_persistence: { ...next },
                    },
                  } : p)
                )
              }}
            >
              <MenuItem value="inmemorydb">In Memory</MenuItem>
              <MenuItem value="redismongodb">Redis + MongoDB</MenuItem>
              <MenuItem value="morkdb">MorkDB + MongoDB</MenuItem>
            </TextField>
          </GridSpan12>

          {peer.localType === "redismongodb" && (
            <RedisMongoSubForm
              key={`${peer.id}-local-redis`}
              category="local"
              initialValues={peer.initialValues?.local_persistence}
              onChange={(data, cat) => updatePeer(peer.id, data, cat)}
            />
          )}

          {peer.localType === "morkdb" && (
            <MorkMongoSubForm
              key={`${peer.id}-local-mork`}
              category="local"
              initialValues={peer.initialValues?.local_persistence}
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
          type="submit"
        >
          Apply AtomDB settings
        </SaveButton>
      </ActionButtonContainer>
    </ConfigForm>
  )
}