import { useState } from 'react';
import { Document } from '../types/api';
import { Button } from './Button';
import { Input } from './Input';
import { Spinner } from './Spinner';
import {
  DocumentIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  ChevronUpDownIcon,
} from '@heroicons/react/24/outline';
import { formatDate, formatCurrency } from '../utils/formatters';

interface DocumentListProps {
  documents: Document[];
  isLoading?: boolean;
  onDownload?: (documentId: number) => Promise<void>;
  onPreview?: (documentId: number) => void;
  onDelete?: (documentId: number) => Promise<void>;
  onSearch?: (query: string) => void;
  onSort?: (sortBy: 'date' | 'name' | 'size', order: 'asc' | 'desc') => void;
}

type SortField = 'date' | 'name' | 'size' | null;

const getFileIcon = (fileType: string) => {
  if (fileType.includes('pdf')) return '📄';
  if (fileType.includes('image')) return '🖼️';
  if (fileType.includes('word') || fileType.includes('document')) return '📝';
  if (fileType.includes('sheet') || fileType.includes('excel')) return '📊';
  return '📎';
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

export function DocumentList({
  documents,
  isLoading = false,
  onDownload,
  onPreview,
  onDelete,
  onSearch,
  onSort,
}: DocumentListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<SortField>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    onSearch?.(value);
  };

  const handleSort = (field: SortField) => {
    let newOrder: 'asc' | 'desc' = 'desc';
    if (sortField === field && sortOrder === 'desc') {
      newOrder = 'asc';
    }
    setSortField(field);
    setSortOrder(newOrder);
    if (field) {
      onSort?.(field, newOrder);
    }
  };

  const handleDownload = async (documentId: number) => {
    if (!onDownload) return;
    setDownloadingId(documentId);
    try {
      await onDownload(documentId);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDelete = async (documentId: number) => {
    if (!onDelete) return;
    if (!confirm('Are you sure you want to delete this document?')) return;
    setDeletingId(documentId);
    try {
      await onDelete(documentId);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Search bar */}
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
        <Input
          type="text"
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Search documents by name or tags..."
          className="pl-10"
        />
      </div>

      {/* Documents table */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('name')}
                  className="flex items-center gap-2 font-semibold text-gray-700 hover:text-gray-900"
                >
                  File Name
                  {sortField === 'name' && <ChevronUpDownIcon className="w-4 h-4" />}
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('size')}
                  className="flex items-center gap-2 font-semibold text-gray-700 hover:text-gray-900"
                >
                  Size
                  {sortField === 'size' && <ChevronUpDownIcon className="w-4 h-4" />}
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('date')}
                  className="flex items-center gap-2 font-semibold text-gray-700 hover:text-gray-900"
                >
                  Uploaded
                  {sortField === 'date' && <ChevronUpDownIcon className="w-4 h-4" />}
                </button>
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">Description</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">Tags</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center">
                  <Spinner />
                </td>
              </tr>
            ) : documents.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  <DocumentIcon className="w-12 h-12 mx-auto text-gray-300 mb-2" />
                  <p>No documents found</p>
                  <p className="text-sm">Upload your first document to get started</p>
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id} className="border-b border-gray-200 hover:bg-gray-50 transition">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <span className="text-lg">{getFileIcon(doc.file_type)}</span>
                      <div className="min-w-0">
                        <p className="font-medium text-gray-900 truncate">{doc.file_name}</p>
                        <p className="text-xs text-gray-500">{doc.file_extension.toUpperCase()}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{formatFileSize(doc.file_size)}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{formatDate(doc.created_at)}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    <p className="line-clamp-2">{doc.description || '-'}</p>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {doc.tags && doc.tags.length > 0 ? (
                        doc.tags.map((tag) => (
                          <span
                            key={tag}
                            className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                          >
                            {tag}
                          </span>
                        ))
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-center gap-2">
                      {onPreview && (
                        <button
                          onClick={() => onPreview(doc.id)}
                          className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition"
                          title="Preview"
                        >
                          <EyeIcon className="w-5 h-5" />
                        </button>
                      )}
                      {onDownload && (
                        <button
                          onClick={() => handleDownload(doc.id)}
                          disabled={downloadingId === doc.id}
                          className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded transition disabled:opacity-50"
                          title="Download"
                        >
                          {downloadingId === doc.id ? (
                            <Spinner size="sm" />
                          ) : (
                            <ArrowDownTrayIcon className="w-5 h-5" />
                          )}
                        </button>
                      )}
                      {onDelete && (
                        <button
                          onClick={() => handleDelete(doc.id)}
                          disabled={deletingId === doc.id}
                          className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded transition disabled:opacity-50"
                          title="Delete"
                        >
                          {deletingId === doc.id ? (
                            <Spinner size="sm" />
                          ) : (
                            <TrashIcon className="w-5 h-5" />
                          )}
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      {documents.length > 0 && (
        <div className="text-sm text-gray-600">
          Showing {documents.length} document{documents.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
}
