import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState
} from "react"
import { getConfigDefaults } from "../../api/ConfigAPI"

const ConfigContext = createContext(null)

export function ConfigurationProvider({ children }) {
  const [config, setConfig] = useState({})
  const configDefaultsRef = useRef({})

  useEffect(() => {
    async function fetchDefaults() {
      try {
        const response = await getConfigDefaults()
        configDefaultsRef.current = response.content || {}
      } catch (error) {
        console.error(error)
      }
    }

    fetchDefaults()
  }, [])

  const getDefault = useCallback((dictionaryKey) => {
    return configDefaultsRef.current[dictionaryKey]
  }, [])

  const updateField = useCallback((fieldName, value) => {
    setConfig((prev) => ({
      ...prev,
      [fieldName]: value
    }))

    sessionStorage.setItem(`config_${fieldName}`, JSON.stringify(value))
  }, [])

  const loadExternalConfiguration = useCallback(({ parsed }) => {
    setConfig(parsed)

    Object.entries(parsed).forEach(([key, value]) => {
      sessionStorage.setItem(`config_${key}`, JSON.stringify(value))
    })
  }, [])

  const resetConfiguration = useCallback(() => {
    setConfig({})
    sessionStorage.clear()
  }, [])

  return (
    <ConfigContext.Provider
      value={{
        config,
        updateField,
        getDefault,
        loadExternalConfiguration,
        resetConfiguration
      }}
    >
      {children}
    </ConfigContext.Provider>
  )
}

export function useConfig() {
  const context = useContext(ConfigContext)
  if (!context) {
    throw new Error("useConfig must be used within ConfigurationProvider")
  }
  return context
}
