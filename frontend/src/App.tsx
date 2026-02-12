import { useState } from 'react';
import InputForm from './components/InputForm';
import AnalysisView from './components/AnalysisView';
import TADViewer from './components/TADViewer';
import { qualifyRequirements, generateTAD } from './services/api';
import { FileText, AlertCircle } from 'lucide-react';

type AppStep = 'input' | 'analysis' | 'tad';

function App() {
  const [step, setStep] = useState<AppStep>('input');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [requirements, setRequirements] = useState<string>('');
  const [analysis, setAnalysis] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [hasGaps, setHasGaps] = useState<boolean>(true);
  const [tadMarkdown, setTadMarkdown] = useState<string>('');

  const handleQualify = async (requirementsInput: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await qualifyRequirements(requirementsInput);
      setRequirements(requirementsInput);
      setAnalysis(response.analysis);
      setStatus(response.status);
      setHasGaps(response.has_gaps);
      setStep('analysis');
    } catch (err) {
      setError(
        err instanceof Error 
          ? err.message 
          : 'Failed to qualify requirements. Please check your connection and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTAD = async () => {
    if (!analysis) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const requirementsData = {
        original_requirements: requirements,
        analysis: analysis,
        status: status,
      };
      
      const response = await generateTAD(requirementsData);
      setTadMarkdown(response.tad_markdown);
      setStep('tad');
    } catch (err) {
      setError(
        err instanceof Error 
          ? err.message 
          : 'Failed to generate TAD. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStep('input');
    setRequirements('');
    setAnalysis('');
    setStatus('');
    setHasGaps(true);
    setTadMarkdown('');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="w-10 h-10 text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  AI Architecture Assistant
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  Generate Technical Architecture Documents with AI
                </p>
              </div>
            </div>
            {step !== 'input' && (
              <button
                onClick={handleReset}
                className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
              >
                Start Over
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-800">Error</h3>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Step 1: Input Form */}
        {step === 'input' && (
          <InputForm onQualify={handleQualify} loading={loading} />
        )}

        {/* Step 2: Analysis View */}
        {step === 'analysis' && analysis && (
          <AnalysisView
            analysis={analysis}
            status={status}
            hasGaps={hasGaps}
            onGenerateTAD={handleGenerateTAD}
            loading={loading}
          />
        )}

        {/* Step 3: TAD Viewer */}
        {step === 'tad' && tadMarkdown && (
          <TADViewer tadMarkdown={tadMarkdown} />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 py-6 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-600">
          <p>
            Powered by Azure OpenAI GPT-4 and Azure AI Search
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
