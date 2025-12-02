import { useState } from 'react';

interface DivinationPanelProps {
  onCalculate: (numbers: number[]) => void;
  onRandom: () => void;
  disabled?: boolean;
}

export function DivinationPanel({ onCalculate, onRandom, disabled }: DivinationPanelProps) {
  const [numbers, setNumbers] = useState<string>('');
  const [mode, setMode] = useState<'manual' | 'random'>('random');

  const handleManualSubmit = () => {
    if (numbers.length === 6 && /^[6-9]+$/.test(numbers)) {
      const numArray = numbers.split('').map(Number);
      onCalculate(numArray);
    }
  };

  return (
    <div className="divination-panel bg-white rounded-lg shadow-md p-6">
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setMode('random')}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition ${
            mode === 'random'
              ? 'bg-amber-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          摇卦
        </button>
        <button
          onClick={() => setMode('manual')}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition ${
            mode === 'manual'
              ? 'bg-amber-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          手动输入
        </button>
      </div>

      {mode === 'random' ? (
        <div className="text-center">
          <p className="text-gray-600 mb-4">
            点击下方按钮，系统将模拟三枚铜钱摇卦六次
          </p>
          <button
            onClick={onRandom}
            disabled={disabled}
            className="w-full py-4 bg-gradient-to-r from-amber-500 to-amber-600 text-white text-lg font-bold rounded-lg hover:from-amber-600 hover:to-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-lg"
          >
            {disabled ? '占卜中...' : '开始摇卦'}
          </button>
        </div>
      ) : (
        <div>
          <p className="text-gray-600 mb-4">
            请输入6个数字（6-9），代表六次摇卦结果：
          </p>
          <ul className="text-sm text-gray-500 mb-4 list-disc list-inside">
            <li>6 = 老阴（变爻）</li>
            <li>7 = 少阳</li>
            <li>8 = 少阴</li>
            <li>9 = 老阳（变爻）</li>
          </ul>
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={numbers}
              onChange={(e) => {
                const val = e.target.value.replace(/[^6-9]/g, '').slice(0, 6);
                setNumbers(val);
              }}
              placeholder="例如：687778"
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent text-center text-xl tracking-widest"
              maxLength={6}
              disabled={disabled}
            />
          </div>
          <button
            onClick={handleManualSubmit}
            disabled={disabled || numbers.length !== 6}
            className="w-full py-3 bg-gradient-to-r from-amber-500 to-amber-600 text-white font-bold rounded-lg hover:from-amber-600 hover:to-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {disabled ? '占卜中...' : '确认占卜'}
          </button>
        </div>
      )}
    </div>
  );
}
