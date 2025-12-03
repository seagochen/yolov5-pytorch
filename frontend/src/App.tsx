import { useState } from 'react';
import './App.css';
import { randomDivination, interpretGua } from './api/client';
import type { DivinationResponse, InterpretationResponse } from './types';

function App() {
  const [question, setQuestion] = useState('');
  const [divinationResult, setDivinationResult] = useState<DivinationResponse | null>(null);
  const [interpretation, setInterpretation] = useState<InterpretationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [interpreting, setInterpreting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDivination = async () => {
    if (!question.trim()) {
      setError('请输入您的占卜问题');
      return;
    }

    setLoading(true);
    setError(null);
    setDivinationResult(null);
    setInterpretation(null);

    try {
      const result = await randomDivination({ question });
      setDivinationResult(result);
    } catch (err) {
      setError('占卜失败，请稍后再试');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInterpretation = async () => {
    if (!divinationResult || !question.trim()) {
      return;
    }

    setInterpreting(true);
    setError(null);

    try {
      const result = await interpretGua({
        question,
        ben_gua: divinationResult.ben_gua,
        bian_gua: divinationResult.bian_gua,
        changing_lines: divinationResult.changing_lines,
      });
      setInterpretation(result);
    } catch (err) {
      setError('AI解卦失败，请稍后再试');
      console.error(err);
    } finally {
      setInterpreting(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>周易占卜</h1>
        <p>探索古老智慧，寻求人生指引</p>
      </header>

      <div className="divination-form">
        <div className="form-group">
          <label htmlFor="question">请输入您的占卜问题</label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="例如：最近工作发展如何？感情运势怎样？..."
            disabled={loading}
          />
        </div>

        <button
          className="divination-button"
          onClick={handleDivination}
          disabled={loading || !question.trim()}
        >
          {loading ? '正在占卜...' : '开始占卜'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {divinationResult && (
        <div className="result-container">
          {divinationResult.numbers && (
            <div className="numbers-display">
              <p>占卜数字：</p>
              <div className="numbers">{divinationResult.numbers.join(' - ')}</div>
            </div>
          )}

          <div className="gua-display">
            <div className="gua-card">
              <h3>本卦</h3>
              {divinationResult.ben_gua.symbol && (
                <div className="gua-symbol">{divinationResult.ben_gua.symbol}</div>
              )}
              <div className="gua-name">{divinationResult.ben_gua.name}</div>
              <div className="gua-description">{divinationResult.ben_gua.description}</div>
            </div>

            <div className="gua-card">
              <h3>变卦</h3>
              {divinationResult.bian_gua.symbol && (
                <div className="gua-symbol">{divinationResult.bian_gua.symbol}</div>
              )}
              <div className="gua-name">{divinationResult.bian_gua.name}</div>
              <div className="gua-description">{divinationResult.bian_gua.description}</div>
            </div>
          </div>

          {divinationResult.changing_lines.length > 0 && (
            <div className="changing-lines">
              <h4>变爻</h4>
              {divinationResult.changing_lines.map((line, index) => (
                <div key={index} className="changing-line-item">
                  <strong>第 {line.position} 爻：</strong> {line.yaoci}
                </div>
              ))}
            </div>
          )}

          <button
            className="interpret-button"
            onClick={handleInterpretation}
            disabled={interpreting}
          >
            {interpreting ? 'AI解卦中...' : '请AI解卦'}
          </button>

          {interpretation && (
            <div className="interpretation-result">
              <h3>AI 解卦结果</h3>

              <div className="interpretation-summary">
                <h4>卦象总结</h4>
                <p>{interpretation.summary}</p>
              </div>

              <div className="interpretation-detail">
                <h4>详细解读</h4>
                <p>{interpretation.interpretation}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
