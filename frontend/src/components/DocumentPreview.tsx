import { useState, useEffect } from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import { Spinner } from './Spinner';
import { Document } from '../types/api';
import { XMarkIcon, ArrowDownTrayIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { formatDate } from '../utils/formatters';

interface DocumentPreviewProps {
  isOpen: boolean;
  onClose: () => void;
  document: Document | null;
  onDownload?: (documentId: number) => Promise<void>;
}

export function DocumentPreview({ isOpen, onClose, document, onDownload }: DocumentPreviewProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [pdfPageNum, setPdfPageNum] = useState(1);
  const [pdfPages, setPdfPages] = useState(0);

  useEffect(() => {
    if (!document) return;

    setIsLoading(true);
    setError('');
    setPreviewUrl('');

    // For now, we'll use the file_path as the preview URL
    // In a real application, you'd have an API endpoint that returns the file content
    if (document.file_type.includes('image')) {
      setPreviewUrl(document.file_path);
      setIsLoading(false);
    } else if (document.file_type.includes('pdf')) {
      // For PDF, we could embed it or show a preview placeholder
      setPreviewUrl(document.file_path);
      setIsLoading(false);
    } else {
      setError(
        'Preview not available for this file type. Please download the file to view it.'
      );
      setIsLoading(false);
    }
  }, [document]);

  const handleDownload = async () => {
    if (!document || !onDownload) return;
    await onDownload(document.id);
  };

  if (!document) return null;

  const isImage = document.file_type.includes('image');
  const isPdf = document.file_type.includes('pdf');
  const canPreview = isImage || isPdf;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Document Preview"
      size="large"
      closeButton={true}
    >
      <div className="space-y-4">
        {/* Document info header */}
        <div className="flex items-start justify-between pb-4 border-b border-gray-200">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900">{document.file_name}</h3>
            <p className="text-sm text-gray-600 mt-1">
              Uploaded {formatDate(document.created_at)} by {document.uploaded_by}
            </p>
            {document.description && (
              <p className="text-sm text-gray-700 mt-2">{document.description}</p>
            )}
          </div>
          {onDownload && (
            <Button
              variant="secondary"
              size="sm"
              onClick={handleDownload}
              className="flex items-center gap-2 ml-4"
            >
              <ArrowDownTrayIcon className="w-4 h-4" />
              Download
            </Button>
          )}
        </div>

        {/* Preview area */}
        <div className="bg-gray-100 rounded-lg overflow-auto" style={{ minHeight: '400px', maxHeight: '600px' }}>
          {isLoading ? (
            <div className="flex items-center justify-center h-96">
              <Spinner />
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <p className="text-gray-600 mb-4">{error}</p>
                <Button variant="primary" onClick={handleDownload} size="sm">
                  Download File
                </Button>
              </div>
            </div>
          ) : isImage ? (
            <div className="flex items-center justify-center p-4">
              <img
                src={previewUrl}
                alt={document.file_name}
                className="max-w-full max-h-96 object-contain"
                onError={() => setError('Failed to load image preview')}
              />
            </div>
          ) : isPdf ? (
            <div className="flex flex-col items-center justify-center h-96 space-y-4">
              <div className="text-center">
                <p className="text-gray-600 mb-4">PDF Preview</p>
                <p className="text-sm text-gray-500 mb-6">
                  Full PDF preview in browser coming soon. Use download to view.
                </p>
                <Button variant="primary" onClick={handleDownload} size="sm">
                  Download PDF
                </Button>
              </div>
            </div>
          ) : null}
        </div>

        {/* Tags section */}
        {document.tags && document.tags.length > 0 && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Tags</p>
            <div className="flex flex-wrap gap-2">
              {document.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-block bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Document metadata */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
          <div>
            <p className="text-xs text-gray-600 uppercase font-semibold">File Type</p>
            <p className="text-sm text-gray-900 mt-1">{document.file_extension.toUpperCase()}</p>
          </div>
          <div>
            <p className="text-xs text-gray-600 uppercase font-semibold">File Size</p>
            <p className="text-sm text-gray-900 mt-1">
              {(document.file_size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600 uppercase font-semibold">Uploaded</p>
            <p className="text-sm text-gray-900 mt-1">{formatDate(document.created_at)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-600 uppercase font-semibold">Visibility</p>
            <p className="text-sm text-gray-900 mt-1">{document.is_public ? 'Public' : 'Private'}</p>
          </div>
        </div>
      </div>

      {/* Footer with close button */}
      <div className="mt-6 flex justify-end">
        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
      </div>
    </Modal>
  );
}
