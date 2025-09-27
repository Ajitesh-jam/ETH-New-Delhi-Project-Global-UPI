"use client"

import { useState, useEffect, useRef } from "react"
import jsQR from "jsqr"
import aiAgentService from "../../services/aiAgentService"
import { saveTransaction, validateAccountNumber, validateIFSC } from "../../utils/transactionUtils"
import NotificationToast from "../../components/NotificationToast"

export default function PayPage() {
  const [mounted, setMounted] = useState(false)
  const [cameraActive, setCameraActive] = useState(false)
  const [scannedData, setScannedData] = useState(null)
  const [showPaymentForm, setShowPaymentForm] = useState(false)
  const [paymentData, setPaymentData] = useState({
    senderName: "",
    senderAccount: "",
    senderIFSC: "",
    amount: "",
    purpose: "",
  })
  const [isProcessing, setIsProcessing] = useState(false)
  const [showResult, setShowResult] = useState(null)
  const [notification, setNotification] = useState(null)
  const [validationErrors, setValidationErrors] = useState({})

  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const scanIntervalRef = useRef(null)

  useEffect(() => {
    setMounted(true)
    return () => {
      stopCamera()
    }
  }, [])

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
      })

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        setCameraActive(true)

        // Start scanning for QR codes
        scanIntervalRef.current = setInterval(scanQRCode, 500)
      }
    } catch (error) {
      console.error("Error accessing camera:", error)
      alert("Unable to access camera. Please ensure camera permissions are granted.")
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
    if (scanIntervalRef.current) {
      clearInterval(scanIntervalRef.current)
      scanIntervalRef.current = null
    }
    setCameraActive(false)
  }

  const scanQRCode = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      const context = canvas.getContext("2d")

      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0, canvas.width, canvas.height)

        const imageData = context.getImageData(0, 0, canvas.width, canvas.height)
        const code = jsQR(imageData.data, imageData.width, imageData.height)

        if (code) {
          try {
            const qrData = JSON.parse(code.data)
            if (qrData.type === "receive") {
              setScannedData(qrData)
              setShowPaymentForm(true)
              stopCamera()
            }
          } catch (error) {
            console.error("Invalid QR code format:", error)
          }
        }
      }
    }
  }

  const handlePaymentInputChange = (e) => {
    const { name, value } = e.target
    setPaymentData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const validateForm = () => {
    const errors = {}

    if (!paymentData.senderName.trim()) {
      errors.senderName = "Name is required"
    }

    if (!validateAccountNumber(paymentData.senderAccount)) {
      errors.senderAccount = "Invalid account number"
    }

    if (!validateIFSC(paymentData.senderIFSC)) {
      errors.senderIFSC = "Invalid IFSC code format"
    }

    if (!paymentData.amount || Number.parseFloat(paymentData.amount) <= 0) {
      errors.amount = "Valid amount is required"
    } else if (Number.parseFloat(paymentData.amount) > 10000) {
      errors.amount = "Amount exceeds maximum limit of $10,000"
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const processPayment = async () => {
    if (!validateForm()) {
      setNotification({
        message: "Please fix the form errors before proceeding",
        type: "error",
      })
      return
    }

    setIsProcessing(true)

    try {
      // Prepare transaction data for AI agent
      const transactionData = {
        sender: {
          name: paymentData.senderName,
          account: paymentData.senderAccount,
          ifsc: paymentData.senderIFSC,
        },
        receiver: {
          name: scannedData.accountHolderName,
          account: scannedData.accountNumber,
          ifsc: scannedData.ifscCode,
          bank: scannedData.bankName,
        },
        amount: Number.parseFloat(paymentData.amount),
        purpose: paymentData.purpose || "Payment",
        currency: "USD",
        timestamp: new Date().toISOString(),
      }

      const response = await aiAgentService.processPayment(transactionData)

      // Save transaction to local storage
      const savedTransaction = saveTransaction({
        ...transactionData,
        transactionId: response.transactionId,
        status: response.status,
        type: "sent",
        fees: response.fees || 0,
      })

      if (response.success) {
        setShowResult({
          type: "success",
          message: response.message,
          transactionId: response.transactionId,
          details: {
            ...transactionData,
            fees: response.fees,
            estimatedTime: response.estimatedTime,
          },
        })

        setNotification({
          message: `Payment of $${paymentData.amount} sent successfully!`,
          type: "success",
        })
      } else {
        setShowResult({
          type: "error",
          message: response.message,
          details: null,
        })

        setNotification({
          message: "Payment failed. Please try again.",
          type: "error",
        })
      }
    } catch (error) {
      console.error("Payment processing error:", error)
      setShowResult({
        type: "error",
        message: "Network error. Please check your connection and try again.",
        details: null,
      })

      setNotification({
        message: "Connection error. Please try again.",
        type: "error",
      })
    } finally {
      setIsProcessing(false)
    }
  }

  const resetPayment = () => {
    setScannedData(null)
    setShowPaymentForm(false)
    setPaymentData({
      senderName: "",
      senderAccount: "",
      senderIFSC: "",
      amount: "",
      purpose: "",
    })
    setShowResult(null)
    setNotification(null)
    setValidationErrors({})
  }

  if (!mounted) return null

  return (
    <div style={{ backgroundColor: "#ffffff", minHeight: "100vh" }}>
      {/* Notification Toast */}
      {notification && (
        <NotificationToast
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}

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
                backgroundColor: "#1a73e8",
                borderRadius: "16px",
                margin: "0 auto 16px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "24px",
              }}
            >
              💸
            </div>
            <h1
              style={{
                fontSize: "24px",
                fontWeight: "400",
                marginBottom: "8px",
                color: "#202124",
              }}
            >
              Send Money
            </h1>
            <p style={{ color: "#5f6368", fontSize: "14px" }}>Scan QR code to send payment</p>
          </header>

          {/* Result Display */}
          {showResult && (
            <div className="modal-overlay" onClick={() => setShowResult(null)}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className={showResult.type === "success" ? "success-popup" : "error-popup"}>
                  <h2 style={{ fontSize: "18px", marginBottom: "12px", fontWeight: "500" }}>
                    {showResult.type === "success" ? "Payment Successful!" : "Payment Failed"}
                  </h2>
                  <p style={{ fontSize: "14px", marginBottom: "16px" }}>{showResult.message}</p>

                  {showResult.details && (
                    <div className="simple-card" style={{ marginBottom: "16px", textAlign: "left" }}>
                      <h3 style={{ marginBottom: "8px", color: "#202124", fontSize: "14px", fontWeight: "500" }}>
                        Transaction Details:
                      </h3>
                      <p style={{ fontSize: "12px", margin: "4px 0" }}>
                        <strong>ID:</strong> {showResult.transactionId}
                      </p>
                      <p style={{ fontSize: "12px", margin: "4px 0" }}>
                        <strong>Amount:</strong> ${showResult.details.amount}
                      </p>
                      <p style={{ fontSize: "12px", margin: "4px 0" }}>
                        <strong>To:</strong> {showResult.details.receiver.name}
                      </p>
                      {showResult.details.fees > 0 && (
                        <p style={{ fontSize: "12px", margin: "4px 0" }}>
                          <strong>Fees:</strong> ${showResult.details.fees.toFixed(2)}
                        </p>
                      )}
                    </div>
                  )}

                  <button
                    onClick={() => {
                      setShowResult(null)
                      resetPayment()
                    }}
                    className="pay-button"
                  >
                    {showResult.type === "success" ? "Make Another Payment" : "Try Again"}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Payment Form */}
          {showPaymentForm && scannedData && (
            <div className="form-container">
              <h2
                style={{
                  textAlign: "center",
                  marginBottom: "16px",
                  color: "#202124",
                  fontSize: "18px",
                  fontWeight: "500",
                }}
              >
                Payment Details
              </h2>

              {/* Receiver Info */}
              <div className="simple-card" style={{ marginBottom: "20px" }}>
                <h3 style={{ color: "#202124", marginBottom: "8px", fontSize: "14px", fontWeight: "500" }}>
                  Paying To:
                </h3>
                <p style={{ color: "#5f6368", margin: "4px 0", fontSize: "12px" }}>
                  <strong>Name:</strong> {scannedData.accountHolderName}
                </p>
                <p style={{ color: "#5f6368", margin: "4px 0", fontSize: "12px" }}>
                  <strong>Account:</strong> {scannedData.accountNumber}
                </p>
                <p style={{ color: "#5f6368", margin: "4px 0", fontSize: "12px" }}>
                  <strong>IFSC:</strong> {scannedData.ifscCode}
                </p>
              </div>

              {/* Sender Form */}
              <div className="form-group">
                <label className="form-label">Your Name</label>
                <input
                  type="text"
                  name="senderName"
                  value={paymentData.senderName}
                  onChange={handlePaymentInputChange}
                  className="form-input"
                  placeholder="Enter your full name"
                  required
                  style={{ borderColor: validationErrors.senderName ? "#ea4335" : "" }}
                />
                {validationErrors.senderName && (
                  <p style={{ color: "#ea4335", fontSize: "12px", marginTop: "4px" }}>{validationErrors.senderName}</p>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Your Account Number</label>
                <input
                  type="text"
                  name="senderAccount"
                  value={paymentData.senderAccount}
                  onChange={handlePaymentInputChange}
                  className="form-input"
                  placeholder="Enter account number"
                  required
                  style={{ borderColor: validationErrors.senderAccount ? "#ea4335" : "" }}
                />
                {validationErrors.senderAccount && (
                  <p style={{ color: "#ea4335", fontSize: "12px", marginTop: "4px" }}>
                    {validationErrors.senderAccount}
                  </p>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Your IFSC Code</label>
                <input
                  type="text"
                  name="senderIFSC"
                  value={paymentData.senderIFSC}
                  onChange={handlePaymentInputChange}
                  className="form-input"
                  placeholder="Enter IFSC code"
                  required
                  style={{ borderColor: validationErrors.senderIFSC ? "#ea4335" : "" }}
                />
                {validationErrors.senderIFSC && (
                  <p style={{ color: "#ea4335", fontSize: "12px", marginTop: "4px" }}>{validationErrors.senderIFSC}</p>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Amount (USD)</label>
                <input
                  type="number"
                  name="amount"
                  value={paymentData.amount}
                  onChange={handlePaymentInputChange}
                  className="form-input"
                  placeholder="Enter amount"
                  min="0.01"
                  step="0.01"
                  required
                  style={{ borderColor: validationErrors.amount ? "#ea4335" : "" }}
                />
                {validationErrors.amount && (
                  <p style={{ color: "#ea4335", fontSize: "12px", marginTop: "4px" }}>{validationErrors.amount}</p>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Purpose (Optional)</label>
                <input
                  type="text"
                  name="purpose"
                  value={paymentData.purpose}
                  onChange={handlePaymentInputChange}
                  className="form-input"
                  placeholder="Payment purpose"
                />
              </div>

              <div style={{ display: "flex", gap: "12px", marginTop: "20px" }}>
                <button
                  onClick={resetPayment}
                  style={{
                    flex: 1,
                    padding: "12px",
                    background: "#ffffff",
                    border: "1px solid #dadce0",
                    borderRadius: "8px",
                    color: "#5f6368",
                    fontSize: "14px",
                    cursor: "pointer",
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={processPayment}
                  disabled={isProcessing}
                  className="pay-button secondary"
                  style={{ flex: 1 }}
                >
                  {isProcessing ? (
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                      <div className="loading-spinner"></div>
                      Processing...
                    </div>
                  ) : (
                    "Pay Now"
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Camera Section */}
          {!showPaymentForm && (
            <div className="form-container">
              <h2
                style={{
                  textAlign: "center",
                  marginBottom: "20px",
                  color: "#202124",
                  fontSize: "18px",
                  fontWeight: "500",
                }}
              >
                Scan QR Code
              </h2>

              {!cameraActive ? (
                <div style={{ textAlign: "center" }}>
                  <p style={{ color: "#5f6368", marginBottom: "20px", fontSize: "14px" }}>
                    Click to start camera and scan a payment QR code
                  </p>
                  <button onClick={startCamera} className="pay-button">
                    Start Camera
                  </button>
                </div>
              ) : (
                <div className="camera-container">
                  <video ref={videoRef} className="camera-video" autoPlay playsInline muted />
                  <div className="camera-overlay"></div>
                  <canvas ref={canvasRef} style={{ display: "none" }} />

                  <div style={{ textAlign: "center", marginTop: "16px" }}>
                    <p style={{ color: "#5f6368", marginBottom: "12px", fontSize: "12px" }}>
                      Position the QR code within the frame
                    </p>
                    <button
                      onClick={stopCamera}
                      style={{
                        padding: "8px 16px",
                        background: "#ffffff",
                        border: "1px solid #dadce0",
                        borderRadius: "8px",
                        color: "#5f6368",
                        fontSize: "12px",
                        cursor: "pointer",
                      }}
                    >
                      Stop Camera
                    </button>
                  </div>
                </div>
              )}
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
