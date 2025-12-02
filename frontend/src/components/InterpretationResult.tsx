import type { InterpretationResult as InterpretationResultType } from '../types';

interface InterpretationResultProps {
  result: InterpretationResultType | null;
  loading?: boolean;
  error?: string | null;
}

export function InterpretationResult({ result, loading, error }: InterpretationResultProps) {
  if (loading) {
    return (
      <div className="interpretation-result bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-10 w-10 border-4 border-amber-500 border-t-transparent"></div>
          <span className="ml-3 text-gray-600">AI 正在解卦中...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="interpretation-result bg-red-50 rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-red-700 mb-2">解卦失败</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  return (
    <div className="interpretation-result bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-amber-800 mb-4 flex items-center">
        <span className="mr-2">🔮</span>
        AI 解卦
      </h3>

      {result.summary && (
        <div className="mb-4 p-4 bg-gradient-to-r from-amber-100 to-orange-100 rounded-lg">
          <p className="text-sm font-medium text-amber-700 mb-1">核心建议</p>
          <p className="text-gray-800 font-medium">{result.summary}</p>
        </div>
      )}

      <div className="prose prose-amber max-w-none">
        <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
          {result.interpretation}
        </div>
      </div>
    </div>
  );
}
