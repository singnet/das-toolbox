import { useContext, useState, createContext } from "react";
import { DEFAULT_JSON, DEFAULT_REDISMONGO_SCHEMA } from "../../assets/default_json";

const ConfigContext = createContext(null)
const DEFAULT_VALUES = structuredClone(DEFAULT_JSON)

export function ConfigurationProvider({ children }){

    const [config, setConfig] = useState(structuredClone(DEFAULT_REDISMONGO_SCHEMA))

    const getDefault = () => {
        return new Proxy(DEFAULT_VALUES, {
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

    const loadExternalConfiguration = (file) => {
        const newConfig = file
        setConfig(newConfig)

        Object.entries(file).forEach(([key, value]) => {
            sessionStorage.setItem(`config_${key}`, JSON.stringify(value))
        })

        location.reload()
    }

    const resetConfiguration = () => {
        setConfig(structuredClone(DEFAULT_REDISMONGO_SCHEMA))
        sessionStorage.clear()
        location.reload()
    }

    return(
        <ConfigContext.Provider value={{config, updateSection, getDefault, loadExternalConfiguration, resetConfiguration}}>
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