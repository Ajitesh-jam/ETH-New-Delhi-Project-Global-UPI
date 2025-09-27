"use client"

import { useState, useEffect } from "react"
import QRCode from "qrcode"

export default function ReceivePage() {
  const [formData, setFormData] = useState({
    accountNumber: "",
    ifscCode: "",
    accountHolderName: "",
    bankName: "",
  })
  const [qrCodeUrl, setQrCodeUrl] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const generateQRCode = async () => {
    if (!formData.accountNumber || !formData.ifscCode || !formData.accountHolderName) {
      alert("Please fill in all required fields")
      return
    }

    setIsGenerating(true)

    try {
      const qrData = JSON.stringify({
        type: "receive",
        accountNumber: formData.accountNumber,
        ifscCode: formData.ifscCode,
        accountHolderName: formData.accountHolderName,
        bankName: formData.bankName,
        timestamp: new Date().toISOString(),
      })

      const qrUrl = await QRCode.toDataURL(qrData, {
        width: 300,
        margin: 2,
        color: {
          dark: "#000000",
          light: "#FFFFFF",
        },
      })

      setQrCodeUrl(qrUrl)
    } catch (error) {
      console.error("Error generating QR code:", error)
      alert("Error generating QR code. Please try again.")
    } finally {
      setIsGenerating(false)
    }
  }

  if (!mounted) return null

  return (
    <div className="animated-bg">
      <main
        style={{
          minHeight: "100vh",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div className="fade-in-up" style={{ width: "100%", maxWidth: "600px" }}>
          {/* Header */}
          <header style={{ textAlign: "center", marginBottom: "40px" }}>
            <h1
              className="text-glow"
              style={{ fontSize: "clamp(2rem, 4vw, 3rem)", fontWeight: "700", marginBottom: "10px" }}
            >
              Receive USD
            </h1>
            <p style={{ color: "#b0b0b0", fontSize: "1.1rem" }}>Generate your payment QR code</p>
          </header>

          {!qrCodeUrl ? (
            /* Form Section */
            <div className="form-container fade-in-up delay-1">
              <h2 style={{ textAlign: "center", marginBottom: "30px", color: "#78dbff", fontSize: "1.5rem" }}>
                Enter Your Bank Details
              </h2>

              <div className="form-group">
                <label className="form-label">Account Holder Name *</label>
                <input
                  type="text"
                  name="accountHolderName"
                  value={formData.accountHolderName}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter full name as per bank records"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Account Number *</label>
                <input
                  type="text"
                  name="accountNumber"
                  value={formData.accountNumber}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter your account number"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">IFSC Code *</label>
                <input
                  type="text"
                  name="ifscCode"
                  value={formData.ifscCode}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter IFSC code (e.g., SBIN0001234)"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Bank Name</label>
                <input
                  type="text"
                  name="bankName"
                  value={formData.bankName}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter bank name (optional)"
                />
              </div>

              <button
                onClick={generateQRCode}
                disabled={isGenerating}
                className="crypto-button"
                style={{ width: "100%", marginTop: "20px" }}
              >
                {isGenerating ? (
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "10px" }}>
                    <div className="loading-spinner" style={{ width: "20px", height: "20px" }}></div>
                    Generating QR Code...
                  </div>
                ) : (
                  "🔗 Generate QR Code"
                )}
              </button>
            </div>
          ) : (
            /* QR Code Display */
            <div className="form-container fade-in-up">
              <div className="qr-container">
                <h2 style={{ color: "#78dbff", marginBottom: "20px", fontSize: "1.5rem" }}>Your Payment QR Code</h2>
                <p style={{ color: "#e0e0e0", marginBottom: "20px", fontSize: "1rem" }}>
                  Share this QR code to receive payments
                </p>

                <div className="qr-code">
                  <img
                    src={qrCodeUrl || "/placeholder.svg"}
                    alt="Payment QR Code"
                    style={{ maxWidth: "100%", height: "auto" }}
                  />
                </div>

                <div
                  style={{
                    marginTop: "20px",
                    padding: "20px",
                    background: "rgba(120, 219, 255, 0.1)",
                    borderRadius: "12px",
                    border: "1px solid rgba(120, 219, 255, 0.2)",
                  }}
                >
                  <h3 style={{ color: "#78dbff", marginBottom: "10px", fontSize: "1.2rem" }}>Account Details</h3>
                  <p style={{ color: "#e0e0e0", margin: "5px 0" }}>
                    <strong>Name:</strong> {formData.accountHolderName}
                  </p>
                  <p style={{ color: "#e0e0e0", margin: "5px 0" }}>
                    <strong>Account:</strong> {formData.accountNumber}
                  </p>
                  <p style={{ color: "#e0e0e0", margin: "5px 0" }}>
                    <strong>IFSC:</strong> {formData.ifscCode}
                  </p>
                  {formData.bankName && (
                    <p style={{ color: "#e0e0e0", margin: "5px 0" }}>
                      <strong>Bank:</strong> {formData.bankName}
                    </p>
                  )}
                </div>

                <button
                  onClick={() => {
                    setQrCodeUrl("")
                    setFormData({
                      accountNumber: "",
                      ifscCode: "",
                      accountHolderName: "",
                      bankName: "",
                    })
                  }}
                  className="crypto-button secondary"
                  style={{ width: "100%", marginTop: "20px" }}
                >
                  🔄 Generate New QR Code
                </button>
              </div>
            </div>
          )}

          {/* Back Button */}
          <div style={{ textAlign: "center", marginTop: "30px" }}>
            <a
              href="/"
              className="crypto-button"
              style={{ background: "rgba(255, 255, 255, 0.1)", textDecoration: "none" }}
            >
              ← Back to Home
            </a>
          </div>
        </div>
      </main>
    </div>
  )
}
