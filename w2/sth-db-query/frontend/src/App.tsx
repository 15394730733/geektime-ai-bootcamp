import { Refine } from "@refinedev/core";
import { RefineKbar, RefineKbarProvider } from "@refinedev/kbar";
import { useNotificationProvider } from "@refinedev/antd";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import routerBindings, {
  UnsavedChangesNotifier,
} from "@refinedev/react-router-v6";
import { dataProvider } from "./services/dataProvider";
import { ColorModeContextProvider } from "./contexts/color-mode";

import {
  ErrorComponent,
} from "@refinedev/antd";
import { App as AntdApp } from "antd";

import "@refinedev/antd/dist/reset.css";

import { DatabaseListPage } from "./pages/databases";
import { QueryPage } from "./pages/Query";
import { AppStateProvider } from "./contexts/AppStateContext";

function App() {
  return (
    <BrowserRouter>
      <RefineKbarProvider>
        <ColorModeContextProvider>
          <AppStateProvider>
            <AntdApp>
              <Refine
                dataProvider={dataProvider}
                notificationProvider={useNotificationProvider}
                routerProvider={routerBindings}
                resources={[
                  {
                    name: "databases",
                    list: "/databases",
                  },
                  {
                    name: "query",
                    list: "/query",
                  },
                ]}
                options={{
                  syncWithLocation: true,
                  warnWhenUnsavedChanges: true,
                  useNewQueryKeys: true,
                }}
              >
                <Routes>
                  <Route index element={<DatabaseListPage />} />
                  <Route path="/databases" element={<DatabaseListPage />} />
                  <Route path="/query" element={<QueryPage />} />
                  <Route path="*" element={<ErrorComponent />} />
                </Routes>
                <RefineKbar />
                <UnsavedChangesNotifier />
              </Refine>
            </AntdApp>
          </AppStateProvider>
        </ColorModeContextProvider>
      </RefineKbarProvider>
    </BrowserRouter>
  );
}

export default App;
