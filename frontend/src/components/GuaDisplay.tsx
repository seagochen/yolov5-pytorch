import type { GuaInfo, ChangingLine } from '../types';

interface GuaDisplayProps {
  title: string;
  gua: GuaInfo;
  changingLines?: ChangingLine[];
  showChangingLines?: boolean;
}

function GuaImage({ binary }: { binary: string }) {
  return (
    <div className="gua-image flex flex-col items-center gap-1 my-4">
      {binary.split('').map((bit, index) => (
        <div
          key={index}
          className={`h-3 flex gap-2 ${bit === '1' ? 'w-24' : 'w-24'}`}
        >
          {bit === '1' ? (
            <div className="w-full h-full bg-gray-800 rounded-sm" />
          ) : (
            <>
              <div className="w-[45%] h-full bg-gray-800 rounded-sm" />
              <div className="w-[45%] h-full bg-gray-800 rounded-sm" />
            </>
          )}
        </div>
      ))}
    </div>
  );
}

export function GuaDisplay({ title, gua, changingLines, showChangingLines }: GuaDisplayProps) {
  return (
    <div className="gua-display bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg p-6 shadow-md">
      <h3 className="text-lg font-semibold text-amber-800 mb-2">{title}</h3>

      <div className="text-center">
        <h4 className="text-2xl font-bold text-gray-800">{gua.name}</h4>
        <p className="text-sm text-gray-500 mb-2">{gua.binary}</p>

        <GuaImage binary={gua.binary} />

        <div className="mt-4 p-3 bg-white/50 rounded-lg">
          <p className="text-sm font-medium text-gray-600 mb-1">卦辞</p>
          <p className="text-gray-800">{gua.description}</p>
        </div>
      </div>

      {showChangingLines && changingLines && changingLines.length > 0 && (
        <div className="mt-4 pt-4 border-t border-amber-200">
          <p className="text-sm font-medium text-amber-700 mb-2">变爻</p>
          <ul className="space-y-2">
            {changingLines.map((line) => (
              <li key={line.position} className="text-sm text-gray-700 bg-white/50 p-2 rounded">
                <span className="font-medium">第{line.position}爻：</span>
                {line.yaoci}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
