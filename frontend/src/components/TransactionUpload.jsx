import { useState } from 'react';
import { Upload, FileText, Check } from 'lucide-react';

function TransactionUpload({ onTransactionsUploaded }) {
  const [uploading, setUploading] = useState(false);
  const [uploadMethod, setUploadMethod] = useState(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const csvData = e.target.result;
        const transactions = parseCSV(csvData);
        onTransactionsUploaded(transactions);
        setUploadMethod('file');
      } catch (error) {
        console.error('Error parsing CSV:', error);
        alert('Error parsing file. Please check the format.');
      } finally {
        setUploading(false);
      }
    };
    
    reader.readAsText(file);
  };

  const parseCSV = (csvData) => {
    const lines = csvData.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    
    return lines.slice(1).map(line => {
      const values = line.split(',');
      const transaction = {};
      
      headers.forEach((header, index) => {
        const value = values[index]?.trim();
        
        if (header.includes('date')) {
          transaction.date = new Date(value).toISOString();
        } else if (header.includes('amount')) {
          transaction.amount = parseFloat(value);
        } else if (header.includes('type')) {
          transaction.type = value.toLowerCase();
        } else if (header.includes('category')) {
          transaction.category = value;
        } else if (header.includes('description')) {
          transaction.description = value;
        }
      });
      
      // Ensure required fields
      if (!transaction.type) {
        transaction.type = transaction.amount > 0 ? 'credit' : 'debit';
      }
      
      return transaction;
    }).filter(t => t.date && t.amount);
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">Transaction Data</h2>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            Upload your bank statements
          </p>
        </div>
        
        {uploadMethod && (
          <div className="flex items-center space-x-2 text-green-600 dark:text-green-400">
            <Check className="w-5 h-5" />
            <span className="text-sm font-medium">
              File uploaded
            </span>
          </div>
        )}
      </div>

      <div>
        {/* File Upload Button */}
        <label className="group p-6 border-2 border-dashed border-gray-300 dark:border-fintech-border rounded-xl hover:border-primary-500 dark:hover:border-primary-500 transition-all hover:shadow-md cursor-pointer block">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
          />
          <div className="flex flex-col items-center text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center group-hover:scale-110 transition-transform">
              {uploading ? (
                <Upload className="w-6 h-6 text-blue-600 dark:text-blue-400 animate-bounce" />
              ) : (
                <FileText className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              )}
            </div>
            <div>
              <h3 className="font-semibold mb-1">Upload CSV File</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {uploading ? 'Processing...' : 'Click to select file'}
              </p>
            </div>
          </div>
        </label>
      </div>

      <div className="mt-4 p-4 bg-gray-100 dark:bg-fintech-dark rounded-lg">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>CSV Format:</strong> date, amount, type (credit/debit), category, description
        </p>
      </div>
    </div>
  );
}

export default TransactionUpload;
