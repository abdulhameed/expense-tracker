import { useState, useRef } from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import { Input } from './Input';
import { Spinner } from './Spinner';
import { CloudArrowUpIcon } from '@heroicons/react/24/outline';

interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (file: File, description?: string, tags?: string[]) => Promise<void>;
  transactionId?: number;
  isLoading?: boolean;
}

const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/png',
  'image/gif',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

export function DocumentUploadModal({
  isOpen,
  onClose,
  onUpload,
  transactionId,
  isLoading = false,
}: DocumentUploadModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    setError('');

    // Validate file type
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      setError('File type not supported. Please upload PDF, images, or documents.');
      return;
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      setError(`File size exceeds 10 MB limit. Your file is ${(file.size / 1024 / 1024).toFixed(2)} MB.`);
      return;
    }

    setSelectedFile(file);
  };

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    const tagList = tags
      .split(',')
      .map((tag) => tag.trim())
      .filter((tag) => tag.length > 0);

    try {
      await onUpload(selectedFile, description || undefined, tagList.length > 0 ? tagList : undefined);
      // Reset form
      setSelectedFile(null);
      setDescription('');
      setTags('');
      setError('');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload document');
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setDescription('');
    setTags('');
    setError('');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Upload Document" size="medium">
      <div className="space-y-4">
        {/* Drag and drop area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'
          } ${selectedFile ? 'border-green-500 bg-green-50' : ''}`}
        >
          {selectedFile ? (
            <div className="space-y-2">
              <div className="text-2xl">✓</div>
              <p className="font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-sm text-gray-600">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Choose different file
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <CloudArrowUpIcon className="w-10 h-10 mx-auto text-gray-400" />
              <div>
                <p className="font-medium text-gray-900">Drag and drop your file here</p>
                <p className="text-sm text-gray-600 mt-1">or</p>
              </div>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-blue-600 hover:text-blue-700 font-medium text-sm"
              >
                browse files
              </button>
              <p className="text-xs text-gray-500 mt-3">
                Supported: PDF, Images (JPG, PNG, GIF), Word, Excel (Max 10 MB)
              </p>
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleInputChange}
            accept={ALLOWED_FILE_TYPES.join(',')}
            className="hidden"
            disabled={isLoading}
          />
        </div>

        {/* Description field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
          <Input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g., Invoice for office supplies"
            disabled={isLoading}
          />
        </div>

        {/* Tags field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Tags (Optional)</label>
          <Input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="e.g., invoice, important, 2024 (comma-separated)"
            disabled={isLoading}
          />
        </div>

        {/* Error message */}
        {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>}

        {/* Transaction ID display */}
        {transactionId && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
            This document will be attached to transaction ID: {transactionId}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-6 flex justify-end gap-3">
        <Button variant="secondary" onClick={handleClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={!selectedFile || isLoading}
          className="flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <Spinner size="sm" />
              Uploading...
            </>
          ) : (
            'Upload Document'
          )}
        </Button>
      </div>
    </Modal>
  );
}
