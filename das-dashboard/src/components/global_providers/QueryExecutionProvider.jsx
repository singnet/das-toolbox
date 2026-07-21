import { createContext, useContext } from "react";
import { useQueryExecution } from "../../hooks/useQueryExecution";
import { QueryParametersProvider, useQueryParameters } from "../../hooks/useQueryParameters";

const QueryExecutionContext = createContext(null);

function QueryExecutionProviderInner({ children }) {
  const parameters = useQueryParameters();
  const queryExecution = useQueryExecution(parameters);

  return (
    <QueryExecutionContext.Provider value={queryExecution}>
      {children}
    </QueryExecutionContext.Provider>
  );
}

export function QueryExecutionProvider({ children }) {
  return (
    <QueryParametersProvider>
      <QueryExecutionProviderInner>{children}</QueryExecutionProviderInner>
    </QueryParametersProvider>
  );
}

export function useQueryExecutionContext() {
  const context = useContext(QueryExecutionContext);
  if (!context) {
    throw new Error("useQueryExecutionContext must be used inside QueryExecutionProvider");
  }
  return context;
}
