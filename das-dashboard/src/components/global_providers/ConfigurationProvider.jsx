import { useContext, useState, createContext } from "react"
import { DEFAULT_JSON, DEFAULT_REDISMONGO_SCHEMA } from "../../assets/default_json"

const ConfigContext = createContext(null)

export function ConfigurationProvider({ children }) {
  const [config, setConfig] = useState(() => structuredClone(DEFAULT_REDISMONGO_SCHEMA))

  const updateField = (fieldName, value) => {
    setConfig((prev) => ({
      ...prev,
      [fieldName]: value
    }))

    sessionStorage.setItem(
      `config_${fieldName}`,
      JSON.stringify(value)
    )
  }

  const updateSection = (sectionName, value) => {
    setConfig((prev) => {
      const next = { ...prev, [sectionName]: value }
      sessionStorage.setItem(`config_${sectionName}`, JSON.stringify(value))
      return next
    })
  }

  const getDefault = () => DEFAULT_JSON

  const loadExternalConfiguration = ({ parsed }) => {
    setConfig(parsed)

    Object.entries(parsed).forEach(([key, value]) => {
      sessionStorage.setItem(`config_${key}`, JSON.stringify(value))
    })

    location.reload()
  }

  const resetConfiguration = () => {
    setConfig(structuredClone(DEFAULT_REDISMONGO_SCHEMA))
    sessionStorage.clear()
    location.reload()
  }

  return (
    <ConfigContext.Provider value={{
      config,
      updateField,
      updateSection,
      getDefault,
      loadExternalConfiguration,
      resetConfiguration
    }}>
      {children}
    </ConfigContext.Provider>
  )
}

export function useConfig() {
  return useContext(ConfigContext)
}
