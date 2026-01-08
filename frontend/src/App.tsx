import { useState } from 'react';
import './App.css';
import { DivinationTab } from './components/DivinationTab';
import { BaziTab } from './components/BaziTab';
import { QimenTab } from './components/QimenTab';

type TabType = 'divination' | 'bazi' | 'qimen';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('divination');

  return (
    <div className="app-wrapper">
      <nav className="nav-bar">
        <div className="nav-container">
          <h1 className="nav-title">易学智慧</h1>
          <div className="nav-tabs">
            <button
              className={`nav-tab ${activeTab === 'divination' ? 'active' : ''}`}
              onClick={() => setActiveTab('divination')}
            >
              周易占卜
            </button>
            <button
              className={`nav-tab ${activeTab === 'bazi' ? 'active' : ''}`}
              onClick={() => setActiveTab('bazi')}
            >
              八字排盘
            </button>
            <button
              className={`nav-tab ${activeTab === 'qimen' ? 'active' : ''}`}
              onClick={() => setActiveTab('qimen')}
            >
              奇门遁甲
            </button>
          </div>
        </div>
      </nav>

      <div className="app-container">
        {activeTab === 'divination' && <DivinationTab />}
        {activeTab === 'bazi' && <BaziTab />}
        {activeTab === 'qimen' && <QimenTab />}
      </div>
    </div>
  );
}

export default App;
