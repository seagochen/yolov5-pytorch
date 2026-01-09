import { useState, useMemo } from 'react';
import { calculateBazi } from '../api/client';
import type { BaziResponse } from '../types';

// 十二时辰定义
const SHICHEN = [
  { value: 23, label: '子时 (23:00-00:59)' },
  { value: 1, label: '丑时 (01:00-02:59)' },
  { value: 3, label: '寅时 (03:00-04:59)' },
  { value: 5, label: '卯时 (05:00-06:59)' },
  { value: 7, label: '辰时 (07:00-08:59)' },
  { value: 9, label: '巳时 (09:00-10:59)' },
  { value: 11, label: '午时 (11:00-12:59)' },
  { value: 13, label: '未时 (13:00-14:59)' },
  { value: 15, label: '申时 (15:00-16:59)' },
  { value: 17, label: '酉时 (17:00-18:59)' },
  { value: 19, label: '戌时 (19:00-20:59)' },
  { value: 21, label: '亥时 (21:00-22:59)' },
];

// 判断是否为闰年
const isLeapYear = (year: number): boolean => {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
};

// 获取某月的天数
const getDaysInMonth = (year: number, month: number): number => {
  const daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (month === 2 && isLeapYear(year)) {
    return 29;
  }
  return daysInMonth[month - 1];
};

// 五行颜色
const getWuXingColor = (wuxing: string): string => {
  const colors: Record<string, string> = {
    '木': '#2d8659',
    '火': '#d4421a',
    '土': '#b8860b',
    '金': '#8b7355',
    '水': '#1e90ff',
  };
  return colors[wuxing] || '#666';
};

// 五行对应的天干/地支
const WUXING_MAP: Record<string, string> = {
  '甲': '木', '乙': '木',
  '丙': '火', '丁': '火',
  '戊': '土', '己': '土',
  '庚': '金', '辛': '金',
  '壬': '水', '癸': '水',
  '子': '水', '丑': '土', '寅': '木', '卯': '木',
  '辰': '土', '巳': '火', '午': '火', '未': '土',
  '申': '金', '酉': '金', '戌': '土', '亥': '水'
};

