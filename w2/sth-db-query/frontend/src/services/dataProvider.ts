/**
 * Custom Data Provider for Database Query Tool
 *
 * Handles the specific API patterns for database connections
 */

import { DataProvider } from "@refinedev/core";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add response interceptor for error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 400) {
      throw new Error(error.response.data?.message || "Bad Request");
    }
    if (error.response?.status === 404) {
      throw new Error("Resource not found");
    }
    if (error.response?.status === 500) {
      throw new Error("Internal server error");
    }
    throw new Error(error.message || "Network error");
  }
);

export const dataProvider: DataProvider = {
  getList: async ({ resource, pagination, filters, sorters, meta }) => {
    if (resource === "dbs") {
      console.log("Getting database list...");
      const response = await axiosInstance.get(`/${resource}/`);
      console.log("API Response:", response.data);
      const data = response.data.data || response.data || [];
      console.log("Extracted data:", data);
      return {
        data: data,
        total: data.length || 0,
      };
    }
    throw new Error(`Unsupported resource: ${resource}`);
  },

  getOne: async ({ resource, id }) => {
    if (resource === "dbs") {
      const response = await axiosInstance.get(`/${resource}/${id}`);
      return {
        data: response.data.data,
      };
    }
    throw new Error(`Unsupported resource: ${resource}`);
  },

  create: async ({ resource, variables }) => {
    if (resource === "dbs") {
      // For databases, use PUT /{name} instead of POST
      const response = await axiosInstance.put(`/${resource}/${variables.name}`, variables);
      return {
        data: response.data.data,
      };
    }
    throw new Error(`Unsupported resource: ${resource}`);
  },

  update: async ({ resource, id, variables }) => {
    if (resource === "dbs") {
      // For databases, use PUT /{name} for updates too
      const response = await axiosInstance.put(`/${resource}/${id}`, variables);
      return {
        data: response.data.data,
      };
    }
    throw new Error(`Unsupported resource: ${resource}`);
  },

  deleteOne: async ({ resource, id }) => {
    if (resource === "dbs") {
      const response = await axiosInstance.delete(`/${resource}/${id}`);
      return {
        data: response.data,
      };
    }
    throw new Error(`Unsupported resource: ${resource}`);
  },

  getApiUrl: () => API_BASE_URL,

  // Custom methods can be added here if needed
};
