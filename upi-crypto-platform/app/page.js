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
    <div className="animated-bg">
      <main
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "20px",
        }}
      >
        {/* Header */}
        <header style={{ textAlign: "center", marginBottom: "60px" }}>
          <h1
            className="fade-in-up text-glow"
            style={{ fontSize: "clamp(2.5rem, 5vw, 4rem)", fontWeight: "800", marginBottom: "20px" }}
          >
            CryptoPay
          </h1>
          <p
            className="fade-in-up delay-1"
            style={{ fontSize: "clamp(1.2rem, 2.5vw, 1.5rem)", color: "#b0b0b0", marginBottom: "10px" }}
          >
            Global UPI Platform
          </p>
          <div
            className="fade-in-up delay-2"
            style={{ fontSize: "clamp(1rem, 2vw, 1.2rem)", color: "#78dbff", fontWeight: "500" }}
          >
            "Pay from anywhere to anywhere in the world"
          </div>
        </header>

        {/* Features */}
        <section
          className="fade-in-up delay-2"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "20px",
            maxWidth: "900px",
            width: "100%",
            marginBottom: "60px",
          }}
        >
          <div className="feature-card">
            <h3 style={{ color: "#78dbff", marginBottom: "10px", fontSize: "1.2rem" }}>⚡ Lightning Fast</h3>
            <p style={{ color: "#e0e0e0", fontSize: "0.95rem" }}>
              Instant transactions across the globe with minimal latency
            </p>
          </div>
          <div className="feature-card">
            <h3 style={{ color: "#78dbff", marginBottom: "10px", fontSize: "1.2rem" }}>🔒 Secure</h3>
            <p style={{ color: "#e0e0e0", fontSize: "0.95rem" }}>Bank-grade security with end-to-end encryption</p>
          </div>
          <div className="feature-card">
            <h3 style={{ color: "#78dbff", marginBottom: "10px", fontSize: "1.2rem" }}>💰 Low Fees</h3>
            <p style={{ color: "#e0e0e0", fontSize: "0.95rem" }}>
              Very low transaction fees for international transfers
            </p>
          </div>
        </section>

        {/* Main Actions */}
        <section
          className="fade-in-up delay-3"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "30px",
            width: "100%",
            maxWidth: "400px",
          }}
        >
          <div style={{ textAlign: "center", marginBottom: "20px" }}>
            <h2 style={{ fontSize: "1.8rem", marginBottom: "10px", color: "#ffffff" }}>Choose Your Action</h2>
            <p style={{ color: "#b0b0b0", fontSize: "1rem" }}>Send or receive money globally with ease</p>
          </div>

          <Link href="/pay" className="crypto-button" style={{ width: "100%" }}>
            💸 Pay (INR → USD)
          </Link>

          <Link href="/receive" className="crypto-button secondary" style={{ width: "100%" }}>
            📥 Receive (USD)
          </Link>
        </section>

        {/* Footer Quote */}
        <footer className="fade-in-up delay-3" style={{ marginTop: "80px", textAlign: "center" }}>
          <p style={{ fontSize: "1.1rem", color: "#78dbff", fontStyle: "italic", opacity: "0.8" }}>
            "Revolutionizing global payments with blockchain technology"
          </p>
        </footer>
      </main>
    </div>
  )
}
