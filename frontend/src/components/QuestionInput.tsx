import { useState } from 'react';

interface QuestionInputProps {
  onSubmit: (question: string) => void;
  disabled?: boolean;
}

export function QuestionInput({ onSubmit, disabled }: QuestionInputProps) {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim()) {
      onSubmit(question.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="question-input">
      <div className="mb-4">
        <label htmlFor="question" className="block text-lg font-medium mb-2">
          请输入您的问题
        </label>
        <textarea
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="例如：我应该换工作吗？这段感情会有结果吗？"
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none"
          rows={3}
          disabled={disabled}
        />
      </div>
      <p className="text-sm text-gray-500 mb-4">
        心诚则灵，请诚心默念您的问题后再进行占卜
      </p>
    </form>
  );
}
