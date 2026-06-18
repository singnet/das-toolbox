import { useContext, useState, createContext, useEffect } from "react"
import { getConfigDefaults } from "../../api/ConfigAPI"

const ConfigContext = createContext(null)

export function ConfigurationProvider({ children }) {
  const [config, setConfig] = useState({})
  let configDefaults = {}

  useEffect(() => {

      const fetchDefaults = async () => {
        try{
          const response = await getConfigDefaults()
          configDefaults = response.content
        }
        catch (error) {
            console.error(error)
        }
      }

      fetchDefaults()
  }, [])


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

  const getDefault = ( dictionaryKey ) => { 
    try{
      return configDefaults[dictionaryKey]
    }
    catch (error){
      return { }
    }
  }

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
