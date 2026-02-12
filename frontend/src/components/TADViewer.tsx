import { Download, FileDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface TADViewerProps {
  tadMarkdown: string;
}

export default function TADViewer({ tadMarkdown }: TADViewerProps) {
  const handleDownloadMarkdown = () => {
    const blob = new Blob([tadMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'technical-architecture-document.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadPDF = async () => {
    try {
      const html2pdf = (await import('html2pdf.js')).default;
      const element = document.getElementById('tad-content');
      
      const opt = {
        margin: 1,
        filename: 'technical-architecture-document.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
      };

      html2pdf().set(opt).from(element).save();
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Error generating PDF. Please try downloading as Markdown instead.');
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <FileDown className="w-8 h-8 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-800">
            Technical Architecture Document
          </h2>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleDownloadMarkdown}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            .MD
          </button>
          <button
            onClick={handleDownloadPDF}
            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            .PDF
          </button>
        </div>
      </div>

      <div
        id="tad-content"
        className="prose prose-slate max-w-none p-6 bg-gray-50 rounded-lg border border-gray-200"
      >
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-3xl font-bold text-gray-900 mb-4 pb-2 border-b-2 border-gray-300">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-2xl font-bold text-gray-800 mt-6 mb-3">
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-xl font-semibold text-gray-800 mt-4 mb-2">
                {children}
              </h3>
            ),
            p: ({ children }) => (
              <p className="text-gray-700 mb-3 leading-relaxed">{children}</p>
            ),
            ul: ({ children }) => (
              <ul className="list-disc list-inside mb-3 space-y-1 text-gray-700">
                {children}
              </ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal list-inside mb-3 space-y-1 text-gray-700">
                {children}
              </ol>
            ),
            code: ({ children, className }) => {
              const isInline = !className;
              return isInline ? (
                <code className="bg-gray-200 text-red-600 px-1 py-0.5 rounded text-sm">
                  {children}
                </code>
              ) : (
                <code className="block bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  {children}
                </code>
              );
            },
            blockquote: ({ children }) => (
              <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-4">
                {children}
              </blockquote>
            ),
          }}
        >
          {tadMarkdown}
        </ReactMarkdown>
      </div>
    </div>
  );
}
