import { Refine } from "@refinedev/core";
import { RefineKbar, RefineKbarProvider } from "@refinedev/kbar";
import { useNotificationProvider } from "@refinedev/antd";
import { BrowserRouter, Route, Routes, Outlet } from "react-router-dom";

import routerBindings, {
  NavigateToResource,
  UnsavedChangesNotifier,
} from "@refinedev/react-router-v6";
import dataProvider from "@refinedev/simple-rest";
import { ColorModeContextProvider } from "./contexts/color-mode";

import {
  ErrorComponent,
  ThemedLayoutV2,
  ThemedSiderV2,
  ThemedTitleV2,
} from "@refinedev/antd";
import { App as AntdApp } from "antd";

import "@refinedev/antd/dist/reset.css";

import { DatabaseListPage } from "./pages/databases";
import { QueryPage } from "./pages/Query";

function App() {
  return (
    <BrowserRouter>
      <RefineKbarProvider>
        <ColorModeContextProvider>
          <AntdApp>
            <Refine
              dataProvider={dataProvider("http://localhost:8000/api/v1")}
              notificationProvider={useNotificationProvider}
              routerProvider={routerBindings}
              resources={[
                {
                  name: "databases",
                  list: "/databases",
                  meta: {
                    label: "Databases",
                    icon: "🏗️",
                  },
                },
                {
                  name: "query",
                  list: "/query",
                  meta: {
                    label: "Query",
                    icon: "🔍",
                  },
                },
              ]}
              options={{
                syncWithLocation: true,
                warnWhenUnsavedChanges: true,
                useNewQueryKeys: true,
              }}
            >
              <Routes>
                <Route
                  element={
                    <ThemedLayoutV2
                      Sider={ThemedSiderV2}
                      Title={ThemedTitleV2}
                    >
                      <Outlet />
                    </ThemedLayoutV2>
                  }
                >
                  <Route
                    index
                    element={<NavigateToResource resource="databases" />}
                  />
                  <Route path="/databases" element={<DatabaseListPage />} />
                  <Route path="/query" element={<QueryPage />} />
                  <Route path="*" element={<ErrorComponent />} />
                </Route>
              </Routes>
              <RefineKbar />
              <UnsavedChangesNotifier />
            </Refine>
          </AntdApp>
        </ColorModeContextProvider>
      </RefineKbarProvider>
    </BrowserRouter>
  );
}

export default App;
