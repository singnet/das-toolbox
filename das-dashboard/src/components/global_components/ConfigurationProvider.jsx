import { useContext, useState, createContext } from "react";
import { DEFAULT_JSON } from "../../assets/default_json";

const ConfigContext = createContext(null)
const DEFAULT_CONFIGURATION = structuredClone(DEFAULT_JSON)

export function ConfigurationProvider({ children }){

    const [config, setConfig] = useState(
        {
            "schema_version": "1.0",
            "atomdb": {},
            "loaders": {
                "metta": {
                    "image": "trueagi/das:1.0.0-metta-parser"
                },
                "morkdb": {
                    "image": "trueagi/das:mork-loader-1.0.5"
                }
            },
            "agents": {},
            "brokers": {},
            "params": {},
            "environment": {}
        }
    )

    const getDefault = () => {
        return new Proxy(DEFAULT_CONFIGURATION, {
            get(target, prop) {
            try {
                const saved = sessionStorage.getItem(`config_${prop}`)
                if (saved) return JSON.parse(saved)
            } catch (e) {}

            return target[prop]
            }
        })
    }

    const updateSection = (sectionName, sectionData) => {
        setConfig(prev => ({
            ...prev,
            [sectionName]: sectionData
        }))

        sessionStorage.setItem(
            `config_${sectionName}`,
            JSON.stringify(sectionData)
        )
    }

    return(
        <ConfigContext.Provider value={{config, updateSection, getDefault}}>
            { children }
        </ConfigContext.Provider>
    )

}

export function useConfig() {
    return useContext(ConfigContext)
}

//   const updateSection = (sectionName, data) => {
//     setConfig(prev => ({
//       schema_version: prev.schema_version,
//       atomdb: sectionName === "atomdb" ? data : prev.atomdb,
//       loaders: prev.loaders,
//       agents: sectionName === "agents" ? data : prev.agents,
//       brokers: sectionName === "brokers" ? data : prev.brokers,
//       params: sectionName === "params" ? data : prev.params,
//       environment: sectionName === "environment" ? data : prev.environment
//     }))
//   } Just a later example to use.