import { useState } from 'react';
import { calculateBazi } from '../api/client';
import type { BaziResponse } from '../types';

export function BaziTab() {
  const [name, setName] = useState('');
  const [useGregorian, setUseGregorian] = useState(true);
  const [year, setYear] = useState('');
  const [month, setMonth] = useState('');
  const [day, setDay] = useState('');
  const [hour, setHour] = useState('');
  const [minute, setMinute] = useState('0');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BaziResponse | null>(null);

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
      const minuteNum = parseInt(minute) || 0;

      // 如果是农历，需要先转换为公历
      if (!useGregorian) {
        // TODO: 实现农历转公历的功能
        setError('农历转换功能暂未实现，请先使用公历输入');
        setLoading(false);
        return;
      }

      const baziResult = await calculateBazi({
        year: yearNum,
        month: monthNum,
        day: dayNum,
        hour: hourNum,
        minute: minuteNum,
      });

      setResult(baziResult);
    } catch (err) {
      setError('计算八字失败，请检查输入是否正确');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getWuXingColor = (wuxing: string): string => {
    const colors: Record<string, string> = {
      '木': '#2d8659',
      '火': '#d4421a',
      '土': '#b8860b',
      '金': '#c0c0c0',
      '水': '#1e90ff',
    };
    return colors[wuxing] || '#666';
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

        <div className="form-group">
          <label>历法选择</label>
          <div className="calendar-toggle">
            <button
              type="button"
              className={`toggle-btn ${useGregorian ? 'active' : ''}`}
              onClick={() => setUseGregorian(true)}
            >
              公历
            </button>
            <button
              type="button"
              className={`toggle-btn ${!useGregorian ? 'active' : ''}`}
              onClick={() => setUseGregorian(false)}
            >
              农历
            </button>
          </div>
        </div>

        <div className="date-inputs">
          <div className="form-group">
            <label htmlFor="year">年</label>
            <input
              type="number"
              id="year"
              value={year}
              onChange={(e) => setYear(e.target.value)}
              placeholder="例如：1990"
              disabled={loading}
              min="1900"
              max="2100"
            />
          </div>

          <div className="form-group">
            <label htmlFor="month">月</label>
            <input
              type="number"
              id="month"
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              placeholder="1-12"
              disabled={loading}
              min="1"
              max="12"
            />
          </div>

          <div className="form-group">
            <label htmlFor="day">日</label>
            <input
              type="number"
              id="day"
              value={day}
              onChange={(e) => setDay(e.target.value)}
              placeholder="1-31"
              disabled={loading}
              min="1"
              max="31"
            />
          </div>

          <div className="form-group">
            <label htmlFor="hour">时</label>
            <input
              type="number"
              id="hour"
              value={hour}
              onChange={(e) => setHour(e.target.value)}
              placeholder="0-23"
              disabled={loading}
              min="0"
              max="23"
            />
          </div>

          <div className="form-group">
            <label htmlFor="minute">分</label>
            <input
              type="number"
              id="minute"
              value={minute}
              onChange={(e) => setMinute(e.target.value)}
              placeholder="0-59"
              disabled={loading}
              min="0"
              max="59"
            />
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

          <div className="bazi-pillars">
            <div className="pillar-card">
              <div className="pillar-label">年柱</div>
              <div className="pillar-value">{result.year_pillar}</div>
              <div className="pillar-detail">
                <span>{result.pillars.year.gan}</span>
                <span>{result.pillars.year.zhi}</span>
              </div>
            </div>

            <div className="pillar-card">
              <div className="pillar-label">月柱</div>
              <div className="pillar-value">{result.month_pillar}</div>
              <div className="pillar-detail">
                <span>{result.pillars.month.gan}</span>
                <span>{result.pillars.month.zhi}</span>
              </div>
            </div>

            <div className="pillar-card">
              <div className="pillar-label">日柱</div>
              <div className="pillar-value">{result.day_pillar}</div>
              <div className="pillar-detail">
                <span>{result.pillars.day.gan}</span>
                <span>{result.pillars.day.zhi}</span>
              </div>
            </div>

            <div className="pillar-card">
              <div className="pillar-label">时柱</div>
              <div className="pillar-value">{result.hour_pillar}</div>
              <div className="pillar-detail">
                <span>{result.pillars.hour.gan}</span>
                <span>{result.pillars.hour.zhi}</span>
              </div>
            </div>
          </div>

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
          </div>

          {result.shensha && result.shensha.count > 0 && (
            <div className="bazi-shensha">
              <h4>神煞分析</h4>
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
                    className={`shensha-card ${shen.type === 'ji' ? 'ji' : 'xiong'}`}
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
