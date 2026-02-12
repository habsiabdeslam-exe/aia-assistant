import { useState } from 'react';
import { FileText, Loader2 } from 'lucide-react';

interface InputFormProps {
  onQualify: (requirements: string) => Promise<void>;
  loading: boolean;
}

export default function InputForm({ onQualify, loading }: InputFormProps) {
  const [requirements, setRequirements] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (requirements.trim()) {
      await onQualify(requirements);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center gap-3 mb-6">
        <FileText className="w-8 h-8 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-800">
          Enter Requirements
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="requirements"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Functional & Non-Functional Requirements
          </label>
          <textarea
            id="requirements"
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            placeholder="Enter your project requirements here...&#10;&#10;Example:&#10;- User authentication with OAuth2&#10;- Real-time data synchronization&#10;- Support for 10,000 concurrent users&#10;- 99.9% uptime SLA"
            className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-gray-700"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !requirements.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Analyzing Requirements...
            </>
          ) : (
            <>
              <FileText className="w-5 h-5" />
              Qualify Requirements
            </>
          )}
        </button>
      </form>
    </div>
  );
}
