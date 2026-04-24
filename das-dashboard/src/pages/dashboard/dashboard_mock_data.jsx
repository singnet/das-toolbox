export const mockMachines = [
  {
    serverIp: "192.168.120.1",
    running: true,

    metrics: {
      timestamps: ["10:00", "10:05", "10:10", "10:15", "10:20", "10:25"],

      agents: [
        {
          name: "attention-broker",
          cpu: [20, 30, 50, 40, 60, 45],
          memory: [1200, 1300, 1400, 1350, 1500, 1480],
        },
        {
          name: "query-engine",
          cpu: [10, 20, 30, 25, 35, 30],
          memory: [800, 850, 900, 950, 1000, 980],
        },
        {
          name: "mongodb",
          cpu: [40, 45, 50, 55, 60, 65],
          memory: [2000, 2100, 2200, 2300, 2400, 2500],
        },
        {
          name: "redis",
          cpu: [5, 10, 8, 12, 9, 7],
          memory: [80, 85, 90, 95, 100, 105],
        },
      ],
    },

    agents: [
      {
        name: "attention-broker",
        port: 40001,
        status: "Running",
        age: "2h",
        memory: "1200MB",
        cpu: "45%"
      },
      {
        name: "query-engine",
        port: 40002,
        status: "Running",
        age: "5h",
        memory: "800MB",
        cpu: "30%"
      },
      {
        name: "mongodb",
        port: 40020,
        status: "Running",
        age: "1d",
        memory: "2048MB",
        cpu: "13%"
      },
      {
        name: "redis",
        port: 40021,
        status: "Running",
        age: "1d",
        memory: "80MB",
        cpu: "7%"
      },
    ],
  },

  {
    serverIp: "192.168.199.128",
    running: true,

    metrics: {
      timestamps: ["10:00", "10:05", "10:10", "10:15", "10:20", "10:25"],

      agents: [
        {
          name: "context-broker",
          cpu: [15, 20, 25, 30, 28, 35],
          memory: [200, 250, 300, 350, 400, 450],
        },
        {
          name: "link-creation-agent",
          cpu: [5, 10, 12, 8, 15, 10],
          memory: [95, 100, 110, 105, 115, 120],
        },
      ],
    },

    agents: [
      {
        name: "context-broker",
        port: 40004,
        status: "Running",
        age: "1d",
        memory: "200MB",
        cpu: "20%"
      },
      {
        name: "link-creation-agent",
        port: 40007,
        status: "Running",
        age: "30m",
        memory: "95MB",
        cpu: "35%"
      },
    ],
  },

  {
    serverIp: "192.168.87.122",
    running: false,

    metrics: {
      timestamps: ["10:00", "10:05", "10:10", "10:15", "10:20", "10:25"],
      agents: [],
    },

    agents: [],
  },
];