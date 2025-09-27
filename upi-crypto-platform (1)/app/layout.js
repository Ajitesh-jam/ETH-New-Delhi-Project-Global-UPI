import "./globals.css"

export const metadata = {
  title: "CryptoPay - Global UPI Platform",
  description: "Pay from anywhere to anywhere in the world with lightning fast, secure transactions",
    generator: 'v0.app'
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
