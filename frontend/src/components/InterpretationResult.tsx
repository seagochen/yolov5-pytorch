import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { InterpretationResult as InterpretationResultType } from '../types';

interface InterpretationResultProps {
  result: InterpretationResultType | null;
  loading?: boolean;
  error?: string | null;
}

export function InterpretationResult({ result, loading, error }: InterpretationResultProps) {
  if (loading) {
    return (
      <div className="interpretation-result bg-gradient-to-br from-purple-50/80 via-white to-indigo-50/80 rounded-2xl shadow-2xl p-12 border-2 border-purple-200 backdrop-blur-sm">
        <div className="flex flex-col items-center justify-center py-16">
          <div className="relative mb-8">
            {/* 外圈旋转 */}
            <div className="animate-spin rounded-full h-20 w-20 border-4 border-purple-200 border-t-purple-600"></div>
            {/* 内圈反向旋转 */}
            <div className="absolute inset-2 animate-spin-reverse rounded-full h-16 w-16 border-4 border-amber-200 border-b-amber-600"></div>
            {/* 中心太极 */}
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl">☯</span>
            </div>
          </div>
          <span className="text-purple-800 text-xl font-medium mb-2">道长正在观卦...</span>
          <p className="text-purple-600 text-sm tracking-wide">贫道掐指一算，稍候片刻</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="interpretation-result bg-red-50 rounded-2xl shadow-xl p-8 border-2 border-red-300">
        <div className="flex items-start">
          <svg className="w-8 h-8 text-red-600 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <div>
            <h3 className="text-xl font-bold text-red-700 mb-2">解卦失败</h3>
            <p className="text-red-600 text-lg">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  return (
    <div className="interpretation-result bg-gradient-to-br from-purple-50/60 via-white to-indigo-50/60 rounded-2xl shadow-2xl p-8 border-2 border-purple-200 backdrop-blur-sm">
      {result.summary && (
        <div className="mb-8 p-6 bg-gradient-to-r from-amber-100/90 via-orange-100/90 to-yellow-100/90 rounded-xl shadow-lg border-2 border-amber-400 relative overflow-hidden">
          {/* 装饰性图案 */}
          <div className="absolute top-0 right-0 text-6xl text-amber-200/30 -mr-4 -mt-4">✦</div>
          <div className="flex items-start relative z-10">
            <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-amber-600 to-orange-600 rounded-full flex items-center justify-center mr-4 shadow-lg">
              <span className="text-2xl">💡</span>
            </div>
            <div className="flex-1">
              <p className="text-xs font-bold text-amber-900 mb-2 tracking-widest flex items-center gap-2">
                <span>✦</span> 道长锦囊 <span>✦</span>
              </p>
              <div className="text-gray-900 text-lg font-medium leading-relaxed prose prose-amber max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {result.summary}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )}

      <article className="prose prose-base prose-slate max-w-none
        prose-headings:font-serif prose-headings:text-purple-900
        prose-h2:text-2xl prose-h2:font-bold prose-h2:mb-4 prose-h2:mt-8 prose-h2:pb-2 prose-h2:border-b-2 prose-h2:border-purple-200
        prose-h3:text-xl prose-h3:font-semibold prose-h3:mb-3 prose-h3:mt-6 prose-h3:text-amber-800
        prose-strong:text-amber-800 prose-strong:font-bold
        prose-ul:list-none prose-ul:my-3 prose-ul:space-y-2
        prose-ol:list-none prose-ol:my-3 prose-ol:space-y-2
        prose-li:text-gray-800 prose-li:pl-0 prose-li:before:content-['✦'] prose-li:before:text-amber-600 prose-li:before:mr-2
        prose-p:text-gray-800 prose-p:leading-relaxed prose-p:mb-3
        prose-a:text-purple-600 prose-a:underline hover:prose-a:text-purple-800
        prose-code:text-amber-700 prose-code:bg-amber-50 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-sm
        prose-blockquote:border-l-4 prose-blockquote:border-amber-500 prose-blockquote:pl-4 prose-blockquote:italic prose-blockquote:text-gray-700">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {result.interpretation}
        </ReactMarkdown>
      </article>
    </div>
  );
}
