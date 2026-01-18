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
  selectedDatabase: string | null;  // 存储 id
  metadata: DatabaseMetadata | null;
  loading: {
    databases: boolean;
    metadata: boolean;
  };
  switchingDatabase: boolean;
  error: string | null;
}

// Action types
type AppAction =
  | { type: 'SET_LOADING'; payload: { key: keyof AppState['loading']; value: boolean } }
  | { type: 'SET_DATABASES'; payload: DatabaseConnection[] }
  | { type: 'SET_SELECTED_DATABASE'; payload: string | null }  // id
  | { type: 'SET_METADATA'; payload: DatabaseMetadata | null }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'ADD_DATABASE'; payload: DatabaseConnection }
  | { type: 'UPDATE_DATABASE'; payload: DatabaseConnection }
  | { type: 'REMOVE_DATABASE'; payload: string }  // id
  | { type: 'START_DATABASE_SWITCH' }
  | { type: 'COMPLETE_DATABASE_SWITCH' };

// Initial state
const initialState: AppState = {
  databases: [],
  selectedDatabase: null,
  metadata: null,
  loading: {
    databases: false,
    metadata: false,
  },
  switchingDatabase: false,
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
      console.log('Reducer: SET_SELECTED_DATABASE', {
        oldValue: state.selectedDatabase,
        newValue: action.payload,
        willClearMetadata: action.payload !== state.selectedDatabase
      });
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
          db.id === action.payload.id ? action.payload : db
        ),
      };
    case 'REMOVE_DATABASE':
      return {
        ...state,
        databases: state.databases.filter(db => db.id !== action.payload),
        // Clear selection if removed database was selected
        selectedDatabase: state.selectedDatabase === action.payload ? null : state.selectedDatabase,
        metadata: state.selectedDatabase === action.payload ? null : state.metadata,
      };
    case 'START_DATABASE_SWITCH':
      return {
        ...state,
        switchingDatabase: true,
      };
    case 'COMPLETE_DATABASE_SWITCH':
      return {
        ...state,
        switchingDatabase: false,
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
    refreshDatabaseMetadata: (databaseName: string) => Promise<void>;
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

  const loadMetadata = async (databaseId: string) => {
    console.log('Loading metadata for database id:', databaseId);
    dispatch({ type: 'SET_LOADING', payload: { key: 'metadata', value: true } });
    
    try {
      const metadata = await apiClient.getDatabaseMetadata(databaseId);
      console.log('Metadata loaded successfully:', metadata);
      
      // Only update the global metadata state if the database being loaded is the currently selected one
      if (databaseId === state.selectedDatabase) {
        dispatch({ type: 'SET_METADATA', payload: metadata });
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to load database metadata';
      console.error('Failed to load metadata:', error);
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      message.error(errorMessage);
      
      // Only clear the global metadata state if the database being loaded is the currently selected one
      if (databaseId === state.selectedDatabase) {
        dispatch({ type: 'SET_METADATA', payload: null });
      }
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'metadata', value: false } });
    }
  };

  const selectDatabase = async (databaseId: string | null) => {
    console.log('=== selectDatabase called ===');
    console.log('New database id:', databaseId);
    console.log('Current database id:', state.selectedDatabase);
    console.log('Are they equal?', databaseId === state.selectedDatabase);
    
    // Don't do anything if selecting the same database
    if (databaseId === state.selectedDatabase) {
      console.log('Database already selected, skipping');
      return;
    }
    
    console.log('Dispatching START_DATABASE_SWITCH');
    dispatch({ type: 'START_DATABASE_SWITCH' });
    
    console.log('Dispatching SET_SELECTED_DATABASE with:', databaseId);
    dispatch({ type: 'SET_SELECTED_DATABASE', payload: databaseId });
    
    // Wait for metadata to load (handled by useEffect)
    // We'll complete the switch after a short delay to ensure useEffect has triggered
    setTimeout(() => {
      console.log('Dispatching COMPLETE_DATABASE_SWITCH');
      dispatch({ type: 'COMPLETE_DATABASE_SWITCH' });
      if (databaseId) {
        const database = state.databases.find(db => db.id === databaseId);
        message.success(`Switched to database: ${database?.name || databaseId}`);
      }
    }, 100);
  };

  const addDatabase = (database: DatabaseConnection) => {
    dispatch({ type: 'ADD_DATABASE', payload: database });
  };

  const updateDatabase = (database: DatabaseConnection) => {
    dispatch({ type: 'UPDATE_DATABASE', payload: database });
  };

  const removeDatabase = (databaseId: string) => {
    dispatch({ type: 'REMOVE_DATABASE', payload: databaseId });
  };

  const refreshMetadata = async () => {
    if (state.selectedDatabase) {
      await loadMetadata(state.selectedDatabase);
    }
  };

  const refreshDatabaseMetadata = async (databaseId: string) => {
    console.log('Refreshing metadata for database id:', databaseId);
    dispatch({ type: 'SET_LOADING', payload: { key: 'metadata', value: true } });
    
    try {
      // Call the refresh endpoint to update metadata on the server and get the latest
      const metadata = await apiClient.refreshDatabaseMetadata(databaseId);
      console.log('Metadata refreshed successfully:', metadata);
      
      // Only update the global metadata state if the database being loaded is the currently selected one
      if (databaseId === state.selectedDatabase) {
        dispatch({ type: 'SET_METADATA', payload: metadata });
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to refresh database metadata';
      console.error('Failed to refresh metadata:', error);
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      message.error(errorMessage);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'metadata', value: false } });
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
      refreshDatabaseMetadata,
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