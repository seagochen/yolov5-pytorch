import { useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { languageNames } from '../i18n/translations';
import type { Language } from '../i18n/translations';
import { divinationApi, interpretationApi } from '../services/api';
import type { DivinationResult as DivinationType, InterpretationResult as InterpretationType } from '../types';
import { TaijiSymbol } from '../components/TaijiSymbol';

type DivinationMethod = 'computer' | 'coin' | 'yarrow';
type Stage = 'question' | 'divining' | 'result';

export function Divination() {
  const { language, setLanguage, t } = useLanguage();
  const [divinationMethod, setDivinationMethod] = useState<DivinationMethod>('computer');
  const [question, setQuestion] = useState('');
  const [stage, setStage] = useState<Stage>('question');
  const [divinationResult, setDivinationResult] = useState<DivinationType | null>(null);
  const [interpretationResult, setInterpretationResult] = useState<InterpretationType | null>(null);
  const [showInterpretation, setShowInterpretation] = useState(false);
  const [typingText, setTypingText] = useState('');

  // 占卜逻辑
  const handleDivination = async () => {
    if (!question.trim()) return;
    setStage('divining');
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      const result = await divinationApi.random({ question: question || undefined });
      setDivinationResult(result);
      const interpretation = await interpretationApi.analyze({
        question,
        ben_gua: result.ben_gua,
        bian_gua: result.bian_gua,
        changing_lines: result.changing_lines,
      });
      setInterpretationResult(interpretation);
      setStage('result');
    } catch (err) {
      console.error('占卜失败:', err);
      setStage('question');
    }
  };

  // 打字机效果
  useEffect(() => {
    if (!showInterpretation || !interpretationResult) {
      setTypingText('');
      return;
    }
    const fullText = interpretationResult.interpretation;
    let currentIndex = 0;
    const timer = setInterval(() => {
      if (currentIndex <= fullText.length) {
        setTypingText(fullText.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(timer);
      }
    }, 20);
    return () => clearInterval(timer);
  }, [showInterpretation, interpretationResult]);

  const handleReset = () => {
    setQuestion('');
    setStage('question');
    setDivinationResult(null);
    setInterpretationResult(null);
    setShowInterpretation(false);
    setTypingText('');
  };

  return (
    <div className="min-h-screen relative flex flex-col" style={{ backgroundColor: 'var(--bg-paper)', color: 'var(--ink-primary)' }}>
      {/* 顶部导航栏：移至右上角，极简风格 */}
      <header className="absolute top-0 right-0 p-6 z-50 flex gap-4 items-center">
        <div className="relative group">
          <select
            value={divinationMethod}
            onChange={(e) => setDivinationMethod(e.target.value as DivinationMethod)}
            className="appearance-none bg-transparent border px-4 py-1.5 rounded-full text-sm cursor-pointer hover:border-[var(--cinnabar)] transition-colors pr-8 focus:outline-none"
            style={{ borderColor: 'var(--ink-secondary)', color: 'var(--ink-primary)' }}
          >
            <option value="computer">{t.computerDivination}</option>
            <option value="coin">{t.coinDivination}</option>
            <option value="yarrow">{t.yarrowDivination}</option>
          </select>
          <span className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-xs" style={{ color: 'var(--ink-secondary)' }}>▼</span>
        </div>

        <div className="relative group">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as Language)}
            className="appearance-none bg-transparent border px-4 py-1.5 rounded-full text-sm cursor-pointer hover:border-[var(--cinnabar)] transition-colors pr-8 focus:outline-none"
            style={{ borderColor: 'var(--ink-secondary)', color: 'var(--ink-primary)' }}
          >
            {Object.entries(languageNames).map(([code, name]) => (
              <option key={code} value={code}>{name}</option>
            ))}
          </select>
          <span className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-xs" style={{ color: 'var(--ink-secondary)' }}>▼</span>
        </div>
      </header>

      {/* 主内容区域 */}
      <main className="flex-1 flex flex-col items-center justify-center p-4 relative w-full max-w-5xl mx-auto">

        {/* 阶段 1: 提问 */}
        {stage === 'question' && (
          <div className="flex flex-col items-center w-full max-w-lg animate-fade-in">
            {/* 太极图 */}
            <div className="w-40 h-40 mb-12 animate-float filter drop-shadow-xl">
              <TaijiSymbol animate />
            </div>

            <h1 className="text-5xl font-light tracking-[0.3em] mb-4" style={{ color: 'var(--ink-primary)' }}>
              周易·问卦
            </h1>
            <p className="mb-12 tracking-widest text-sm font-light" style={{ color: 'var(--ink-secondary)' }}>
              心诚则灵 · 万物皆数
            </p>

            {/* 输入框 */}
            <div className="w-full relative group input-glow transition-all duration-500">
              <div className="absolute inset-0 bg-white opacity-40 rounded-xl blur-sm group-hover:opacity-60 transition-opacity"></div>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder={t.questionPlaceholder}
                rows={3}
                className="relative w-full bg-transparent border-b-2 px-4 py-4 text-xl text-center placeholder:text-gray-400 placeholder:font-light outline-none resize-none focus:border-[var(--cinnabar)] transition-colors"
                style={{ borderColor: 'var(--ink-secondary)', color: 'var(--ink-primary)' }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleDivination();
                  }
                }}
              />
            </div>

            <button
              onClick={handleDivination}
              disabled={!question.trim()}
              className="mt-12 px-10 py-3 text-lg tracking-[0.5em] rounded-sm hover:bg-[var(--cinnabar)] transition-all duration-500 disabled:opacity-30 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              style={{ backgroundColor: 'var(--ink-primary)', color: '#f7f4ed' }}
            >
              <span className="pl-2">起卦</span>
            </button>
          </div>
        )}

        {/* 阶段 2: 演算中 */}
        {stage === 'divining' && (
          <div className="flex flex-col items-center justify-center animate-fade-in">
            <div className="w-24 h-24 mb-8">
              <TaijiSymbol animate />
            </div>
            <p className="text-xl tracking-[0.5em] animate-pulse" style={{ color: 'var(--ink-secondary)' }}>
              推演天机...
            </p>
          </div>
        )}

        {/* 阶段 3: 结果与解卦 */}
        {stage === 'result' && divinationResult && (
          <div className="w-full animate-fade-in pb-20">
            {/* 顶部问题回顾 */}
            <div className="text-center mb-12 border-b border-gray-200 pb-8">
              <p className="text-sm mb-2" style={{ color: 'var(--ink-secondary)' }}>所问何事</p>
              <h2 className="text-2xl font-medium" style={{ color: 'var(--ink-primary)' }}>" {question} "</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">
              {/* 本卦 */}
              <div className="transform transition-all hover:scale-105 duration-500 bg-white/40 rounded-2xl p-8 shadow-lg">
                <h3 className="text-center text-xl mb-6 tracking-[0.2em] font-light" style={{ color: 'var(--ink-primary)' }}>
                  {t.originalGua}
                </h3>
                <div className="text-center mb-4">
                  <div className="text-7xl mb-4" style={{ color: 'var(--ink-primary)' }}>
                    {divinationResult.ben_gua.symbol || '☯'}
                  </div>
                  <p className="text-2xl font-normal mb-2" style={{ color: 'var(--ink-primary)' }}>
                    {divinationResult.ben_gua.name}
                  </p>
                </div>
                <div className="mt-6 p-4 rounded-xl bg-black/5">
                  <p className="text-sm leading-relaxed" style={{ color: 'var(--ink-secondary)' }}>
                    {divinationResult.ben_gua.description}
                  </p>
                </div>
                {divinationResult.changing_lines.length > 0 && (
                  <div className="mt-4 text-center text-sm" style={{ color: 'var(--cinnabar)' }}>
                    变爻：{divinationResult.changing_lines.map(cl => cl.position).join('、')}
                  </div>
                )}
              </div>

              {/* 变卦 */}
              <div className="transform transition-all hover:scale-105 duration-500 delay-100 bg-white/40 rounded-2xl p-8 shadow-lg">
                <h3 className="text-center text-xl mb-6 tracking-[0.2em] font-light" style={{ color: 'var(--ink-primary)' }}>
                  {t.changedGua}
                </h3>
                <div className="text-center mb-4">
                  <div className="text-7xl mb-4" style={{ color: 'var(--ink-primary)' }}>
                    {divinationResult.bian_gua.symbol || '☯'}
                  </div>
                  <p className="text-2xl font-normal mb-2" style={{ color: 'var(--ink-primary)' }}>
                    {divinationResult.bian_gua.name}
                  </p>
                </div>
                <div className="mt-6 p-4 rounded-xl bg-black/5">
                  <p className="text-sm leading-relaxed" style={{ color: 'var(--ink-secondary)' }}>
                    {divinationResult.bian_gua.description}
                  </p>
                </div>
              </div>
            </div>

            {/* AI 解卦区域 */}
            <div className="mt-20 max-w-3xl mx-auto">
              {!showInterpretation ? (
                <div className="text-center">
                  <div className="w-16 h-1 mx-auto mb-8 opacity-20" style={{ backgroundColor: 'var(--cinnabar)' }}></div>
                  <button
                    onClick={() => setShowInterpretation(true)}
                    className="group relative px-8 py-3 overflow-hidden rounded-full border hover:text-white transition-colors duration-300"
                    style={{ borderColor: 'var(--ink-primary)', color: 'var(--ink-primary)' }}
                  >
                    <span className="absolute inset-0 w-full h-full transform -translate-x-full group-hover:translate-x-0 transition-transform duration-300 ease-out" style={{ backgroundColor: 'var(--ink-primary)' }}></span>
                    <span className="relative z-10 tracking-[0.2em]">{t.interpretationButton}</span>
                  </button>
                </div>
              ) : (
                <div className="bg-white/50 p-8 md:p-12 rounded-lg shadow-sm border border-gray-100 relative overflow-hidden">
                   {/* 装饰水印 */}
                  <div className="absolute top-0 right-0 text-[10rem] opacity-5 pointer-events-none select-none font-serif">解</div>

                  <h3 className="text-xl font-bold mb-6 flex items-center gap-2" style={{ color: 'var(--cinnabar)' }}>
                    <span className="w-1 h-6 inline-block" style={{ backgroundColor: 'var(--cinnabar)' }}></span>
                    大师解卦
                  </h3>
                  <div className="text-justify text-lg leading-loose font-serif" style={{ color: 'var(--ink-primary)' }}>
                    {typingText}
                  </div>

                  {typingText.length === interpretationResult?.interpretation.length && (
                    <div className="text-center mt-12 pt-8 border-t border-gray-200">
                      <button
                         onClick={handleReset}
                         className="hover:text-[var(--cinnabar)] transition-colors text-sm tracking-widest border-b border-transparent hover:border-[var(--cinnabar)] pb-1"
                         style={{ color: 'var(--ink-secondary)' }}
                      >
                        {t.reset}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
