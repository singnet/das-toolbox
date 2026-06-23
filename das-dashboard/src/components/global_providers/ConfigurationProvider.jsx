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
  const [configSeed, setConfigSeed] = useState(0)

  const defaultsRef = useRef({})
  const atomdbTemplatesRef = useRef({})

  useEffect(() => {
    async function fetchDefaults() {
      try {
        const response = await getConfigDefaults()
        defaultsRef.current = response.content || {}
        atomdbTemplatesRef.current = response.atomdb_templates || {}
        setConfig(defaultsRef.current)
        setConfigSeed((seed) => seed + 1)
      } catch (error) {
        console.error(error)
      }
    }

    fetchDefaults()
  }, [])

  const getDefaults = useCallback(() => defaultsRef.current, [])

  const getDefaultSection = useCallback((sectionKey) => {
    return defaultsRef.current[sectionKey]
  }, [])

  const getAtomdbTemplate = useCallback((atomdbType) => {
    return atomdbTemplatesRef.current[atomdbType]
  }, [])

  const updateField = useCallback((fieldName, value) => {
    setConfig((prev) => ({
      ...prev,
      [fieldName]: value
    }))
  }, [])

  const applyLoadedConfiguration = useCallback((flat) => {
    defaultsRef.current = flat
    setConfig(flat)
    setConfigSeed((seed) => seed + 1)
  }, [])

  const resetConfiguration = useCallback(async () => {
    const response = await getConfigDefaults({ factory: true })
    defaultsRef.current = response.content || {}
    atomdbTemplatesRef.current = response.atomdb_templates || {}
    setConfig(defaultsRef.current)
    setConfigSeed((seed) => seed + 1)
  }, [])

  return (
    <ConfigContext.Provider
      value={{
        config,
        configSeed,
        updateField,
        getDefaults,
        getDefaultSection,
        getAtomdbTemplate,
        applyLoadedConfiguration,
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
