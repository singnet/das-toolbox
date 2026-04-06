import {
  Box,
  Button,
  TextField,
  Typography,
  MenuItem,
  Paper,
  Divider
} from "@mui/material"
import { useState, useRef } from "react"
import { RedisMongoSubForm } from "./RedisMongoSubForm"
import { MorkMongoSubForm } from "./MorkMongoSubForm"
import { useConfig } from "../../../global_components/ConfigurationProvider"
import { useToast } from "../../../global_components/ToastProvider"

export function RemoteDBOptions() {

  const { updateSection } = useConfig()
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

  const updatePeer = (id, subFormData, category) => {
    const base = peersRefs.current[id]

    if (category === "main") {
      const cleaned = {
        uid: base.uid,
        context: base.context,
        type: subFormData.type,
        local_persistence: base.local_persistence || { type: "inmemorydb" }
      }

      if (subFormData.type === "redismongodb") {
        peersRefs.current[id] = {
          ...cleaned,
          redis: subFormData.redis,
          mongodb: subFormData.mongodb
        }
      }

      if (subFormData.type === "morkmongodb") {
        peersRefs.current[id] = {
          ...cleaned,
          mongodb: subFormData.mongodb,
          morkdb: subFormData.morkdb
        }
      }
    }

    if (category === "local") {
      if (subFormData.type === "redismongodb") {
        peersRefs.current[id].local_persistence = {
          type: "redismongodb",
          context: `${base.context}local_`,
          redis: subFormData.redis,
          mongodb: subFormData.mongodb
        }
      }

      if (subFormData.type === "morkmongodb") {
        peersRefs.current[id].local_persistence = {
          type: "morkmongodb",
          context: `${base.context}local_`,
          mongodb: subFormData.mongodb,
          morkdb: subFormData.morkdb
        }
      }
    }
  }

  const handleSave = () => {
    const cleanedPeers = Object.values(peersRefs.current)
      .filter(peer => {
        if (!peer.type) return false

        if (peer.type === "redismongodb" && (!peer.redis || !peer.mongodb)) return false
        if (peer.type === "morkmongodb" && (!peer.mongodb || !peer.morkdb)) return false

        return true
      })
      .map(peer => {
        const base = {
          uid: peer.uid,
          type: peer.type,
          context: peer.context
        }

        if (peer.type === "redismongodb") {
          base.redis = peer.redis
          base.mongodb = peer.mongodb
        }

        if (peer.type === "morkmongodb") {
          base.mongodb = peer.mongodb
          base.morkdb = peer.morkdb
        }

        const lp = peer.local_persistence || { type: "inmemorydb" }

        base.local_persistence = {
          type: lp.type,
          context: `${peer.context}local_`,
          ...(lp.redis && { redis: lp.redis }),
          ...(lp.mongodb && { mongodb: lp.mongodb }),
          ...(lp.morkdb && { morkdb: lp.morkdb })
        }

        return base
      })

    updateSection("atomdb", {
      remote_peers: cleanedPeers
    })
  }

  return (
    <Box sx={{ mt: 1 }}>
      <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
        Remote Peers List
      </Typography>

      {peers.map(peer => (
        <Paper key={peer.id} variant="outlined" sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
            <TextField
              label="Peer UID"
              size="small"
              value={peer.uid}
              disabled
            />

            <TextField
              select
              label="Main Connection"
              size="small"
              value={peer.type}
              onChange={e => {
                const val = e.target.value

                peersRefs.current[peer.id].type = val

                setPeers(prev =>
                  prev.map(p =>
                    p.id === peer.id ? { ...p, type: val } : p
                  )
                )
              }}
            >
              <MenuItem value="redismongodb">Redis + Mongo</MenuItem>
              <MenuItem value="morkmongodb">Mork + Mongo</MenuItem>
            </TextField>
          </Box>

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

          <Divider sx={{ my: 2 }} />

          <Typography variant="caption">
            LOCAL PERSISTENCE TYPE
          </Typography>

          <TextField
            select
            fullWidth
            size="small"
            value={peer.localType}
            sx={{ mt: 1 }}
            onChange={e => {
              const val = e.target.value

              setPeers(prev =>
                prev.map(p =>
                  p.id === peer.id ? { ...p, localType: val } : p
                )
              )

              if (val === "inmemorydb") {
                peersRefs.current[peer.id].local_persistence = {
                  type: "inmemorydb"
                }
              } else {
                peersRefs.current[peer.id].local_persistence = {}
              }
            }}
          >
            <MenuItem value="inmemorydb">In Memory</MenuItem>
            <MenuItem value="redismongodb">Redis + MongoDB</MenuItem>
            <MenuItem value="morkmongodb">MorkDB + MongoDB</MenuItem>
          </TextField>

          {peer.localType === "redismongodb" && (
            <RedisMongoSubForm
              category="local"
              onChange={(data, cat) => updatePeer(peer.id, data, cat)}
            />
          )}

          {peer.localType === "morkmongodb" && (
            <MorkMongoSubForm
              category="local"
              onChange={(data, cat) => updatePeer(peer.id, data, cat)}
            />
          )}
        </Paper>
      ))}

      <Button onClick={addPeer} fullWidth>
        + Add Peer
      </Button>

      <Button onClick={() => {
        handleSave()
        showToast("AtomDB saved successfully!")
      }
      } fullWidth color="success">
        Save
      </Button>
    </Box>
  )
}