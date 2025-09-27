"use client"

import { useEffect, useState } from "react"
import Link from "next/link"

export default function Home() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div style={{ backgroundColor: "#ffffff", minHeight: "100vh" }}>
      <main
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "20px",
          maxWidth: "400px",
          margin: "0 auto",
        }}
      >
        {/* Header */}
        <header style={{ textAlign: "center", marginBottom: "48px" }} className="fade-in">
          <div
            style={{
              width: "80px",
              height: "80px",
              backgroundColor: "#1a73e8",
              borderRadius: "20px",
              margin: "0 auto 24px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "32px",
            }}
          >
            💳
          </div>
          <h1
            style={{
              fontSize: "28px",
              fontWeight: "400",
              marginBottom: "8px",
              color: "#202124",
            }}
          >
            GlobalPay
          </h1>
          <p
            style={{
              fontSize: "16px",
              color: "#5f6368",
              marginBottom: "16px",
            }}
          >
            Pay from anywhere to anywhere in the world
          </p>
          <p
            style={{
              fontSize: "14px",
              color: "#1a73e8",
              fontWeight: "500",
            }}
          >
            Secure • Fast • Low fees
          </p>
        </header>

        {/* Main Actions */}
        <section
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "16px",
            width: "100%",
            marginBottom: "32px",
          }}
          className="fade-in"
        >
          <Link href="/pay" className="pay-button">
            Send Money (INR → USD)
          </Link>

          <Link href="/receive" className="pay-button secondary">
            Receive Money (USD)
          </Link>
        </section>

        {/* Simple Info */}
        <div
          style={{
            textAlign: "center",
            padding: "24px",
            backgroundColor: "#f8f9fa",
            borderRadius: "12px",
            width: "100%",
          }}
          className="fade-in"
        >
          <p
            style={{
              fontSize: "14px",
              color: "#5f6368",
              lineHeight: "1.4",
            }}
          >
            Lightning fast transactions with very low fees. Secure and reliable global payments.
          </p>
        </div>
      </main>
    </div>
  )
}
