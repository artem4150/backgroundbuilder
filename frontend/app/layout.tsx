import "./globals.css";
export const metadata = { title: "Состав — конструктор иллюстраций" };
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
