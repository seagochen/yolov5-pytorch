import { useState, useEffect, useMemo } from 'react';
import { qimenPaipan, getQimenGuide } from '../api/client';
import type { QimenResponse } from '../types';

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

export function QimenTab() {
  const [year, setYear] = useState('');
  const [month, setMonth] = useState('');
  const [day, setDay] = useState('');
  const [hour, setHour] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QimenResponse | null>(null);
  const [showGuide, setShowGuide] = useState(false);
  const [guideData, setGuideData] = useState<any>(null);

  // 加载指南数据
  useEffect(() => {
    const loadGuide = async () => {
      try {
        const data = await getQimenGuide();
        setGuideData(data);
      } catch (err) {
        console.error('加载指南数据失败:', err);
      }
    };
    loadGuide();
  }, []);

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
    if (!year || !month || !day || !hour) {
      setError('请填写完整的日期和时辰');
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

      const qimenResult = await qimenPaipan({
        year: yearNum,
        month: monthNum,
        day: dayNum,
        hour: hourNum,
        minute: 0,
      });

      setResult(qimenResult);
    } catch (err) {
      setError('奇门遁甲排盘失败，请检查输入是否正确');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getJiXiongColor = (jiXiong: string): string => {
    if (jiXiong.includes('大吉') || jiXiong.includes('吉')) {
      return '#2d8659';
    } else if (jiXiong.includes('大凶') || jiXiong.includes('凶')) {
      return '#d4421a';
    }
    return '#b8860b';
  };

  // 宫位用神含义 - 从 API 数据加载，如果没有则使用默认值
  const getGongYongShen = (gongNum: number): { name: string; meaning: string }[] => {
    if (guideData?.yongshen_meanings?.meanings) {
      return guideData.yongshen_meanings.meanings[gongNum.toString()] || [];
    }

    // 默认值（备用）
    const meanings: Record<number, { name: string; meaning: string }[]> = {
      1: [
        { name: '年干', meaning: '求测者本人、自己的想法' },
        { name: '值符', meaning: '最重要的人或事，核心问题' },
      ],
      3: [
        { name: '月干', meaning: '兄弟姐妹、同事、朋友' },
        { name: '求财', meaning: '求财看震宫' },
      ],
      6: [
        { name: '日干', meaning: '父母、领导、上级、贵人' },
        { name: '求官', meaning: '求官看乾宫' },
      ],
      7: [
        { name: '时干', meaning: '子女、下属、晚辈' },
        { name: '求学', meaning: '求学看兑宫' },
      ],
      2: [{ name: '坤宫', meaning: '母亲、妻子、老妇人、土地、房产' }],
      4: [{ name: '巽宫', meaning: '长女、文书、消息、远方' }],
      8: [{ name: '艮宫', meaning: '少男、停止、阻碍、山林' }],
      9: [{ name: '离宫', meaning: '中女、文采、名声、光明' }],
    };
    return meanings[gongNum] || [];
  };

  const renderGongPosition = (gongNum: number) => {
    // 九宫格布局位置映射
    const positions: Record<number, { row: number; col: number }> = {
      4: { row: 0, col: 0 }, // 巽宫
      9: { row: 0, col: 1 }, // 离宫
      2: { row: 0, col: 2 }, // 坤宫
      3: { row: 1, col: 0 }, // 震宫
      5: { row: 1, col: 1 }, // 中宫
      7: { row: 1, col: 2 }, // 兑宫
      8: { row: 2, col: 0 }, // 艮宫
      1: { row: 2, col: 1 }, // 坎宫
      6: { row: 2, col: 2 }, // 乾宫
    };
    return positions[gongNum];
  };

  const renderJiuGong = () => {
    if (!result) return null;

    const gongArray = Array.from({ length: 9 }, (_, i) => i + 1);
    const grid: (number | null)[][] = [
      [null, null, null],
      [null, null, null],
      [null, null, null],
    ];

    // 将宫位填入九宫格
    gongArray.forEach((gongNum) => {
      const pos = renderGongPosition(gongNum);
      grid[pos.row][pos.col] = gongNum;
    });

    return (
      <div className="jiugong-grid">
        {grid.map((row, rowIndex) => (
          <div key={rowIndex} className="jiugong-row">
            {row.map((gongNum, colIndex) => {
              if (!gongNum) return null;
              const gong = result.jiu_gong[gongNum];
              const isZhiFu = result.zhi_fu_gong === gongNum;

              return (
                <div
                  key={colIndex}
                  className={`gong-card ${isZhiFu ? 'zhifu' : ''}`}
                  style={{
                    borderColor: getJiXiongColor(gong.ji_xiong),
                  }}
                >
                  <div className="gong-header">
                    <span className="gong-name">{gong.gong_name}</span>
                    {isZhiFu && <span className="zhifu-badge">值符</span>}
                  </div>
                  <div className="gong-content">
                    <div className="gong-item">
                      <span className="label">八卦：</span>
                      <span>{gong.ba_gua}</span>
                    </div>
                    <div className="gong-item">
                      <span className="label">地盘：</span>
                      <span>{gong.di_pan}</span>
                    </div>
                    <div className="gong-item">
                      <span className="label">天盘：</span>
                      <span>{gong.tian_pan}</span>
                    </div>
                    <div className="gong-item">
                      <span className="label">八门：</span>
                      <span>{gong.ba_men}</span>
                    </div>
                    <div className="gong-item">
                      <span className="label">九星：</span>
                      <span>{gong.jiu_xing}</span>
                    </div>
                    <div className="gong-item">
                      <span className="label">八神：</span>
                      <span>{gong.ba_shen}</span>
                    </div>
                    <div
                      className="gong-jixiong"
                      style={{ color: getJiXiongColor(gong.ji_xiong) }}
                    >
                      {gong.ji_xiong}
                    </div>
                    {gong.notes.length > 0 && (
                      <div className="gong-notes">
                        {gong.notes.map((note, idx) => (
                          <div key={idx} className="note-item">
                            • {note}
                          </div>
                        ))}
                      </div>
                    )}
                    {getGongYongShen(gongNum).length > 0 && (
                      <div className="gong-yongshen">
                        <div className="yongshen-title">用神含义：</div>
                        {getGongYongShen(gongNum).map((ys, idx) => (
                          <div key={idx} className="yongshen-item">
                            <strong>{ys.name}：</strong>
                            <span>{ys.meaning}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="tab-content">
      {showGuide && (
        <div className="guide-overlay" onClick={() => setShowGuide(false)}>
          <div className="guide-modal" onClick={(e) => e.stopPropagation()}>
            <div className="guide-header">
              <h3>奇门遁甲使用指南</h3>
              <button className="guide-close" onClick={() => setShowGuide(false)}>
                ×
              </button>
            </div>
            <div className="guide-content">
              {guideData ? (
                <>
                  {/* 简介 */}
                  {guideData.introduction && (
                    <section>
                      <h4>{guideData.introduction.title}</h4>
                      <p>{guideData.introduction.description}</p>
                    </section>
                  )}

                  {/* 九宫格元素说明 */}
                  {guideData.elements && (
                    <section>
                      <h4>{guideData.elements.title}</h4>
                      <ul>
                        {guideData.elements.items.map((item: any, idx: number) => (
                          <li key={idx}>
                            <strong>{item.name}：</strong>{item.description}
                          </li>
                        ))}
                      </ul>
                    </section>
                  )}

                  {/* 四柱用神 */}
                  {guideData.four_pillars && (
                    <section>
                      <h4>{guideData.four_pillars.title}</h4>
                      {guideData.four_pillars.description && (
                        <p>{guideData.four_pillars.description}</p>
                      )}
                      <ul>
                        {guideData.four_pillars.pillars.map((pillar: any, idx: number) => (
                          <li key={idx}>
                            <strong>{pillar.name}（{pillar.gong}）：</strong>{pillar.meaning}
                          </li>
                        ))}
                      </ul>
                      {guideData.four_pillars.examples && (
                        <p className="guide-tip">
                          💡 <strong>应用举例：</strong>
                          {guideData.four_pillars.examples.map((ex: any, idx: number) => (
                            <span key={idx}>
                              <br />• {ex.scenario}看{ex.pillar}，{ex.explanation}
                            </span>
                          ))}
                        </p>
                      )}
                    </section>
                  )}

                  {/* 八卦宫位 */}
                  {guideData.bagua_palaces && (
                    <section>
                      <h4>{guideData.bagua_palaces.title}</h4>
                      <ul>
                        {guideData.bagua_palaces.palaces.map((palace: any, idx: number) => (
                          <li key={idx}>
                            <strong>{palace.name}（{palace.number}）：</strong>
                            {palace.direction}，{palace.element}，{palace.meanings.join('、')}
                          </li>
                        ))}
                      </ul>
                    </section>
                  )}

                  {/* 吉凶判断 */}
                  {guideData.fortune_judgment && (
                    <section>
                      <h4>{guideData.fortune_judgment.title}</h4>
                      <ul>
                        {guideData.fortune_judgment.categories.map((cat: any, idx: number) => (
                          <li key={idx}>
                            <strong>{cat.type}：</strong>
                            {Array.isArray(cat.items) && typeof cat.items[0] === 'string'
                              ? cat.items.join('、')
                              : cat.items.map((item: any) =>
                                  typeof item === 'string' ? item : `${item.name}（${item.alias}）`
                                ).join('、')}
                          </li>
                        ))}
                      </ul>
                    </section>
                  )}

                  {/* 解读步骤 */}
                  {guideData.interpretation_steps && (
                    <section>
                      <h4>{guideData.interpretation_steps.title}</h4>
                      <ol>
                        {guideData.interpretation_steps.steps.map((step: string, idx: number) => (
                          <li key={idx}>{step}</li>
                        ))}
                      </ol>
                    </section>
                  )}
                </>
              ) : (
                <p>加载指南中...</p>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="qimen-form">
        <div className="form-description">
          <p>
            奇门遁甲是中国古代术数中的一种预测方法，需要输入准确的时间进行排盘。
            <button className="guide-button" onClick={() => setShowGuide(true)}>
              📖 查看使用指南
            </button>
          </p>
        </div>

        <div className="date-inputs">
          <div className="form-group">
            <label htmlFor="qm-year">年</label>
            <input
              type="number"
              id="qm-year"
              value={year}
              onChange={(e) => handleYearChange(e.target.value)}
              placeholder="例如：2024"
              disabled={loading}
              min="1900"
              max="2100"
            />
          </div>

          <div className="form-group">
            <label htmlFor="qm-month">月</label>
            <select
              id="qm-month"
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
            <label htmlFor="qm-day">日</label>
            <select
              id="qm-day"
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
            <label htmlFor="qm-hour">时辰</label>
            <select
              id="qm-hour"
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
          disabled={loading || !year || !month || !day || !hour}
        >
          {loading ? '排盘中...' : '开始排盘'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result-container">
          <div className="qimen-header">
            <h3>奇门遁甲排盘结果</h3>
            <div className="qimen-info">
              <p>时间：{result.date_time}</p>
              <p>节气：{result.term} / 元运：{result.yuan}</p>
              <p>遁式：{result.dun_type} / 局数：{result.ju_number}局</p>
            </div>
          </div>

          {renderJiuGong()}

          <div className="qimen-analysis">
            <h4>整体分析</h4>
            <div className="analysis-content">
              <div className="analysis-item">
                <strong>综合评价：</strong>
                <span>{result.zong_ping.overall}</span>
              </div>
              <div className="analysis-item">
                <strong>吉凶统计：</strong>
                <span>
                  吉格 {result.zong_ping.ji_count} 个，凶格 {result.zong_ping.xiong_count} 个
                </span>
              </div>
              <div className="analysis-item">
                <strong>最佳方位：</strong>
                <span>{result.zong_ping.best_gong_name}（{result.zong_ping.best_gong}宫）</span>
              </div>
              <div className="analysis-item">
                <strong>不利方位：</strong>
                <span>{result.zong_ping.worst_gong_name}（{result.zong_ping.worst_gong}宫）</span>
              </div>
              <div className="analysis-summary">
                <p>{result.zong_ping.summary}</p>
              </div>
              <div className="analysis-advice">
                <strong>建议：</strong>
                <p>{result.zong_ping.advice}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
