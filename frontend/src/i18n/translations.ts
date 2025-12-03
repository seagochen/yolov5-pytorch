export type Language = 'zh-CN' | 'zh-TW' | 'ja' | 'en';

export interface Translations {
  // Header
  divinationMethod: string;
  computerDivination: string;
  coinDivination: string;
  yarrowDivination: string;
  language: string;

  // Question Input
  questionPlaceholder: string;
  startDivination: string;

  // Loading
  divining: string;

  // Results
  originalGua: string;
  changedGua: string;
  guaName: string;

  // Interpretation
  interpretationPrompt: string;
  interpretationButton: string;

  // Common
  reset: string;
}

export const translations: Record<Language, Translations> = {
  'zh-CN': {
    divinationMethod: '起卦方式',
    computerDivination: '电脑起卦',
    coinDivination: '铜钱起卦',
    yarrowDivination: '蓍草起卦',
    language: '语言',

    questionPlaceholder: '请输入您的问题或想法...',
    startDivination: '开始占卜',

    divining: '解卦中',

    originalGua: '本卦',
    changedGua: '变卦',
    guaName: '卦象',

    interpretationPrompt: '想知道是什么意思吗？',
    interpretationButton: '查看解释',

    reset: '重新占卜',
  },
  'zh-TW': {
    divinationMethod: '起卦方式',
    computerDivination: '電腦起卦',
    coinDivination: '銅錢起卦',
    yarrowDivination: '蓍草起卦',
    language: '語言',

    questionPlaceholder: '請輸入您的問題或想法...',
    startDivination: '開始占卜',

    divining: '解卦中',

    originalGua: '本卦',
    changedGua: '變卦',
    guaName: '卦象',

    interpretationPrompt: '想知道是什麼意思嗎？',
    interpretationButton: '查看解釋',

    reset: '重新占卜',
  },
  'ja': {
    divinationMethod: '占い方法',
    computerDivination: 'コンピューター占い',
    coinDivination: '銅銭占い',
    yarrowDivination: '筮竹占い',
    language: '言語',

    questionPlaceholder: 'あなたの質問や考えを入力してください...',
    startDivination: '占いを始める',

    divining: '解卦中',

    originalGua: '本卦',
    changedGua: '変卦',
    guaName: '卦象',

    interpretationPrompt: 'どういう意味か知りたいですか？',
    interpretationButton: '解釈を見る',

    reset: '再占い',
  },
  'en': {
    divinationMethod: 'Method',
    computerDivination: 'Computer',
    coinDivination: 'Coins',
    yarrowDivination: 'Yarrow',
    language: 'Language',

    questionPlaceholder: 'Enter your question or thoughts...',
    startDivination: 'Start Divination',

    divining: 'Divining',

    originalGua: 'Original',
    changedGua: 'Changed',
    guaName: 'Hexagram',

    interpretationPrompt: 'Want to know what it means?',
    interpretationButton: 'View Interpretation',

    reset: 'Reset',
  },
};

export const languageNames: Record<Language, string> = {
  'zh-CN': '简体中文',
  'zh-TW': '繁體中文',
  'ja': '日本語',
  'en': 'English',
};
