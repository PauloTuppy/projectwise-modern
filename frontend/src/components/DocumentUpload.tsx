import React, { useState } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';

interface Analysis {
  summary: string;
  extracted_data: string;
  confidence_score: number;
  processing_time: number;
  analyzed_by: string;
}

interface DocumentUploadProps {
  projectId: string;
  onUploadComplete?: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ 
  projectId, 
  onUploadComplete 
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);

  const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    
    if (selectedFile) {
      // Validate file size
      if (selectedFile.size > MAX_FILE_SIZE) {
        setError(`File size (${(selectedFile.size / 1024 / 1024).toFixed(2)}MB) exceeds 500MB limit`);
        return;
      }
      
      // Validate file type
      const fileExt = selectedFile.name.split('.').pop()?.toLowerCase();
      const allowedExts = ['pdf', 'docx', 'dwg'];
      
      if (!allowedExts.includes(fileExt || '')) {
        setError('Only PDF, DOCX, and DWG files are allowed');
        return;
      }
      
      setFile(selectedFile);
      setError(null);
      setAnalysis(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name);

    try {
      // Upload document
      const uploadResponse = await axios.post(
        `/api/v1/projects/${projectId}/documents`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / (progressEvent.total || 1)
            );
            setProgress(percentCompleted);
          }
        }
      );

      const docId = uploadResponse.data.id;
      setDocumentId(docId);

      // Simulate AI analysis (in real implementation, this would be async)
      // Poll for analysis results
      let attempts = 0;
      const maxAttempts = 60; // 5 minutes max
      
      const pollAnalysis = setInterval(async () => {
        attempts++;
        
        try {
          const analysisResponse = await axios.get(
            `/api/v1/documents/${docId}/analysis`
          );
          
          if (analysisResponse.data && analysisResponse.data.summary) {
            setAnalysis(analysisResponse.data);
            setUploading(false);
            clearInterval(pollAnalysis);
            
            if (onUploadComplete) {
              onUploadComplete();
            }
          }
        } catch (err) {
          // Analysis not ready yet, continue polling
          if (attempts >= maxAttempts) {
            clearInterval(pollAnalysis);
            setError('Analysis is taking longer than expected. Please check back later.');
            setUploading(false);
          }
        }
      }, 5000); // Check every 5 seconds

    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 flex items-center">
        <span className="mr-2">📄</span>
        Upload Document with AI Analysis
      </h2>

      {/* File Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">
          Select Document
        </label>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition">
          <input
            type="file"
            accept=".pdf,.docx,.dwg"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
            disabled={uploading}
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer flex flex-col items-center"
          >
            <svg
              className="w-12 h-12 text-gray-400 mb-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <span className="text-sm text-gray-600">
              Click to select or drag and drop
            </span>
            <span className="text-xs text-gray-500 mt-1">
              PDF, DOCX, DWG (max 500MB)
            </span>
          </label>
        </div>

        {file && (
          <div className="mt-3 p-3 bg-gray-50 rounded flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{file.name}</p>
              <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
            </div>
            <button
              onClick={() => setFile(null)}
              className="text-red-500 hover:text-red-700"
              disabled={uploading}
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {/* Upload Button */}
      <Button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="w-full mb-4"
      >
        {uploading ? (
          <>
            <span className="mr-2">⏳</span>
            {progress < 100 ? `Uploading... ${progress}%` : 'Analyzing with AI...'}
          </>
        ) : (
          <>
            <span className="mr-2">🚀</span>
            Upload & Analyze with AI
          </>
        )}
      </Button>

      {/* Progress Bar */}
      {uploading && progress < 100 && (
        <div className="mb-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              style={{ width: `${progress}%` }}
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            ></div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* AI Analysis Results */}
      {analysis && (
        <div className="mt-6 space-y-4 animate-fade-in">
          <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center mb-2">
              <span className="text-2xl mr-2">✅</span>
              <h3 className="text-lg font-bold text-green-800">
                Analysis Complete!
              </h3>
            </div>
            <p className="text-sm text-gray-600">
              Processed by {analysis.analyzed_by} in {analysis.processing_time.toFixed(2)}s
            </p>
          </div>

          {/* Summary */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="font-bold mb-2 flex items-center">
              <span className="mr-2">📝</span>
              AI Summary
            </h4>
            <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
          </div>

          {/* Extracted Data */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="font-bold mb-2 flex items-center">
              <span className="mr-2">🔍</span>
              Extracted Data
            </h4>
            <div className="text-sm text-gray-700 whitespace-pre-wrap">
              {analysis.extracted_data}
            </div>
          </div>

          {/* Confidence Score */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="font-bold mb-2 flex items-center">
              <span className="mr-2">📊</span>
              Confidence Score
            </h4>
            <div className="flex items-center">
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    style={{ width: `${analysis.confidence_score * 100}%` }}
                    className={`h-3 rounded-full ${
                      analysis.confidence_score >= 0.9
                        ? 'bg-green-500'
                        : analysis.confidence_score >= 0.7
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                  ></div>
                </div>
              </div>
              <span className="ml-4 font-bold text-lg">
                {(analysis.confidence_score * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button
              onClick={() => {
                setFile(null);
                setAnalysis(null);
                setDocumentId(null);
              }}
              className="flex-1"
            >
              Upload Another Document
            </Button>
            {documentId && (
              <Button
                onClick={() => window.open(`/documents/${documentId}`, '_blank')}
                className="flex-1 bg-green-500 hover:bg-green-600"
              >
                View Document
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-bold text-blue-900 mb-2">🤖 AI Analysis Features</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Automatic 3-sentence summary generation</li>
          <li>• Key data extraction (dates, numbers, entities)</li>
          <li>• OCR text extraction for searchability</li>
          <li>• Confidence scoring for quality assurance</li>
          <li>• Full audit trail for compliance</li>
        </ul>
      </div>
    </div>
  );
};
