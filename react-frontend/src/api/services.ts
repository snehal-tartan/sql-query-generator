import apiClient from './client';

export interface DatabaseCredentials {
  host: string;
  user: string;
  password: string;
  database: string;
  port?: number;
}

export interface GenerateSQLRequest {
  query: string;
}

export interface GenerateSQLResponse {
  sql_query?: string;
  error?: string;
}

export const queryService = {
  generateSQL: async (naturalLanguageQuery: string): Promise<GenerateSQLResponse> => {
    const response = await apiClient.post<GenerateSQLResponse>('/generate_sql', {
      query: naturalLanguageQuery,
    });
    return response.data;
  },

  executeSQL: async (sqlQuery: string) => {
    const response = await apiClient.post('/execute_sql', {
      query: sqlQuery,
    });
    return response.data;
  },

  downloadCSV: async (sqlQuery: string) => {
    const response = await apiClient.post('/download_csv', {
      query: sqlQuery,
    }, {
      responseType: 'blob',
    });
    return response.data;
  },

  connectDatabase: async (host: string, user: string, password: string, database: string, port: number) => {
    const response = await apiClient.post('/connect_database', {
      host,
      user,
      password,
      database,
      port,
    });
    return response.data;
  },

  getDatabaseStatus: async () => {
    const response = await apiClient.get('/database_status');
    return response.data;
  },

  generateGraph: async (sqlQuery: string, chartType: string, chartName?: string) => {
    const response = await apiClient.post('/generate_graph', {
      sql_query: sqlQuery,
      chart_type: chartType,
      chart_name: chartName,
    });
    return response.data;
  },
};

