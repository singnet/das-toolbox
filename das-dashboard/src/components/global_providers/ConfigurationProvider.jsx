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

function syncAtomdbTemplate(templates, atomdbSection) {
  if (!atomdbSection?.atomdb_type) {
    return templates
  }

  return {
    ...templates,
    [atomdbSection.atomdb_type]: atomdbSection
  }
}

export function ConfigurationProvider({ children }) {
  const [config, setConfig] = useState({})
  const defaultsRef = useRef({})
  const atomdbTemplatesRef = useRef({})

  useEffect(() => {
    async function fetchDefaults() {
      try {
        const response = await getConfigDefaults()
        defaultsRef.current = response.content || {}
        atomdbTemplatesRef.current = response.atomdb_templates || {}
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

    sessionStorage.setItem(`config_${fieldName}`, JSON.stringify(value))
  }, [])

  const applyLoadedConfiguration = useCallback((flat) => {
    defaultsRef.current = flat
    atomdbTemplatesRef.current = syncAtomdbTemplate(atomdbTemplatesRef.current, flat.atomdb)
    setConfig(flat)

    Object.entries(flat).forEach(([key, value]) => {
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
