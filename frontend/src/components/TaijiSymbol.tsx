export function TaijiSymbol({ className = '', animate = false }: { className?: string; animate?: boolean }) {
  return (
    <div className={`relative ${className} select-none`}>
      {/* 太极主体：利用线性渐变实现黑白分明 */}
      <div
        className={`w-full h-full rounded-full shadow-2xl relative overflow-hidden
          ${animate ? 'animate-[spin_12s_linear_infinite]' : ''}`}
        style={{
          background: 'linear-gradient(to bottom, #2c2c2c 50%, #fdfbf7 50%)',
          boxShadow: '0 10px 30px rgba(0,0,0,0.15), inset 0 0 20px rgba(0,0,0,0.05)'
        }}
      >
        {/* 左边的圆（黑中白点区域的背景） */}
        <div className="absolute top-1/2 left-0 w-1/2 h-1/2 -mt-[25%] bg-[#2c2c2c] rounded-full translate-x-1/2"></div>

        {/* 右边的圆（白中黑点区域的背景） */}
        <div className="absolute bottom-1/2 left-0 w-1/2 h-1/2 mb-[-25%] bg-[#fdfbf7] rounded-full translate-x-1/2"></div>

        {/* 上方白点 */}
        <div className="absolute top-1/4 left-1/2 w-[12%] h-[12%] bg-[#fdfbf7] rounded-full -translate-x-1/2 shadow-inner"></div>

        {/* 下方黑点 */}
        <div className="absolute bottom-1/4 left-1/2 w-[12%] h-[12%] bg-[#2c2c2c] rounded-full -translate-x-1/2 shadow-inner"></div>
      </div>
    </div>
  );
}
