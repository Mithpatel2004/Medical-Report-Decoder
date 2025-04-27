export default function SummarizedReport({ summary }) {
    if (!summary) return null;
    
    return (
      <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg mt-6 border border-gray-200">
        <h2 className="text-xl font-bold mb-4 text-blue-700">Report Summary</h2>
        <div className="bg-gray-50 p-4 rounded-lg border-l-4 border-green-500">
          <p className="text-gray-800 leading-relaxed">{summary}</p>
        </div>
      </div>
    );
  }