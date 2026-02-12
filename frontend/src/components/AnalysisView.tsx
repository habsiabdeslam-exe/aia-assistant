import { CheckCircle, AlertTriangle, FileCheck, Loader2, Info } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

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

  // Parse sections from analysis
  const sections = parseAnalysisSections(analysis);

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center gap-3">
          <FileCheck className="w-8 h-8 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-800">
            Requirements Analysis
          </h2>
        </div>
      </div>

      {/* Status Banner */}
      <div
        className={`rounded-xl shadow-sm p-6 border-2 ${
          isReady
            ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300'
            : 'bg-gradient-to-r from-orange-50 to-amber-50 border-orange-300'
        }`}
      >
        <div className="flex items-center gap-3 mb-2">
          {isReady ? (
            <CheckCircle className="w-10 h-10 text-green-600" />
          ) : (
            <AlertTriangle className="w-10 h-10 text-orange-600" />
          )}
          <div>
            <h3 className="text-2xl font-bold text-gray-800">
              Status: {status}
            </h3>
            <p
              className={`text-sm mt-1 ${
                isReady ? 'text-green-700' : 'text-orange-700'
              }`}
            >
              {isReady
                ? '✓ Requirements are READY for architecture design!'
                : '⚠ Requirements have MUST-HAVE gaps that need to be addressed.'}
            </p>
          </div>
        </div>
      </div>

      {/* Business Intent Section */}
      {sections.businessIntent && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 mt-8">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Info className="w-5 h-5 text-blue-600" />
            Business Intent and Scope
          </h3>
          <p className="text-gray-700 leading-relaxed">{sections.businessIntent}</p>
        </div>
      )}

      {/* Functional Requirements Table */}
      {sections.frTable && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 mt-8">
          <h3 className="text-lg font-bold text-gray-800 mb-6">Functional Requirements (FR)</h3>
          <div className="overflow-x-auto mb-4">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                table: ({ node, ...props }) => (
                  <table className="min-w-full divide-y divide-gray-300 border-2 border-gray-300 rounded-lg overflow-hidden shadow-sm" {...props} />
                ),
                thead: ({ node, ...props }) => (
                  <thead className="bg-blue-50" {...props} />
                ),
                th: ({ node, ...props }) => (
                  <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider border-r border-gray-300 last:border-r-0" {...props} />
                ),
                tbody: ({ node, ...props }) => (
                  <tbody className="bg-white divide-y divide-gray-200" {...props} />
                ),
                tr: ({ node, ...props }) => (
                  <tr className="hover:bg-gray-50 transition-colors" {...props} />
                ),
                td: ({ node, ...props }) => (
                  <td className="px-6 py-4 text-sm text-gray-700 border-r border-gray-200 last:border-r-0" {...props} />
                ),
              }}
            >
              {sections.frTable}
            </ReactMarkdown>
          </div>
          {sections.frRemarks && sections.frRemarks.length > 0 && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="text-sm font-semibold text-blue-900 mb-2">FR Remarks:</h4>
              <ul className="space-y-1">
                {sections.frRemarks.map((remark, idx) => (
                  <li key={idx} className="text-sm text-blue-800 flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    <span>{remark}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Non-Functional Requirements Table */}
      {sections.nfrTable && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 mt-8">
          <h3 className="text-lg font-bold text-gray-800 mb-6">Non-Functional Requirements (NFR)</h3>
          <div className="overflow-x-auto mb-4">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                table: ({ node, ...props }) => (
                  <table className="min-w-full divide-y divide-gray-300 border-2 border-gray-300 rounded-lg overflow-hidden shadow-sm" {...props} />
                ),
                thead: ({ node, ...props }) => (
                  <thead className="bg-purple-50" {...props} />
                ),
                th: ({ node, ...props }) => (
                  <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider border-r border-gray-300 last:border-r-0" {...props} />
                ),
                tbody: ({ node, ...props }) => (
                  <tbody className="bg-white divide-y divide-gray-200" {...props} />
                ),
                tr: ({ node, ...props }) => (
                  <tr className="hover:bg-gray-50 transition-colors" {...props} />
                ),
                td: ({ node, ...props }) => (
                  <td className="px-6 py-4 text-sm text-gray-700 border-r border-gray-200 last:border-r-0" {...props} />
                ),
              }}
            >
              {sections.nfrTable}
            </ReactMarkdown>
          </div>
          {sections.nfrRemarks && sections.nfrRemarks.length > 0 && (
            <div className="mt-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
              <h4 className="text-sm font-semibold text-purple-900 mb-2">NFR Remarks:</h4>
              <ul className="space-y-1">
                {sections.nfrRemarks.map((remark, idx) => (
                  <li key={idx} className="text-sm text-purple-800 flex items-start gap-2">
                    <span className="text-purple-600 mt-1">•</span>
                    <span>{remark}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Architecture Gaps */}
      {sections.gaps && (
        <div className={`rounded-xl shadow-sm p-6 border-2 mt-8 ${
          isReady ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300'
        }`}>
          <h3 className="text-lg font-bold text-gray-800 mb-6">Architecture Gap Analysis</h3>
          {isReady ? (
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle className="w-5 h-5" />
              <span className="font-semibold">MUST-HAVE gaps: 0 (READY for design)</span>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  table: ({ node, ...props }) => (
                    <table className="min-w-full divide-y divide-gray-300 border-2 border-red-300 rounded-lg overflow-hidden shadow-sm" {...props} />
                  ),
                  thead: ({ node, ...props }) => (
                    <thead className="bg-red-100" {...props} />
                  ),
                  th: ({ node, ...props }) => (
                    <th className="px-6 py-3 text-left text-xs font-bold text-red-900 uppercase tracking-wider border-r border-red-300 last:border-r-0" {...props} />
                  ),
                  tbody: ({ node, ...props }) => (
                    <tbody className="bg-white divide-y divide-gray-200" {...props} />
                  ),
                  tr: ({ node, ...props }) => (
                    <tr className="hover:bg-red-50 transition-colors" {...props} />
                  ),
                  td: ({ node, ...props }) => (
                    <td className="px-6 py-4 text-sm text-gray-700 border-r border-red-200 last:border-r-0" {...props} />
                  ),
                }}
              >
                {sections.gaps}
              </ReactMarkdown>
            </div>
          )}
        </div>
      )}

      {/* Generate TAD Button (only if READY) */}
      {isReady && (
        <button
          onClick={onGenerateTAD}
          disabled={loading}
          className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-xl shadow-lg transition-all duration-200 flex items-center justify-center gap-3 text-lg"
        >
          {loading ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              Generating TAD...
            </>
          ) : (
            <>
              <FileCheck className="w-6 h-6" />
              Generate Technical Architecture Document
            </>
          )}
        </button>
      )}

      {/* Message if NOT READY */}
      {!isReady && (
        <div className="p-6 bg-gradient-to-r from-orange-50 to-amber-50 border-2 border-orange-300 rounded-xl shadow-sm">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold text-orange-900 mb-1">Action Required</h4>
              <p className="text-sm text-orange-800">
                Please address the MUST-HAVE gaps listed above before proceeding to TAD generation.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper function to parse analysis sections
function parseAnalysisSections(analysis: string) {
  const sections: {
    businessIntent?: string;
    frTable?: string;
    frRemarks?: string[];
    nfrTable?: string;
    nfrRemarks?: string[];
    gaps?: string;
  } = {};

  // Extract Business Intent
  const businessMatch = analysis.match(/1\)\s*Business Intent and Scope[^\n]*\n([\s\S]*?)(?=2\)|$)/i);
  if (businessMatch) {
    sections.businessIntent = businessMatch[1].trim();
  }

  // Extract FR Table
  const frMatch = analysis.match(/2\)\s*Functional Requirements[^\n]*\n([\s\S]*?)(?=FR Remarks:|3\)|$)/i);
  if (frMatch) {
    sections.frTable = frMatch[1].trim();
  }

  // Extract FR Remarks
  const frRemarksMatch = analysis.match(/FR Remarks:\s*\n([\s\S]*?)(?=3\)|$)/i);
  if (frRemarksMatch) {
    sections.frRemarks = frRemarksMatch[1]
      .split('\n')
      .map(line => line.replace(/^[-•*]\s*/, '').trim())
      .filter(line => line.length > 0);
  }

  // Extract NFR Table
  const nfrMatch = analysis.match(/3\)\s*Non-Functional Requirements[^\n]*\n([\s\S]*?)(?=NFR Remarks:|4\)|$)/i);
  if (nfrMatch) {
    sections.nfrTable = nfrMatch[1].trim();
  }

  // Extract NFR Remarks
  const nfrRemarksMatch = analysis.match(/NFR Remarks:\s*\n([\s\S]*?)(?=4\)|$)/i);
  if (nfrRemarksMatch) {
    sections.nfrRemarks = nfrRemarksMatch[1]
      .split('\n')
      .map(line => line.replace(/^[-•*]\s*/, '').trim())
      .filter(line => line.length > 0);
  }

  // Extract Gaps
  const gapsMatch = analysis.match(/4\)\s*Architecture Gap List[^\n]*\n([\s\S]*?)(?=5\)|$)/i);
  if (gapsMatch) {
    sections.gaps = gapsMatch[1].trim();
  }

  return sections;
}
