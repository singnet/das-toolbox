import { Button, Checkbox, FormControlLabel, TextField } from "@mui/material"
import { useRef, useState } from "react"
import { ClusterForm } from "./ClusterForm"

export function MorkMongoOptions ({ onSave }) {

  const form = useRef({
      morkPort: "",
      mongoPort: "",
      mongoUser: "",
      mongoPass: "",
      mongoCluster: false,
      mongoNodes: [],
  })

  const [showMongo, setShowMongo] = useState(false)
  
  const handleSave = () => {
    const data = form.current

    const defaultNode = [{ context: "default", ip: "localhost", username: "root" }];

    const getSafeNodes = (isCluster, nodes) => {
      if (isCluster && nodes && nodes.length > 0) return nodes;
      return defaultNode;
    };

    const section = {

      "mongodb": {
        "endpoint": `localhost:${data.mongoPort}`,
        "username": data.mongoUser,
        "password": data.mongoPass,
        "cluster": data.mongoCluster,
        "cluster_secret_key": "None",
        "nodes": getSafeNodes(data.mongoCluster, data.mongoNodes)
      },
      "morkdb": {
        "endpoint": `localhost:${data.morkPort}`
      }

    }

    onSave(section)
  }

  return (
    <>
      <TextField
        fullWidth
        label="MorkDB Port"
        type="number"
        margin="normal"
        defaultValue={40022}
        onChange={(e) =>
          form.morkPort = e.target.value
        }
      />

      <TextField
        fullWidth
        label="MongoDB Port"
        type="number"
        margin="normal"
        onChange={(e) =>
          form.mongoPort = e.target.value
        }
        defaultValue={40021}
      />

      <TextField
        fullWidth
        label="MongoDB Username"
        type="text"
        margin="normal"
        onChange={(e) =>
          form.mongoUser = e.target.value
        }
        defaultValue={"admin"}
      />

      <TextField
        fullWidth
        label="MongoDB Password"
        type="password"
        margin="normal"
        onChange={(e) =>
          form.mongoPass = e.target.value
        }
        defaultValue={"admin"}
      />

      <FormControlLabel label="Mongo Cluster" control={
      <Checkbox onChange={(e) => { 
          form.current.mongoCluster = e.target.checked
          setShowMongo(e.target.checked) 
      }} />
      }/>

      {showMongo && <ClusterForm onChange={(nodes) => form.current.mongoNodes = nodes} />}

      <Button variant="contained" color="success" onClick={handleSave} sx={{ mt: 2 }}>
        Save AtomDB Section
      </Button>
    </>
  )
}