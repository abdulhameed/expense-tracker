import { useState } from 'react';
import { MainLayout, Card, Breadcrumb, Button, Alert } from '@/components';

export function DataImport() {
  const [file, setFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
    }
  };

  const handleImport = async () => {
    if (!file) {
      setResult({ success: false, message: 'Please select a file' });
      return;
    }

    setImporting(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/transactions/import', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setResult({
          success: true,
          message: `Successfully imported ${data.imported_count} transactions`,
        });
        setFile(null);
      } else {
        const error = await response.json();
        setResult({
          success: false,
          message: error.detail || 'Import failed',
        });
      }
    } catch (err) {
      setResult({
        success: false,
        message: err instanceof Error ? err.message : 'Import error occurred',
      });
    } finally {
      setImporting(false);
    }
  };

  const downloadTemplate = () => {
    const headers = ['date', 'title', 'description', 'amount', 'type', 'category', 'payment_method'];
    const csv = [
      headers.join(','),
      '2024-03-01,Grocery Shopping,Weekly groceries,150.00,expense,Food,credit_card',
      '2024-03-05,Salary,Monthly salary,5000.00,income,Salary,bank_transfer',
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transactions-template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Data Import' },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">Data Import</h1>
        <p className="text-neutral-600 mt-2">Import transactions from CSV files</p>
      </div>

      {result && (
        <Alert
          variant={result.success ? 'success' : 'error'}
          closeable
          className="mb-8"
        >
          {result.message}
        </Alert>
      )}

      {/* Template Section */}
      <Card className="mb-8">
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-4">CSV Template</h2>
          <p className="text-neutral-600 mb-4">
            Download a template CSV file with the required format for importing transactions.
          </p>
          <Button
            onClick={downloadTemplate}
            className="bg-secondary-600 hover:bg-secondary-700 text-white"
          >
            📥 Download Template
          </Button>

          <div className="mt-6 pt-6 border-t border-neutral-200">
            <h3 className="font-semibold text-neutral-900 mb-3">Required Columns:</h3>
            <ul className="space-y-2 text-sm text-neutral-600">
              <li>• <span className="font-mono">date</span> - Transaction date (YYYY-MM-DD)</li>
              <li>• <span className="font-mono">title</span> - Transaction title</li>
              <li>• <span className="font-mono">description</span> - Optional description</li>
              <li>• <span className="font-mono">amount</span> - Transaction amount (numeric)</li>
              <li>• <span className="font-mono">type</span> - 'income' or 'expense'</li>
              <li>• <span className="font-mono">category</span> - Category name</li>
              <li>• <span className="font-mono">payment_method</span> - Payment method</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Import Section */}
      <Card>
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Import CSV File</h2>

          <div className="border-2 border-dashed border-neutral-300 rounded-lg p-8 text-center mb-6">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="hidden"
              id="csv-input"
              disabled={importing}
            />
            <label htmlFor="csv-input" className="cursor-pointer">
              <div className="text-4xl mb-2">📁</div>
              <p className="text-neutral-900 font-medium mb-1">
                {file ? file.name : 'Click to select CSV file'}
              </p>
              <p className="text-neutral-600 text-sm">
                {file ? 'Ready to import' : 'or drag and drop a CSV file'}
              </p>
            </label>
          </div>

          <div className="flex gap-3 justify-center">
            {file && (
              <Button
                onClick={() => setFile(null)}
                className="px-6 py-2 text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded-lg"
                disabled={importing}
              >
                Clear
              </Button>
            )}
            <Button
              onClick={handleImport}
              disabled={!file || importing}
              className={`px-6 py-2 rounded-lg text-white ${
                file && !importing
                  ? 'bg-primary-600 hover:bg-primary-700 cursor-pointer'
                  : 'bg-neutral-400 cursor-not-allowed'
              }`}
            >
              {importing ? 'Importing...' : 'Import Transactions'}
            </Button>
          </div>

          <div className="mt-6 pt-6 border-t border-neutral-200">
            <h3 className="font-semibold text-neutral-900 mb-3">Important Notes:</h3>
            <ul className="space-y-2 text-sm text-neutral-600 list-disc list-inside">
              <li>Maximum file size: 10MB</li>
              <li>Duplicate transactions will be detected and skipped</li>
              <li>Invalid rows will be reported but won't block the entire import</li>
              <li>All categories must exist in your account</li>
            </ul>
          </div>
        </div>
      </Card>
    </MainLayout>
  );
}
