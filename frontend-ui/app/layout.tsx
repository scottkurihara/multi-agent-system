import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Multi-Agent System',
  description: 'Interactive frontend for the multi-agent system',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0 }}>{children}</body>
    </html>
  );
}
