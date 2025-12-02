import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-amber-700 to-amber-800 text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold text-center">周易 AI 解卦</h1>
          <p className="text-center text-amber-200 mt-2">诚心求问，易理指引</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-amber-800 text-amber-200 py-4 mt-8">
        <div className="container mx-auto px-4 text-center text-sm">
          <p>周易 AI 解卦系统 | 仅供参考，请理性对待</p>
        </div>
      </footer>
    </div>
  );
}
