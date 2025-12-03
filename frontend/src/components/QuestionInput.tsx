interface QuestionInputProps {
  onSubmit: (question: string) => void;
  disabled?: boolean;
}

export function QuestionInput({ onSubmit, disabled }: QuestionInputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    onSubmit(value);
  };

  return (
    <div className="question-input">
      <div className="mb-4">
        <label htmlFor="question" className="block text-lg font-medium text-amber-900 mb-2">
          请输入您的问题
        </label>
        <textarea
          id="question"
          onChange={handleChange}
          placeholder="例如：我应该换工作吗？这段感情会有结果吗？"
          className="w-full p-4 border-2 border-amber-300 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-amber-500 resize-none shadow-sm text-lg"
          rows={3}
          disabled={disabled}
        />
      </div>
      <p className="text-sm text-gray-600 mb-4">
        心诚则灵，请诚心默念您的问题后再进行占卜
      </p>
    </div>
  );
}
