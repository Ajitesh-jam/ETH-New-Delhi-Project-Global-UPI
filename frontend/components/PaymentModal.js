"use client"

import { useState } from "react"

export default function PaymentModal({ isOpen, onClose, type, data, onConfirm }) {
  const [isProcessing, setIsProcessing] = useState(false)

  if (!isOpen) return null

  const handleConfirm = async () => {
    setIsProcessing(true)
    try {
      await onConfirm()
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ textAlign: "center" }}>
          <h2 style={{ fontSize: "1.8rem", marginBottom: "20px", color: "#78dbff" }}>
            {type === "confirm" ? "Confirm Payment" : "Payment Status"}
          </h2>

          {type === "confirm" && data && (
            <div>
              <div
                style={{
                  background: "rgba(120, 219, 255, 0.1)",
                  padding: "20px",
                  borderRadius: "12px",
                  marginBottom: "25px",
                  border: "1px solid rgba(120, 219, 255, 0.2)",
                }}
              >
                <h3 style={{ color: "#78dbff", marginBottom: "15px", fontSize: "1.3rem" }}>Transaction Summary</h3>
                <div style={{ textAlign: "left", color: "#e0e0e0" }}>
                  <p style={{ margin: "8px 0" }}>
                    <strong>Amount:</strong> ${data.amount}
                  </p>
                  <p style={{ margin: "8px 0" }}>
                    <strong>From:</strong> {data.sender.name}
                  </p>
                  <p style={{ margin: "8px 0" }}>
                    <strong>To:</strong> {data.receiver.name}
                  </p>
                  <p style={{ margin: "8px 0" }}>
                    <strong>Purpose:</strong> {data.purpose || "Payment"}
                  </p>
                </div>
              </div>

              <div
                style={{
                  background: "rgba(255, 193, 7, 0.1)",
                  padding: "15px",
                  borderRadius: "8px",
                  marginBottom: "25px",
                  border: "1px solid rgba(255, 193, 7, 0.3)",
                }}
              >
                <p style={{ color: "#ffc107", fontSize: "0.95rem", margin: 0 }}>
                  ⚠️ Please verify all details before confirming. This transaction cannot be reversed.
                </p>
              </div>

              <div style={{ display: "flex", gap: "15px" }}>
                <button
                  onClick={onClose}
                  className="crypto-button"
                  style={{ flex: 1, background: "rgba(255, 255, 255, 0.1)" }}
                  disabled={isProcessing}
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirm}
                  className="crypto-button secondary"
                  style={{ flex: 1 }}
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "10px" }}>
                      <div className="loading-spinner" style={{ width: "20px", height: "20px" }}></div>
                      Processing...
                    </div>
                  ) : (
                    "Confirm Payment"
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
