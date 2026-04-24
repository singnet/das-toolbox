import { createContext, useContext, useState } from "react";

const DashboardContext = createContext(null)

export default function DashboardContextProvider( { children } ) {

    const [currentContext, setCurrentContext] = useState(null)
    const [currentMachine, setCurrentMachine] = useState(null)
    const [currentService, setCurrentService] = useState(null)

    const getCurrentContext = () => currentContext;
    const getCurrentMachine = () => currentMachine;
    const getCurrentService = () => currentService;

    return (
        <DashboardContext.Provider
        value={{
            currentMachine,
            setCurrentMachine,
            currentService,
            setCurrentService,
        }}
        >
            {children}
        </DashboardContext.Provider>
    )

}

export function useDashboardContext() {
  const context = useContext(DashboardContext)

  if (!context) {
    throw new Error("DashboardContext must be used with a DashboardContextProvider!")
  }

  return context
}