import { useEffect, useState } from 'react';
import { useTransactionStore } from '@/store/transactionStore';
import { MainLayout, Card, Breadcrumb, Spinner, Alert, Button, Select, Modal } from '@/components';
import { formatCurrency } from '@/utils/formatters';
import { ExportResponse } from '@/types/api';

export function Export() {
  const {
    exports,
    fetchExportHistory,
    exportData,
    deleteExport,
    isLoading,
    error,
  } = useTransactionStore();

  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'csv' | 'xlsx'>('pdf');
  const [selectedDataType, setSelectedDataType] = useState<'transactions' | 'report' | 'analytics'>('transactions');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [exporting, setExporting] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    isOpen: boolean;
    fileUrl?: string;
  }>({ isOpen: false });

  useEffect(() => {
    fetchExportHistory();
  }, [fetchExportHistory]);

  const handleExport = async () => {
    setExporting(true);
    try {
      await exportData(selectedFormat, selectedDataType);
      await fetchExportHistory();
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setExporting(false);
    }
  };

  const handleDownload = (fileUrl: string) => {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = fileUrl.split('/').pop() || 'export';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmation.fileUrl) return;

    try {
      await deleteExport(deleteConfirmation.fileUrl);
      await fetchExportHistory();
      setDeleteConfirmation({ isOpen: false });
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const getFileIcon = (format: string) => {
    switch (format.toLowerCase()) {
      case 'pdf':
        return '📄';
      case 'csv':
        return '📊';
      case 'xlsx':
        return '📈';
      default:
        return '📁';
    }
  };

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Export Data' },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">Export Data</h1>
        <p className="text-neutral-600 mt-2">Download your financial data in multiple formats</p>
      </div>

      {error && (
        <Alert variant="error" closeable className="mb-8">
          {error}
        </Alert>
      )}

      {/* Export Controls */}
      <Card className="mb-8">
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Create New Export</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Format Selection */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Export Format
              </label>
              <div className="flex gap-3">
                {(['pdf', 'csv', 'xlsx'] as const).map((format) => (
                  <button
                    key={format}
                    onClick={() => setSelectedFormat(format)}
                    className={`flex-1 py-2 px-4 rounded-lg border-2 transition-all ${
                      selectedFormat === format
                        ? 'border-primary-500 bg-primary-50 text-primary-900 font-bold'
                        : 'border-neutral-300 text-neutral-600 hover:border-primary-300'
                    }`}
                  >
                    {format.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {/* Data Type Selection */}
            <div>
              <Select
                label="Data Type"
                value={selectedDataType}
                onChange={(e) => setSelectedDataType(e.target.value as any)}
                options={[
                  { value: 'transactions', label: 'All Transactions' },
                  { value: 'report', label: 'Financial Report' },
                  { value: 'analytics', label: 'Analytics Summary' },
                ]}
              />
            </div>
          </div>

          {/* Date Range Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Start Date (Optional)
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                End Date (Optional)
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Format Info */}
          <div className="p-3 bg-neutral-50 rounded-lg mb-6 text-sm text-neutral-600">
            {selectedFormat === 'pdf' && (
              '📄 PDF: Formatted document perfect for printing and sharing. Great for reports.'
            )}
            {selectedFormat === 'csv' && (
              '📊 CSV: Comma-separated values, compatible with Excel and other spreadsheet applications.'
            )}
            {selectedFormat === 'xlsx' && (
              '📈 XLSX: Excel format with full formatting, charts, and advanced features.'
            )}
          </div>

          {/* Export Button */}
          <Button
            onClick={handleExport}
            disabled={exporting}
            className="w-full bg-primary-600 text-white hover:bg-primary-700 disabled:bg-neutral-400"
          >
            {exporting ? (
              <>
                <Spinner size="small" color="text-white" />
                <span className="ml-2">Exporting...</span>
              </>
            ) : (
              '⬇️ Export Now'
            )}
          </Button>
        </div>
      </Card>

      {/* Export History */}
      <Card>
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Export History</h2>

          {exports.length === 0 ? (
            <div className="py-12 text-center text-neutral-600">
              <p>No exports yet. Create your first export above!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {exports.map((exp) => (
                <div
                  key={exp.file_name}
                  className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <span className="text-2xl">{getFileIcon(exp.format)}</span>
                    <div className="flex-1">
                      <p className="font-medium text-neutral-900">{exp.file_name}</p>
                      <p className="text-sm text-neutral-500">
                        {exp.format.toUpperCase()} • Created{' '}
                        {new Date(exp.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleDownload(exp.file_url)}
                      className="px-4 py-2 bg-primary-600 text-white hover:bg-primary-700 text-sm"
                    >
                      Download
                    </Button>
                    <Button
                      onClick={() => setDeleteConfirmation({ isOpen: true, fileUrl: exp.file_url })}
                      className="px-4 py-2 bg-error-100 text-error-600 hover:bg-error-200 text-sm"
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* Delete Export Confirmation Modal */}
      <Modal
        isOpen={deleteConfirmation.isOpen}
        onClose={() => setDeleteConfirmation({ isOpen: false })}
        title="Delete Export"
        size="small"
      >
        <div className="space-y-4">
          <p className="text-neutral-700">
            Are you sure you want to delete this export? This action cannot be undone.
          </p>
          <div className="flex justify-end gap-3">
            <Button
              onClick={() => setDeleteConfirmation({ isOpen: false })}
              className="px-4 py-2 text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded-lg"
            >
              Cancel
            </Button>
            <Button
              onClick={handleDeleteConfirm}
              className="px-4 py-2 bg-error-600 text-white hover:bg-error-700 rounded-lg"
            >
              Delete
            </Button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}
