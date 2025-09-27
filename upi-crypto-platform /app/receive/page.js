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
    <div style={{ backgroundColor: "#ffffff", minHeight: "100vh" }}>
      <main
        style={{
          minHeight: "100vh",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          maxWidth: "400px",
          margin: "0 auto",
        }}
      >
        <div className="fade-in" style={{ width: "100%" }}>
          {/* Header */}
          <header style={{ textAlign: "center", marginBottom: "32px" }}>
            <div
              style={{
                width: "60px",
                height: "60px",
                backgroundColor: "#34a853",
                borderRadius: "16px",
                margin: "0 auto 16px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "24px",
              }}
            >
              📥
            </div>
            <h1
              style={{
                fontSize: "24px",
                fontWeight: "400",
                marginBottom: "8px",
                color: "#202124",
              }}
            >
              Receive Money
            </h1>
            <p style={{ color: "#5f6368", fontSize: "14px" }}>Generate your payment QR code</p>
          </header>

          {!qrCodeUrl ? (
            /* Form Section */
            <div className="form-container">
              <div className="form-group">
                <label className="form-label">Account Holder Name</label>
                <input
                  type="text"
                  name="accountHolderName"
                  value={formData.accountHolderName}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter full name"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Account Number</label>
                <input
                  type="text"
                  name="accountNumber"
                  value={formData.accountNumber}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter account number"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">IFSC Code</label>
                <input
                  type="text"
                  name="ifscCode"
                  value={formData.ifscCode}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter IFSC code"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Bank Name (Optional)</label>
                <input
                  type="text"
                  name="bankName"
                  value={formData.bankName}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter bank name"
                />
              </div>

              <button
                onClick={generateQRCode}
                disabled={isGenerating}
                className="pay-button secondary"
                style={{ marginTop: "16px" }}
              >
                {isGenerating ? (
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                    <div className="loading-spinner"></div>
                    Generating...
                  </div>
                ) : (
                  "Generate QR Code"
                )}
              </button>
            </div>
          ) : (
            /* QR Code Display */
            <div className="form-container">
              <div className="qr-container">
                <h2 style={{ color: "#202124", marginBottom: "16px", fontSize: "18px", fontWeight: "500" }}>
                  Your Payment QR Code
                </h2>
                <p style={{ color: "#5f6368", marginBottom: "20px", fontSize: "14px" }}>
                  Share this QR code to receive payments
                </p>

                <div className="qr-code">
                  <img
                    src={qrCodeUrl || "/placeholder.svg"}
                    alt="Payment QR Code"
                    style={{ maxWidth: "100%", height: "auto" }}
                  />
                </div>

                <div className="simple-card" style={{ marginTop: "20px", textAlign: "left" }}>
                  <h3 style={{ color: "#202124", marginBottom: "12px", fontSize: "16px", fontWeight: "500" }}>
                    Account Details
                  </h3>
                  <p style={{ color: "#5f6368", margin: "4px 0", fontSize: "14px" }}>
                    <strong>Name:</strong> {formData.accountHolderName}
                  </p>
                  <p style={{ color: "#5f6368", margin: "4px 0", fontSize: "14px" }}>
                    <strong>Account:</strong> {formData.accountNumber}
                  </p>
                  <p style={{ color: "#5f6368", margin: "4px 0", fontSize: "14px" }}>
                    <strong>IFSC:</strong> {formData.ifscCode}
                  </p>
                  {formData.bankName && (
                    <p style={{ color: "#5f6368", margin: "4px 0", fontSize: "14px" }}>
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
                  className="pay-button"
                  style={{ marginTop: "20px" }}
                >
                  Generate New QR Code
                </button>
              </div>
            </div>
          )}

          {/* Back Button */}
          <div style={{ textAlign: "center", marginTop: "24px" }}>
            <a
              href="/"
              style={{
                color: "#1a73e8",
                textDecoration: "none",
                fontSize: "14px",
                fontWeight: "500",
              }}
            >
              ← Back to Home
            </a>
          </div>
        </div>
      </main>
    </div>
  )
}
