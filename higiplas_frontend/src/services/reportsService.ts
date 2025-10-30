import { apiService } from './apiService';

export interface StockMovement {
  id: number;
  data: string;
  produto: string;
  codigo_produto: string;
  tipo: 'ENTRADA' | 'SAIDA';
  quantidade: number;
  quantidade_antes: number | null;
  quantidade_depois: number | null;
  usuario: string;
  origem: string | null;
  observacao: string | null;
}

export interface StockReportSummary {
  entradas: number;
  saidas: number;
}

export interface StockReport {
  periodo: string;
  total_movimentacoes: number;
  resumo: StockReportSummary;
  detalhes: StockMovement[];
}

export interface StockReportParams {
  start_date?: string;
  end_date?: string;
  format?: 'json' | 'pdf' | 'xlsx';
}

export interface MonthlyReportParams {
  month?: number;
  year?: number;
  format?: 'json' | 'pdf' | 'xlsx';
}

export const reportsService = {
  async fetchWeeklyStockReport(params?: StockReportParams): Promise<StockReport> {
    const queryParams = new URLSearchParams();

    if (params?.start_date) {
      queryParams.append('start_date', params.start_date);
    }
    if (params?.end_date) {
      queryParams.append('end_date', params.end_date);
    }
    if (params?.format) {
      queryParams.append('format', params.format);
    }

    const endpoint = `/api/v1/reports/stock/weekly${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiService.get(endpoint);
    return response?.data;
  },

  async fetchMonthlyStockReport(params?: MonthlyReportParams): Promise<StockReport> {
    const queryParams = new URLSearchParams();

    if (params?.month) {
      queryParams.append('month', params.month.toString());
    }
    if (params?.year) {
      queryParams.append('year', params.year.toString());
    }
    if (params?.format) {
      queryParams.append('format', params.format);
    }

    const endpoint = `/api/v1/reports/stock/monthly${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiService.get(endpoint);
    return response?.data;
  },

  async fetchCustomStockReport(start_date: string, end_date: string, format: 'json' | 'pdf' | 'xlsx' = 'json'): Promise<StockReport> {
    const queryParams = new URLSearchParams({
      start_date,
      end_date,
      format
    });

    const endpoint = `/api/v1/reports/stock/custom?${queryParams.toString()}`;
    const response = await apiService.get(endpoint);
    return response?.data;
  },

  async downloadWeeklyStockReport(format: 'pdf' | 'xlsx', params?: StockReportParams): Promise<void> {
    const queryParams = new URLSearchParams({ format });

    if (params?.start_date) {
      queryParams.append('start_date', params.start_date);
    }
    if (params?.end_date) {
      queryParams.append('end_date', params.end_date);
    }

    const endpoint = `/api/v1/reports/stock/weekly?${queryParams.toString()}`;
    const response = await apiService.get(endpoint);

    if (response?.data?.content) {
      const byteCharacters = atob(response.data.content);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: response.data.content_type });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = response.data.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }
  },

  formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  },

  getLastWeekDates(): { start_date: string; end_date: string } {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 7);
    
    return {
      start_date: this.formatDate(start),
      end_date: this.formatDate(end)
    };
  },

  getCurrentMonthDates(): { month: number; year: number } {
    const now = new Date();
    return {
      month: now.getMonth() + 1,
      year: now.getFullYear()
    };
  }
};
