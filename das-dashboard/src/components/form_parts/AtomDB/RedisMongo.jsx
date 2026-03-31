import { TextField, FormControlLabel, Checkbox, Button } from "@mui/material"
import { useState, useRef } from "react"
import { ClusterForm } from "./ClusterForm"

export function RedisMongoOptions({ onSave }) {

  const form = useRef({
    redisPort: "", 
    mongoPort: "",
    mongoUser: "",
    mongoPass: "",
    redisCluster: false, 
    mongoCluster: false,
    redisNodes: [], 
    mongoNodes: []
  })

  const [showRedis, setShowRedis] = useState(false)
  const [showMongo, setShowMongo] = useState(false)

  const handleSave = () => {

    const defaultNode = [{ context: "default", ip: "localhost", username: "root" }];

    const getSafeNodes = (isCluster, nodes) => {
        if (isCluster && nodes && nodes.length > 0) return nodes;
        return defaultNode;
    };

    const data = form.current
    const section = {
      "redis": { 
        "endpoint": `localhost:${data.redisPort}`,
        "cluster": data.redisCluster, 
        "nodes": getSafeNodes(data.redisCluster, data.redisNodes)
    },

      "mongodb": { 
        "endpoint": `localhost:${data.mongoPort}`, 
        "username": data.mongoUser, 
        "password": data.mongoPass,
        "cluster": data.mongoCluster, 
        "cluster_secret_key": "None",
        "nodes": getSafeNodes(data.mongoCluster, data.mongoNodes)
      }
    }
    onSave(section)
  }

  return (
    <>
        <TextField fullWidth label="Redis Port" type="number" margin="normal" defaultValue={40020} 
        onChange={(e) => form.current.redisPort = e.target.value} />
        
        <TextField fullWidth label="Mongo Port" type="number" margin="normal" defaultValue={40021}
        onChange={(e) => form.current.mongoPort = e.target.value} />

        <TextField fullWidth label="MongoDB Username" type="text" margin="normal" defaultValue={"admin"} 
            onChange={(e) => form.current.mongoUser = e.target.value} />
        
        <TextField fullWidth label="MongoDB Password" type="password" margin="normal" defaultValue={"admin"}
            onChange={(e) => form.current.mongoPass = e.target.value} />

        <FormControlLabel label="Mongo Cluster" control={
        <Checkbox onChange={(e) => { 
            form.current.mongoCluster = e.target.checked
            setShowMongo(e.target.checked) 
        }} />
        }/>

        <FormControlLabel label="Redis Cluster" control={
        <Checkbox onChange={(e) => { 
            form.current.redisCluster = e.target.checked
            setShowRedis(e.target.checked) 
        }} />
        }/>

        {showRedis && <ClusterForm onChange={(nodes) => form.current.redisNodes = nodes} />}
        {showMongo && <ClusterForm onChange={(nodes) => form.current.mongoNodes = nodes} />}

        <Button variant="contained" color="success" onClick={handleSave} sx={{ mt: 2 }}>
        Save AtomDB Section
        </Button>
    </>
  )
}