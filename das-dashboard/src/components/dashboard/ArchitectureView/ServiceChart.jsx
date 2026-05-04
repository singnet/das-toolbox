import { Box, Typography } from "@mui/material";
import { CPUViewChart } from "../MainContent/CPUViewChart";
import { MemoryViewChart } from "../MainContent/MemoryViewChart";

export function ServiceChart({ selectedMachine, selectedService }){
    return (
        <Box mt={4}>
            <Typography
            variant="h6"
            fontWeight="bold"
            mb={2}
            >
            Metrics — {selectedService.displayName}
            </Typography>

            <Box
                display="grid"
                gridTemplateColumns={{
                    xs: "1fr",
                    lg: "1fr 1fr",
                }}
                gap={3}
                >
                <Box
                    sx={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: 0,
                    p: 2,
                    overflow: "hidden",
                    minHeight: 320,
                    maxHeight: 320,
                    }}
                >
                    <Typography
                    fontSize={12}
                    fontWeight={700}
                    color="#475569"
                    mb={1.5}
                    textTransform="uppercase"
                    letterSpacing={0.5}
                    >
                    CPU Usage In-Time
                    </Typography>

                    <Box
                    sx={{
                        width: "100%",
                        height: 250,
                        overflow: "hidden",
                    }}
                    >
                    <CPUViewChart machine={selectedMachine} />
                    </Box>
                </Box>

                <Box
                    sx={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: 0,
                    p: 2,
                    overflow: "hidden",
                    minHeight: 320,
                    maxHeight: 320,
                    }}
                >
                    <Typography
                    fontSize={12}
                    fontWeight={700}
                    color="#475569"
                    mb={1.5}
                    textTransform="uppercase"
                    letterSpacing={0.5}
                    >
                    Memory Usage In-Time
                    </Typography>

                    <Box
                    sx={{
                        width: "100%",
                        height: 250,
                        overflow: "hidden",
                    }}
                    >
                    <MemoryViewChart machine={selectedMachine} />
                    </Box>
                </Box>
            </Box>
        </Box>
    )
}