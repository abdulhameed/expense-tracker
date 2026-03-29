import apiClient from './api';
import { Document, DocumentListResponse, DocumentFilter, UploadDocumentRequest } from '@/types/api';

/**
 * Document Management API Service
 */
export const documentService = {
  /**
   * Get list of documents with optional filtering and pagination
   */
  async getDocuments(filters?: DocumentFilter): Promise<DocumentListResponse> {
    try {
      const params = new URLSearchParams();

      if (filters) {
        if (filters.transaction_id) params.append('transaction_id', filters.transaction_id.toString());
        if (filters.file_type) params.append('file_type', filters.file_type);
        if (filters.search) params.append('search', filters.search);
        if (filters.start_date) params.append('start_date', filters.start_date);
        if (filters.end_date) params.append('end_date', filters.end_date);
        if (filters.tags && filters.tags.length > 0) {
          params.append('tags', filters.tags.join(','));
        }
        if (filters.page) params.append('page', filters.page.toString());
        if (filters.limit) params.append('limit', filters.limit.toString());
        if (filters.sort_by) params.append('sort_by', filters.sort_by);
        if (filters.sort_order) params.append('sort_order', filters.sort_order);
      }

      const queryString = params.toString();
      const url = `/documents${queryString ? '?' + queryString : ''}`;

      const response = await apiClient.get<DocumentListResponse>(url);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get a specific document by ID
   */
  async getDocument(documentId: number): Promise<Document> {
    try {
      const response = await apiClient.get<Document>(`/documents/${documentId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Upload a new document
   */
  async uploadDocument(
    file: File,
    transactionId?: number,
    description?: string,
    tags?: string[]
  ): Promise<Document> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      if (transactionId) {
        formData.append('transaction_id', transactionId.toString());
      }
      if (description) {
        formData.append('description', description);
      }
      if (tags && tags.length > 0) {
        formData.append('tags', JSON.stringify(tags));
      }

      const response = await apiClient.post<Document>('/documents/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update document metadata
   */
  async updateDocument(
    documentId: number,
    updates: {
      description?: string;
      tags?: string[];
      is_public?: boolean;
    }
  ): Promise<Document> {
    try {
      const response = await apiClient.patch<Document>(`/documents/${documentId}`, updates);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete a document
   */
  async deleteDocument(documentId: number): Promise<void> {
    try {
      await apiClient.delete(`/documents/${documentId}`);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Download a document file
   */
  async downloadDocument(documentId: number): Promise<void> {
    try {
      const response = await apiClient.get(`/documents/${documentId}/download/`, {
        responseType: 'blob',
      });

      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;

      // Get filename from response headers or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'document';

      if (contentDisposition) {
        const matches = contentDisposition.match(/filename="?([^"]*)"?/);
        if (matches && matches[1]) {
          filename = matches[1];
        }
      }

      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get document preview URL
   */
  async getPreviewUrl(documentId: number): Promise<string> {
    try {
      const response = await apiClient.get<{ preview_url: string }>(
        `/documents/${documentId}/preview/`
      );
      return response.data.preview_url;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get documents by transaction ID
   */
  async getDocumentsByTransaction(transactionId: number): Promise<Document[]> {
    try {
      const response = await apiClient.get<Document[]>(
        `/documents/by-transaction/${transactionId}/`
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Bulk delete documents
   */
  async bulkDeleteDocuments(documentIds: number[]): Promise<void> {
    try {
      await apiClient.post('/documents/bulk-delete/', { document_ids: documentIds });
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get document statistics
   */
  async getDocumentStats(): Promise<{
    total_documents: number;
    total_size_bytes: number;
    by_type: Record<string, number>;
  }> {
    try {
      const response = await apiClient.get<{
        total_documents: number;
        total_size_bytes: number;
        by_type: Record<string, number>;
      }>('/documents/stats/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};
