import { CheckCircle, AlertTriangle, FileCheck, Loader2 } from 'lucide-react';
import type { Qualification } from '../types';

interface QualificationViewProps {
  qualification: Qualification;
  gap: number;
  onGenerateTAD: () => Promise<void>;
  loading: boolean;
}

export default function QualificationView({
  qualification,
  gap,
  onGenerateTAD,
  loading,
}: QualificationViewProps) {
  const isValid = gap === 0;

  const getCategoryColor = (score: number) => {
    if (score === 0) return 'text-green-600';
    if (score < 30) return 'text-yellow-600';
    if (score < 70) return 'text-orange-600';
    return 'text-red-600';
  };

  const getCategoryBgColor = (score: number) => {
    if (score === 0) return 'bg-green-50 border-green-200';
    if (score < 30) return 'bg-yellow-50 border-yellow-200';
    if (score < 70) return 'bg-orange-50 border-orange-200';
    return 'bg-red-50 border-red-200';
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center gap-3 mb-6">
        <FileCheck className="w-8 h-8 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-800">
          Qualification Results
        </h2>
      </div>

      {/* GAB Score */}
      <div
        className={`mb-6 p-6 rounded-lg border-2 ${
          isValid
            ? 'bg-green-50 border-green-200'
            : 'bg-orange-50 border-orange-200'
        }`}
      >
        <div className="flex items-center gap-3 mb-2">
          {isValid ? (
            <CheckCircle className="w-8 h-8 text-green-600" />
          ) : (
            <AlertTriangle className="w-8 h-8 text-orange-600" />
          )}
          <h3 className="text-xl font-bold text-gray-800">
            Gap Analysis Score (GAB): {gap}
          </h3>
        </div>
        <p
          className={`text-sm ${
            isValid ? 'text-green-700' : 'text-orange-700'
          }`}
        >
          {isValid
            ? '✓ Requirements are complete and ready for TAD generation!'
            : '⚠ Requirements need improvement before generating TAD.'}
        </p>
      </div>

      {/* Qualification Categories */}
      <div className="space-y-4 mb-6">
        <h3 className="text-lg font-semibold text-gray-800">
          Detailed Analysis
        </h3>

        {/* Completeness */}
        <div
          className={`p-4 rounded-lg border ${getCategoryBgColor(
            qualification.completeness.score
          )}`}
        >
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-semibold text-gray-800">Completeness</h4>
            <span
              className={`font-bold ${getCategoryColor(
                qualification.completeness.score
              )}`}
            >
              {qualification.completeness.score}/100
            </span>
          </div>
          {qualification.completeness.issues.length > 0 && (
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              {qualification.completeness.issues.map((issue, idx) => (
                <li key={idx}>{issue}</li>
              ))}
            </ul>
          )}
        </div>

        {/* Clarity */}
        <div
          className={`p-4 rounded-lg border ${getCategoryBgColor(
            qualification.clarity.score
          )}`}
        >
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-semibold text-gray-800">Clarity</h4>
            <span
              className={`font-bold ${getCategoryColor(
                qualification.clarity.score
              )}`}
            >
              {qualification.clarity.score}/100
            </span>
          </div>
          {qualification.clarity.issues.length > 0 && (
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              {qualification.clarity.issues.map((issue, idx) => (
                <li key={idx}>{issue}</li>
              ))}
            </ul>
          )}
        </div>

        {/* Feasibility */}
        <div
          className={`p-4 rounded-lg border ${getCategoryBgColor(
            qualification.feasibility.score
          )}`}
        >
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-semibold text-gray-800">Feasibility</h4>
            <span
              className={`font-bold ${getCategoryColor(
                qualification.feasibility.score
              )}`}
            >
              {qualification.feasibility.score}/100
            </span>
          </div>
          {qualification.feasibility.issues.length > 0 && (
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              {qualification.feasibility.issues.map((issue, idx) => (
                <li key={idx}>{issue}</li>
              ))}
            </ul>
          )}
        </div>

        {/* Consistency */}
        <div
          className={`p-4 rounded-lg border ${getCategoryBgColor(
            qualification.consistency.score
          )}`}
        >
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-semibold text-gray-800">Consistency</h4>
            <span
              className={`font-bold ${getCategoryColor(
                qualification.consistency.score
              )}`}
            >
              {qualification.consistency.score}/100
            </span>
          </div>
          {qualification.consistency.issues.length > 0 && (
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              {qualification.consistency.issues.map((issue, idx) => (
                <li key={idx}>{issue}</li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Recommendations */}
      {qualification.recommendations.length > 0 && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-2">Recommendations</h4>
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
            {qualification.recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Generate TAD Button */}
      {isValid && (
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
    </div>
  );
}
