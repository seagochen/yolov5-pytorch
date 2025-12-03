import type { GuaInfo, ChangingLine } from '../types';

interface GuaDisplayProps {
  title: string;
  gua: GuaInfo;
  changingLines?: ChangingLine[];
  showChangingLines?: boolean;
}

export function GuaDisplay({ title, gua, changingLines, showChangingLines }: GuaDisplayProps) {
  return (
    <div className="gua-display bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl p-8 shadow-xl border border-amber-200 hover:shadow-2xl transition-all duration-300">
      <div className="text-center mb-6">
        <div className="inline-block bg-amber-800 text-amber-50 px-4 py-1 rounded-full text-sm font-medium mb-4">
          {title}
        </div>
      </div>

      <div className="text-center">
        {/* Unicode 卦象符号 - 超大显示 */}
        <div className="text-[120px] leading-none my-6 text-gray-800 font-serif">
          {gua.image}
        </div>

        <h4 className="text-3xl font-bold text-gray-800 mb-2">{gua.name}</h4>
        <p className="text-xs text-gray-500 mb-4 font-mono">{gua.binary}</p>

        <div className="mt-6 p-4 bg-white/70 rounded-xl shadow-inner">
          <p className="text-xs font-semibold text-amber-700 mb-2 uppercase tracking-wider">卦辞</p>
          <p className="text-gray-800 leading-relaxed">{gua.description}</p>
        </div>
      </div>

      {showChangingLines && changingLines && changingLines.length > 0 && (
        <div className="mt-6 pt-6 border-t border-amber-300">
          <p className="text-sm font-semibold text-amber-800 mb-3 flex items-center justify-center">
            <span className="w-2 h-2 bg-amber-600 rounded-full mr-2"></span>
            变爻
          </p>
          <ul className="space-y-3">
            {changingLines.map((line) => (
              <li key={line.position} className="text-sm text-gray-700 bg-white/70 p-3 rounded-lg shadow-sm">
                <span className="font-bold text-amber-700">第{line.position}爻：</span>
                {line.yaoci}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
