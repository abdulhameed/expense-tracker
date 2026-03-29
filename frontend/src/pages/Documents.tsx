import { useState, useEffect } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Breadcrumb } from '@/components/Breadcrumb';
import { DocumentUploadModal } from '@/components/DocumentUploadModal';
import { DocumentList } from '@/components/DocumentList';
import { DocumentPreview } from '@/components/DocumentPreview';
import { Spinner } from '@/components/Spinner';
import { Document, DocumentFilter } from '@/types/api';
import { documentService } from '@/services/documents';
import { showNotification } from '@/utils/notifications';
import { CloudArrowUpIcon, DocumentIcon } from '@heroicons/react/24/outline';

export function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [filter, setFilter] = useState<DocumentFilter>({
    page: 1,
    limit: 20,
    sort_by: 'date',
    sort_order: 'desc',
  });
  const [totalDocuments, setTotalDocuments] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  // Load documents
  useEffect(() => {
    loadDocuments();
  }, [filter]);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await documentService.getDocuments(filter);
      setDocuments(response.items);
      setTotalDocuments(response.total);
    } catch (error) {
      showNotification('error', 'Failed to load documents');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpload = async (file: File, description?: string, tags?: string[]) => {
    try {
      setIsUploading(true);
      await documentService.uploadDocument(file, undefined, description, tags);
      showNotification('success', 'Document uploaded successfully');
      setIsUploadModalOpen(false);
      // Reload documents
      await loadDocuments();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload document';
      showNotification('error', errorMessage);
      throw error;
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = async (documentId: number) => {
    try {
      await documentService.downloadDocument(documentId);
      showNotification('success', 'Document downloaded successfully');
    } catch (error) {
      showNotification('error', 'Failed to download document');
      console.error(error);
    }
  };

  const handlePreview = (documentId: number) => {
    const doc = documents.find((d) => d.id === documentId);
    if (doc) {
      setSelectedDocument(doc);
      setIsPreviewOpen(true);
    }
  };

  const handleDelete = async (documentId: number) => {
    try {
      await documentService.deleteDocument(documentId);
      showNotification('success', 'Document deleted successfully');
      await loadDocuments();
    } catch (error) {
      showNotification('error', 'Failed to delete document');
      console.error(error);
    }
  };

  const handleSearch = (query: string) => {
    setFilter((prev) => ({
      ...prev,
      search: query || undefined,
      page: 1,
    }));
  };

  const handleSort = (sortBy: 'date' | 'name' | 'size', sortOrder: 'asc' | 'desc') => {
    setFilter((prev) => ({
      ...prev,
      sort_by: sortBy,
      sort_order: sortOrder,
      page: 1,
    }));
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <Breadcrumb items={[{ label: 'Documents' }]} />
            <h1 className="text-3xl font-bold text-gray-900 mt-2">Document Management</h1>
            <p className="text-gray-600 mt-2">Upload, organize, and manage your financial documents</p>
          </div>
          <Button
            variant="primary"
            size="lg"
            onClick={() => setIsUploadModalOpen(true)}
            className="flex items-center gap-2"
          >
            <CloudArrowUpIcon className="w-5 h-5" />
            Upload Document
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Documents</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{totalDocuments}</p>
              </div>
              <DocumentIcon className="w-10 h-10 text-blue-100" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Recent Upload</p>
                <p className="text-lg font-semibold text-gray-900 mt-2">
                  {documents.length > 0 ? new Date(documents[0]?.created_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
              <CloudArrowUpIcon className="w-10 h-10 text-green-100" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Storage Used</p>
                <p className="text-lg font-semibold text-gray-900 mt-2">
                  {documents.length > 0
                    ? (
                        documents.reduce((sum, doc) => sum + doc.file_size, 0) /
                        1024 /
                        1024
                      ).toFixed(2) + ' MB'
                    : '0 MB'}
                </p>
              </div>
              <DocumentIcon className="w-10 h-10 text-purple-100" />
            </div>
          </Card>
        </div>

        {/* Documents Table */}
        <Card className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Your Documents</h2>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Spinner />
            </div>
          ) : (
            <DocumentList
              documents={documents}
              isLoading={isLoading}
              onDownload={handleDownload}
              onPreview={handlePreview}
              onDelete={handleDelete}
              onSearch={handleSearch}
              onSort={handleSort}
            />
          )}
        </Card>
      </div>

      {/* Upload Modal */}
      <DocumentUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUpload={handleUpload}
        isLoading={isUploading}
      />

      {/* Preview Modal */}
      <DocumentPreview
        isOpen={isPreviewOpen}
        onClose={() => {
          setIsPreviewOpen(false);
          setSelectedDocument(null);
        }}
        document={selectedDocument}
        onDownload={handleDownload}
      />
    </MainLayout>
  );
}
