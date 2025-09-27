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
    <div className="animated-bg">
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
        }}
      >
        <div className="fade-in-up" style={{ width: "100%", maxWidth: "600px" }}>
          {/* Header */}
          <header style={{ textAlign: "center", marginBottom: "40px" }}>
            <h1
              className="text-glow"
              style={{ fontSize: "clamp(2rem, 4vw, 3rem)", fontWeight: "700", marginBottom: "10px" }}
            >
              Pay (INR → USD)
            </h1>
            <p style={{ color: "#b0b0b0", fontSize: "1.1rem" }}>Scan QR code to send payment</p>
          </header>

          {/* Result Display */}
          {showResult && (
            <div className="modal-overlay" onClick={() => setShowResult(null)}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className={showResult.type === "success" ? "success-popup" : "error-popup"}>
                  <h2 style={{ fontSize: "1.5rem", marginBottom: "15px" }}>
                    {showResult.type === "success" ? "✅ Payment Successful!" : "❌ Payment Failed"}
                  </h2>
                  <p style={{ fontSize: "1.1rem", marginBottom: "20px" }}>{showResult.message}</p>

                  {showResult.details && (
                    <div
                      style={{
                        background: "rgba(255, 255, 255, 0.1)",
                        padding: "15px",
                        borderRadius: "8px",
                        marginBottom: "20px",
                        textAlign: "left",
                      }}
                    >
                      <h3 style={{ marginBottom: "10px", color: "#78dbff" }}>Transaction Details:</h3>
                      <p>
                        <strong>Transaction ID:</strong> {showResult.transactionId}
                      </p>
                      <p>
                        <strong>Amount:</strong> ${showResult.details.amount}
                      </p>
                      <p>
                        <strong>To:</strong> {showResult.details.receiver.name}
                      </p>
                      <p>
                        <strong>From:</strong> {showResult.details.sender.name}
                      </p>
                      {showResult.details.fees > 0 && (
                        <p>
                          <strong>Fees:</strong> ${showResult.details.fees.toFixed(2)}
                        </p>
                      )}
                      {showResult.details.estimatedTime && (
                        <p>
                          <strong>Processing Time:</strong> {showResult.details.estimatedTime}
                        </p>
                      )}
                    </div>
                  )}

                  <button
                    onClick={() => {
                      setShowResult(null)
                      resetPayment()
                    }}
                    className="crypto-button"
                    style={{ width: "100%" }}
                  >
                    {showResult.type === "success" ? "Make Another Payment" : "Try Again"}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Payment Form */}
          {showPaymentForm && scannedData && (
            <div className="form-container fade-in-up">
              <h2 style={{ textAlign: "center", marginBottom: "20px", color: "#78dbff", fontSize: "1.5rem" }}>
                Payment Details
              </h2>

              {/* Receiver Info */}
              <div
                style={{
                  background: "rgba(120, 219, 255, 0.1)",
                  padding: "15px",
                  borderRadius: "12px",
                  marginBottom: "25px",
                  border: "1px solid rgba(120, 219, 255, 0.2)",
                }}
              >
                <h3 style={{ color: "#78dbff", marginBottom: "10px", fontSize: "1.2rem" }}>Paying To:</h3>
                <p style={{ color: "#e0e0e0", margin: "5px 0" }}>
                  <strong>Name:</strong> {scannedData.accountHolderName}
                </p>
                <p style={{ color: "#e0e0e0", margin: "5px 0" }}>
                  <strong>Account:</strong> {scannedData.accountNumber}
                </p>
                <p style={{ color: "#e0e0e0", margin: "5px 0" }}>
                  <strong>IFSC:</strong> {scannedData.ifscCode}
                </p>
              </div>

              {/* Sender Form with Validation */}
              <div className="form-group">
                <label className="form-label">Your Name *</label>
                <input
                  type="text"
                  name="senderName"
                  value={paymentData.senderName}
                  onChange={handlePaymentInputChange}
                  className="form-input"
                  placeholder="Enter your full name"
                  required
                  style={{ borderColor: validationErrors.senderName ? "#f44336" : "" }}
                />
                {validationErrors.senderName && (
                  <p style={{ color: "#f44336", fontSize: "0.8rem", marginTop: "5px" }}>
                    {validationErrors.senderName}
                  </p>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Your Account Number *</label>
                <input
                  type="text"
                  name="senderAccount"
                  value={paymentData.senderAccount}
                  onChange={handlePaymentInputChange}
                  className="form-input"
                  placeholder="Enter your account number"
                  required
                  style={{ borderColor: validationErrors.senderAccount ? "#f44336" : "" }}
                />
                {validationErrors.senderAccount && (
                  <p style={{ color: "#f44336", fontSize: "0.8rem", marginTop: "5px" }}>
                    {validationErrors.senderAccount}
                  </p>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Your IFSC Code *</label>
                <input
                  type="text"
                  name="senderIFSC"
                  value={paymentData.senderIFSC}
                  onChange={handlePaymentInputChange}
                  className="form-input"
                  placeholder="Enter your IFSC code"
                  required
                  style={{ borderColor: validationErrors.senderIFSC ? "#f44336" : "" }}
                />
                {validationErrors.senderIFSC && (
                  <p style={{ color: "#f44336", fontSize: "0.8rem", marginTop: "5px" }}>
                    {validationErrors.senderIFSC}
                  </p>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Amount (USD) *</label>
                <input
                  type="number"
                  name="amount"
                  value={paymentData.amount}
                  onChange={handlePaymentInputChange}
                  className="form-input"
                  placeholder="Enter amount in USD"
                  min="0.01"
                  step="0.01"
                  required
                  style={{ borderColor: validationErrors.amount ? "#f44336" : "" }}
                />
                {validationErrors.amount && (
                  <p style={{ color: "#f44336", fontSize: "0.8rem", marginTop: "5px" }}>{validationErrors.amount}</p>
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

              <div style={{ display: "flex", gap: "15px", marginTop: "25px" }}>
                <button
                  onClick={resetPayment}
                  className="crypto-button"
                  style={{ flex: 1, background: "rgba(255, 255, 255, 0.1)" }}
                >
                  Cancel
                </button>
                <button
                  onClick={processPayment}
                  disabled={isProcessing}
                  className="crypto-button secondary"
                  style={{ flex: 1 }}
                >
                  {isProcessing ? (
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "10px" }}>
                      <div className="loading-spinner" style={{ width: "20px", height: "20px" }}></div>
                      Processing...
                    </div>
                  ) : (
                    "💳 Pay Now"
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Camera Section */}
          {!showPaymentForm && (
            <div className="form-container fade-in-up delay-1">
              <h2 style={{ textAlign: "center", marginBottom: "25px", color: "#78dbff", fontSize: "1.5rem" }}>
                Scan QR Code
              </h2>

              {!cameraActive ? (
                <div style={{ textAlign: "center" }}>
                  <p style={{ color: "#e0e0e0", marginBottom: "25px", fontSize: "1rem" }}>
                    Click the button below to start your camera and scan a payment QR code
                  </p>
                  <button onClick={startCamera} className="crypto-button" style={{ width: "100%" }}>
                    📷 Start Camera
                  </button>
                </div>
              ) : (
                <div className="camera-container">
                  <video ref={videoRef} className="camera-video" autoPlay playsInline muted />
                  <div className="camera-overlay"></div>
                  <canvas ref={canvasRef} style={{ display: "none" }} />

                  <div style={{ textAlign: "center", marginTop: "20px" }}>
                    <p style={{ color: "#78dbff", marginBottom: "15px", fontSize: "1rem" }}>
                      Position the QR code within the frame
                    </p>
                    <button
                      onClick={stopCamera}
                      className="crypto-button"
                      style={{ background: "rgba(255, 255, 255, 0.1)" }}
                    >
                      Stop Camera
                    </button>
                  </div>
                </div>
              )}
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