export function BaziTab() {
  const [name, setName] = useState('');
  const [year, setYear] = useState('');
  const [month, setMonth] = useState('');
  const [day, setDay] = useState('');
  const [hour, setHour] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BaziResponse | null>(null);

  // 根据年月计算可选的日期
  const availableDays = useMemo(() => {
    if (!year || !month) return [];
    const yearNum = parseInt(year);
    const monthNum = parseInt(month);
    if (isNaN(yearNum) || isNaN(monthNum)) return [];
    const maxDays = getDaysInMonth(yearNum, monthNum);
    return Array.from({ length: maxDays }, (_, i) => i + 1);
  }, [year, month]);

  // 当年或月改变时，重置日期（如果当前日期超出范围）
  const handleYearChange = (newYear: string) => {
    setYear(newYear);
    if (day && month && newYear) {
      const maxDays = getDaysInMonth(parseInt(newYear), parseInt(month));
      if (parseInt(day) > maxDays) {
        setDay('');
      }
    }
  };

  const handleMonthChange = (newMonth: string) => {
    setMonth(newMonth);
    if (day && year && newMonth) {
      const maxDays = getDaysInMonth(parseInt(year), parseInt(newMonth));
      if (parseInt(day) > maxDays) {
        setDay('');
      }
    }
  };

  const handleCalculate = async () => {
    if (!name.trim()) {
      setError('请输入姓名');
      return;
    }

    if (!year || !month || !day || !hour) {
      setError('请填写完整的出生日期和时辰');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const yearNum = parseInt(year);
      const monthNum = parseInt(month);
      const dayNum = parseInt(day);
      const hourNum = parseInt(hour);

      const baziResult = await calculateBazi({
        year: yearNum,
        month: monthNum,
        day: dayNum,
        hour: hourNum,
        minute: 0,
      });

      setResult(baziResult);
    } catch (err) {
      setError('计算八字失败，请检查输入是否正确');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 渲染四柱卡片
  const renderPillarCard = (
    label: string,
    pillarKey: 'year' | 'month' | 'day' | 'hour',
    _pillar: string,
    gan: string,
    zhi: string
  ) => {
    if (!result) return null;

    const cangGan = result.cang_gan[pillarKey];
    const nayin = result.nayin[pillarKey];
    const shishenKey = `${pillarKey}_gan` as keyof typeof result.shishen;
    const shishen = result.shishen[shishenKey];
    const cangganShishen = result.canggan_shishen[pillarKey];
    const pillarShensha = result.shensha.by_pillar?.[pillarKey] || [];

    return (
      <div className="pillar-card-enhanced">
        <div className="pillar-label">{label}</div>

        {/* 十神 */}
        <div className="pillar-shishen">
          <span className={`shishen-tag ${getShishenClass(shishen)}`}>
            {shishen}
          </span>
        </div>

        {/* 天干 */}
        <div
          className="pillar-gan"
          style={{ color: getWuXingColor(WUXING_MAP[gan]) }}
        >
          {gan}
        </div>

        {/* 地支 */}
        <div
          className="pillar-zhi"
          style={{ color: getWuXingColor(WUXING_MAP[zhi]) }}
        >
          {zhi}
        </div>

        {/* 藏干及其十神 */}
        <div className="pillar-canggan">
          <div className="canggan-label">藏干</div>
          <div className="canggan-items">
            {cangGan.map((cg, idx) => (
              <div key={idx} className="canggan-item">
                <span
                  className="canggan-char"
                  style={{ color: getWuXingColor(WUXING_MAP[cg]) }}
                >
                  {cg}
                </span>
                <span className={`canggan-shishen ${getShishenClass(cangganShishen[idx])}`}>
                  {cangganShishen[idx]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* 纳音 */}
        <div className="pillar-nayin">
          <span className="nayin-label">纳音</span>
          <span className="nayin-value">{nayin}</span>
        </div>

        {/* 神煞 */}
        {pillarShensha.length > 0 && (
          <div className="pillar-shensha">
            {pillarShensha.map((ss, idx) => (
              <span
                key={idx}
                className={`shensha-tag ${ss.type}`}
                title={ss.description}
              >
                {ss.name}
              </span>
            ))}
          </div>
        )}
      </div>
    );
  };

  // 获取十神样式类
  const getShishenClass = (shishen: string): string => {
    const classes: Record<string, string> = {
      '比肩': 'bijian',
      '劫财': 'jiecai',
      '食神': 'shishen',
      '伤官': 'shangguan',
      '偏财': 'piancai',
      '正财': 'zhengcai',
      '七杀': 'qisha',
      '正官': 'zhengguan',
      '偏印': 'pianyin',
      '正印': 'zhengyin',
      '日主': 'rizhu',
    };
    return classes[shishen] || '';
  };

  return (
    <div className="tab-content">
      <div className="bazi-form">
        <div className="form-group">
          <label htmlFor="name">姓名</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="请输入您的姓名"
            disabled={loading}
          />
        </div>

        <div className="date-inputs">
          <div className="form-group">
            <label htmlFor="year">年</label>
            <input
              type="number"
              id="year"
              value={year}
              onChange={(e) => handleYearChange(e.target.value)}
              placeholder="例如：1990"
              disabled={loading}
              min="1900"
              max="2100"
            />
          </div>

          <div className="form-group">
            <label htmlFor="month">月</label>
            <select
              id="month"
              value={month}
              onChange={(e) => handleMonthChange(e.target.value)}
              disabled={loading || !year}
            >
              <option value="">请选择</option>
              {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                <option key={m} value={m}>
                  {m}月
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="day">日</label>
            <select
              id="day"
              value={day}
              onChange={(e) => setDay(e.target.value)}
              disabled={loading || !year || !month}
            >
              <option value="">请选择</option>
              {availableDays.map((d) => (
                <option key={d} value={d}>
                  {d}日
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="hour">时辰</label>
            <select
              id="hour"
              value={hour}
              onChange={(e) => setHour(e.target.value)}
              disabled={loading}
            >
              <option value="">请选择</option>
              {SHICHEN.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          className="divination-button"
          onClick={handleCalculate}
          disabled={loading || !name.trim() || !year || !month || !day || !hour}
        >
          {loading ? '计算中...' : '开始排盘'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result-container">
          <div className="bazi-header">
            <h3>{name} 的八字排盘</h3>
            <p className="bazi-datetime">
              公历：{result.solar.formatted}<br />
              农历：{result.lunar.formatted}（{result.lunar.sheng_xiao}年）
            </p>
          </div>

          {/* 四柱详细信息 */}
          <div className="bazi-pillars-enhanced">
            {renderPillarCard('年柱', 'year', result.year_pillar,
              result.pillars.year.gan, result.pillars.year.zhi)}
            {renderPillarCard('月柱', 'month', result.month_pillar,
              result.pillars.month.gan, result.pillars.month.zhi)}
            {renderPillarCard('日柱', 'day', result.day_pillar,
              result.pillars.day.gan, result.pillars.day.zhi)}
            {renderPillarCard('时柱', 'hour', result.hour_pillar,
              result.pillars.hour.gan, result.pillars.hour.zhi)}
          </div>

          {/* 五行分析 */}
          <div className="bazi-wuxing">
            <h4>五行分析</h4>
            <div className="wuxing-chart">
              {Object.entries(result.wu_xing_count).map(([element, count]) => (
                <div key={element} className="wuxing-item">
                  <div
                    className="wuxing-label"
                    style={{ color: getWuXingColor(element) }}
                  >
                    {element}
                  </div>
                  <div className="wuxing-count">{count}</div>
                  <div
                    className="wuxing-bar"
                    style={{
                      width: `${(count / 8) * 100}%`,
                      backgroundColor: getWuXingColor(element),
                    }}
                  />
                </div>
              ))}
            </div>
            {/* 五行缺失提示 */}
            {Object.entries(result.wu_xing_count).some(([, count]) => count === 0) && (
              <div className="wuxing-missing">
                <span>五行缺：</span>
                {Object.entries(result.wu_xing_count)
                  .filter(([, count]) => count === 0)
                  .map(([element]) => (
                    <span
                      key={element}
                      className="missing-element"
                      style={{ color: getWuXingColor(element) }}
                    >
                      {element}
                    </span>
                  ))}
              </div>
            )}
          </div>

          {/* 神煞总览 */}
          {result.shensha && result.shensha.count > 0 && (
            <div className="bazi-shensha">
              <h4>神煞总览</h4>
              <div className="shensha-summary">
                <div className="shensha-count">
                  <span className="ji-count">吉神：{result.shensha.ji.length}</span>
                  <span className="xiong-count">凶神：{result.shensha.xiong.length}</span>
                </div>
              </div>
              <div className="shensha-details">
                {result.shensha.details.map((shen, index) => (
                  <div
                    key={index}
                    className={`shensha-card ${shen.type}`}
                  >
                    <div className="shensha-name">{shen.name}</div>
                    <div className="shensha-desc">{shen.description}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
