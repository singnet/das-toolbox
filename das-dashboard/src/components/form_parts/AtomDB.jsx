import {
  Box,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
  Divider,
  MenuItem,
  AccordionDetails
} from "@mui/material"


const ATOMDB_TYPES = {
    "Redis + MongoDB": "redismongo",
    "Mork + MongoDB": "morkmongo",
    "InMemoryDB": "inmemorydb",
    "RemoteDB": "remotedb"
}

function RedisMongoOptions({ config, onChange }) {
    return (
        <div>
            <TextField
                fullWidth
                label="Redis Port"
                type="number"
                margin="normal"
                value={config.atomdb.redis.port}
                onChange={(e) =>
                    onChange("atomdb.redis.port", Number(e.target.value))
                }
            />

            <TextField
                fullWidth
                label="MongoDB Port"
                type="number"
                margin="normal"
                value={config.atomdb.mongodb.port}
                onChange={(e) =>
                    onChange("atomdb.mongodb.port", Number(e.target.value))
                }
                >
            </TextField>

            <FormControlLabel
                control={
                    <Switch
                    checked={config.atomdb.redis.cluster}
                    onChange={(e) =>
                        onChange("atomdb.redis.cluster", e.target.checked)
                    }
                    />
                }
                label="Redis Cluster"
            />
        </div>
    )
}

function MorkMongoOptions({ config, onChange }) {

    return (
        <div>
            <TextField
                fullWidth
                label="MorkDB Port"
                type="number"
                margin="normal"
                value={config.atomdb.mork.port}
                onChange={(e) =>
                    onChange("atomdb.morkdb.port", Number(e.target.value))
                }
            />

            <TextField
                fullWidth
                label="MongoDB Port"
                type="number"
                margin="normal"
                value={config.atomdb.mongodb.port}
                onChange={(e) =>
                    onChange("atomdb.mongodb.port", Number(e.target.value))
                }
            />
        </div>
    )

}

function RemoteDbOptions({ config, onChange }) {

}

export default function AtomDBForm({ config, onChange }) {

    return (
        <Accordion>
            <AccordionSummary>
                <Typography sx={{ mt: 2 }}>AtomDB</Typography>
            </AccordionSummary>

            <AccordionDetails>
                <TextField
                select
                fullWidth
                label="Type"
                margin="normal"
                value={config.atomdb.type}
                onChange={(e) =>
                    onChange("atomdb.type", e.target.value)
                }
                >
                    {Object.keys(ATOMDB_TYPES).map((key) => (
                        <MenuItem key={key} value={ATOMDB_TYPES[key]}>
                        {key}
                        </MenuItem>
                    ))}
                </TextField>

                {config.atomdb.type === "redismongo" && (
                    <RedisMongoOptions config={config} onChange={onChange} />
                )}
                {config.atomdb.type === "morkmongo" && (
                    <MorkMongoOptions config={config} onChange={onChange} />
                )}
                {config.atomdb.type === "remotedb" && (
                    <RemoteDbOptions config={config} onChange={onChange} />
                )}
            </AccordionDetails>
        </Accordion>
    )
}