import { useState } from 'react';
import { QuestionInput } from '../components/QuestionInput';
import { DivinationPanel } from '../components/DivinationPanel';
import { GuaDisplay } from '../components/GuaDisplay';
import { InterpretationResult } from '../components/InterpretationResult';
import { divinationApi, interpretationApi } from '../services/api';
import type { DivinationResult as DivinationType, InterpretationResult as InterpretationType } from '../types';

export function Divination() {
  const [question, setQuestion] = useState('');
  const [divinationResult, setDivinationResult] = useState<DivinationType | null>(null);
  const [interpretationResult, setInterpretationResult] = useState<InterpretationType | null>(null);
  const [loading, setLoading] = useState(false);
  const [interpreting, setInterpreting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDivination = async (numbers?: number[]) => {
    setLoading(true);
    setError(null);
    setDivinationResult(null);
    setInterpretationResult(null);

    try {
      let result: DivinationType;
      if (numbers) {
        result = await divinationApi.calculate({ numbers, question: question || undefined });
      } else {
        result = await divinationApi.random({ question: question || undefined });
      }
      setDivinationResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '占卜失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleInterpret = async () => {
    if (!divinationResult || !question.trim()) {
      setError('请先输入问题并完成占卜');
      return;
    }

    setInterpreting(true);
    setError(null);

    try {
      const result = await interpretationApi.analyze({
        question,
        ben_gua: divinationResult.ben_gua,
        bian_gua: divinationResult.bian_gua,
        changing_lines: divinationResult.changing_lines,
      });
      setInterpretationResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'AI 解卦失败，请重试');
    } finally {
      setInterpreting(false);
    }
  };

  const handleReset = () => {
    setQuestion('');
    setDivinationResult(null);
    setInterpretationResult(null);
    setError(null);
  };

  return (
    <>
      {/* Question Input */}
      <section className="mb-8">
        <QuestionInput
          onSubmit={setQuestion}
          disabled={loading || interpreting}
        />
        {question && (
          <div className="mt-2 p-3 bg-amber-100 rounded-lg">
            <span className="text-amber-800 font-medium">您的问题：</span>
            <span className="text-gray-700">{question}</span>
          </div>
        )}
      </section>

      {/* Divination Panel */}
      <section className="mb-8">
        <DivinationPanel
          onCalculate={(numbers) => handleDivination(numbers)}
          onRandom={() => handleDivination()}
          disabled={loading}
        />
      </section>

      {/* Error Display */}
      {error && (
        <div className="mb-8 p-4 bg-red-100 border border-red-300 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Divination Result */}
      {divinationResult && (
        <section className="mb-8">
          <h2 className="text-xl font-bold text-amber-800 mb-4">占卜结果</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <GuaDisplay
              title="本卦"
              gua={divinationResult.ben_gua}
              changingLines={divinationResult.changing_lines}
              showChangingLines={true}
            />
            <GuaDisplay
              title="变卦"
              gua={divinationResult.bian_gua}
            />
          </div>

          {/* AI Interpret Button */}
          <div className="mt-6 text-center">
            <button
              onClick={handleInterpret}
              disabled={interpreting || !question.trim()}
              className="px-8 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-lg"
            >
              {interpreting ? '解卦中...' : 'AI 解卦'}
            </button>
            {!question.trim() && (
              <p className="mt-2 text-sm text-gray-500">请先在上方输入您的问题</p>
            )}
          </div>
        </section>
      )}

      {/* AI Interpretation Result */}
      {(interpreting || interpretationResult) && (
        <section className="mb-8">
          <InterpretationResult
            result={interpretationResult}
            loading={interpreting}
            error={null}
          />
        </section>
      )}

      {/* Reset Button */}
      {(divinationResult || interpretationResult) && (
        <div className="text-center">
          <button
            onClick={handleReset}
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
          >
            重新占卜
          </button>
        </div>
      )}
    </>
  );
}
