/**
 * Application State Context
 * 
 * Provides global state management for the database query tool application.
 * Manages database connections, selected database, and cross-component communication.
 */

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { message } from 'antd';
import { apiClient, DatabaseConnection, DatabaseMetadata } from '../services/api';

// State interface
interface AppState {
  databases: DatabaseConnection[];
  selectedDatabase: string | null;
  metadata: DatabaseMetadata | null;
  loading: {
    databases: boolean;
    metadata: boolean;
  };
  error: string | null;
}

// Action types
type AppAction =
  | { type: 'SET_LOADING'; payload: { key: keyof AppState['loading']; value: boolean } }
  | { type: 'SET_DATABASES'; payload: DatabaseConnection[] }
  | { type: 'SET_SELECTED_DATABASE'; payload: string | null }
  | { type: 'SET_METADATA'; payload: DatabaseMetadata | null }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'ADD_DATABASE'; payload: DatabaseConnection }
  | { type: 'UPDATE_DATABASE'; payload: DatabaseConnection }
  | { type: 'REMOVE_DATABASE'; payload: string };

// Initial state
const initialState: AppState = {
  databases: [],
  selectedDatabase: null,
  metadata: null,
  loading: {
    databases: false,
    metadata: false,
  },
  error: null,
};

// Reducer
function appStateReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: {
          ...state.loading,
          [action.payload.key]: action.payload.value,
        },
      };
    case 'SET_DATABASES':
      return {
        ...state,
        databases: action.payload,
      };
    case 'SET_SELECTED_DATABASE':
      return {
        ...state,
        selectedDatabase: action.payload,
        // Clear metadata when database changes
        metadata: action.payload === state.selectedDatabase ? state.metadata : null,
      };
    case 'SET_METADATA':
      return {
        ...state,
        metadata: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    case 'ADD_DATABASE':
      return {
        ...state,
        databases: [...state.databases, action.payload],
      };
    case 'UPDATE_DATABASE':
      return {
        ...state,
        databases: state.databases.map(db =>
          db.name === action.payload.name ? action.payload : db
        ),
      };
    case 'REMOVE_DATABASE':
      return {
        ...state,
        databases: state.databases.filter(db => db.name !== action.payload),
        // Clear selection if the removed database was selected
        selectedDatabase: state.selectedDatabase === action.payload ? null : state.selectedDatabase,
        metadata: state.selectedDatabase === action.payload ? null : state.metadata,
      };
    default:
      return state;
  }
}

// Context interface
interface AppStateContextType {
  state: AppState;
  actions: {
    loadDatabases: () => Promise<void>;
    selectDatabase: (databaseName: string | null) => Promise<void>;
    addDatabase: (database: DatabaseConnection) => void;
    updateDatabase: (database: DatabaseConnection) => void;
    removeDatabase: (databaseName: string) => void;
    refreshMetadata: () => Promise<void>;
    clearError: () => void;
  };
}

// Create context
const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

// Provider component
interface AppStateProviderProps {
  children: ReactNode;
}

export const AppStateProvider: React.FC<AppStateProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appStateReducer, initialState);

  // Load databases on mount
  useEffect(() => {
    loadDatabases();
  }, []);

  // Load metadata when selected database changes
  useEffect(() => {
    if (state.selectedDatabase) {
      loadMetadata(state.selectedDatabase);
    }
  }, [state.selectedDatabase]);

  const loadDatabases = async () => {
    dispatch({ type: 'SET_LOADING', payload: { key: 'databases', value: true } });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const databases = await apiClient.getDatabases();
      dispatch({ type: 'SET_DATABASES', payload: databases });
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to load databases';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      message.error(errorMessage);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'databases', value: false } });
    }
  };

  const loadMetadata = async (databaseName: string) => {
    dispatch({ type: 'SET_LOADING', payload: { key: 'metadata', value: true } });
    
    try {
      const metadata = await apiClient.getDatabaseMetadata(databaseName);
      dispatch({ type: 'SET_METADATA', payload: metadata });
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to load database metadata';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      message.error(errorMessage);
      dispatch({ type: 'SET_METADATA', payload: null });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'metadata', value: false } });
    }
  };

  const selectDatabase = async (databaseName: string | null) => {
    dispatch({ type: 'SET_SELECTED_DATABASE', payload: databaseName });
  };

  const addDatabase = (database: DatabaseConnection) => {
    dispatch({ type: 'ADD_DATABASE', payload: database });
  };

  const updateDatabase = (database: DatabaseConnection) => {
    dispatch({ type: 'UPDATE_DATABASE', payload: database });
  };

  const removeDatabase = (databaseName: string) => {
    dispatch({ type: 'REMOVE_DATABASE', payload: databaseName });
  };

  const refreshMetadata = async () => {
    if (state.selectedDatabase) {
      await loadMetadata(state.selectedDatabase);
    }
  };

  const clearError = () => {
    dispatch({ type: 'SET_ERROR', payload: null });
  };

  const contextValue: AppStateContextType = {
    state,
    actions: {
      loadDatabases,
      selectDatabase,
      addDatabase,
      updateDatabase,
      removeDatabase,
      refreshMetadata,
      clearError,
    },
  };

  return (
    <AppStateContext.Provider value={contextValue}>
      {children}
    </AppStateContext.Provider>
  );
};

// Hook to use the context
export const useAppState = (): AppStateContextType => {
  const context = useContext(AppStateContext);
  if (context === undefined) {
    throw new Error('useAppState must be used within an AppStateProvider');
  }
  return context;
};

export default AppStateContext;