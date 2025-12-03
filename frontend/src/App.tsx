import { LanguageProvider } from './contexts/LanguageContext';
import { Divination } from './pages/Divination';

function App() {
  return (
    <LanguageProvider>
      <Divination />
    </LanguageProvider>
  );
}

export default App;
