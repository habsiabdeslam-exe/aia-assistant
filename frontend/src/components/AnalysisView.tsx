import { CheckCircle, AlertTriangle, FileCheck, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface AnalysisViewProps {
  analysis: string;
  status: string;
  hasGaps: boolean;
  onGenerateTAD: () => Promise<void>;
  loading: boolean;
}

export default function AnalysisView({
  analysis,
  status,
  hasGaps,
  onGenerateTAD,
  loading,
}: AnalysisViewProps) {
  const isReady = status === 'READY' && !hasGaps;

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center gap-3 mb-6">
        <FileCheck className="w-8 h-8 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-800">
          Requirements Analysis
        </h2>
      </div>

      {/* Status Banner */}
      <div
        className={`mb-6 p-6 rounded-lg border-2 ${
          isReady
            ? 'bg-green-50 border-green-200'
            : 'bg-orange-50 border-orange-200'
        }`}
      >
        <div className="flex items-center gap-3 mb-2">
          {isReady ? (
            <CheckCircle className="w-8 h-8 text-green-600" />
          ) : (
            <AlertTriangle className="w-8 h-8 text-orange-600" />
          )}
          <h3 className="text-xl font-bold text-gray-800">
            Status: {status}
          </h3>
        </div>
        <p
          className={`text-sm ${
            isReady ? 'text-green-700' : 'text-orange-700'
          }`}
        >
          {isReady
            ? '✓ Requirements are READY for architecture design!'
            : '⚠ Requirements have MUST-HAVE gaps that need to be addressed.'}
        </p>
      </div>

      {/* Analysis Content (Markdown) */}
      <div className="mb-6 p-6 bg-gray-50 border border-gray-200 rounded-lg prose prose-sm max-w-none">
        <ReactMarkdown
          components={{
            table: ({ node, ...props }) => (
              <table className="min-w-full divide-y divide-gray-300 border border-gray-300" {...props} />
            ),
            thead: ({ node, ...props }) => (
              <thead className="bg-gray-100" {...props} />
            ),
            th: ({ node, ...props }) => (
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-900 border border-gray-300" {...props} />
            ),
            td: ({ node, ...props }) => (
              <td className="px-4 py-2 text-sm text-gray-700 border border-gray-300" {...props} />
            ),
            h2: ({ node, ...props }) => (
              <h2 className="text-xl font-bold text-gray-800 mt-6 mb-3" {...props} />
            ),
            h3: ({ node, ...props }) => (
              <h3 className="text-lg font-semibold text-gray-800 mt-4 mb-2" {...props} />
            ),
            p: ({ node, ...props }) => (
              <p className="text-gray-700 mb-3" {...props} />
            ),
            ul: ({ node, ...props }) => (
              <ul className="list-disc list-inside text-gray-700 space-y-1 mb-3" {...props} />
            ),
          }}
        >
          {analysis}
        </ReactMarkdown>
      </div>

      {/* Generate TAD Button (only if READY) */}
      {isReady && (
        <button
          onClick={onGenerateTAD}
          disabled={loading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating TAD...
            </>
          ) : (
            <>
              <FileCheck className="w-5 h-5" />
              Generate Technical Architecture Document
            </>
          )}
        </button>
      )}

      {/* Message if NOT READY */}
      {!isReady && (
        <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
          <p className="text-sm text-orange-800 font-medium">
            Please address the MUST-HAVE gaps listed above before proceeding to TAD generation.
          </p>
        </div>
      )}
    </div>
  );
}
