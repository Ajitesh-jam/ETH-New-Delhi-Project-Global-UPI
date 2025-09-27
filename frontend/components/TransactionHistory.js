"use client"

import { useState, useEffect } from "react"

export default function TransactionHistory() {
  const [transactions, setTransactions] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Load transaction history from localStorage
    const loadTransactions = () => {
      try {
        const stored = localStorage.getItem("cryptopay_transactions")
        if (stored) {
          setTransactions(JSON.parse(stored))
        }
      } catch (error) {
        console.error("Error loading transactions:", error)
      } finally {
        setIsLoading(false)
      }
    }

    loadTransactions()
  }, [])

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const getStatusColor = (status) => {
    switch (status) {
      case "success":
        return "#4CAF50"
      case "failed":
        return "#f44336"
      case "pending":
        return "#ff9800"
      default:
        return "#78dbff"
    }
  }

  if (isLoading) {
    return (
      <div className="form-container">
        <div style={{ textAlign: "center", padding: "40px" }}>
          <div className="loading-spinner"></div>
          <p style={{ marginTop: "20px", color: "#b0b0b0" }}>Loading transactions...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="form-container">
      <h2 style={{ textAlign: "center", marginBottom: "30px", color: "#78dbff", fontSize: "1.5rem" }}>
        Transaction History
      </h2>

      {transactions.length === 0 ? (
        <div style={{ textAlign: "center", padding: "40px" }}>
          <p style={{ color: "#b0b0b0", fontSize: "1.1rem" }}>No transactions yet</p>
          <p style={{ color: "#888", fontSize: "0.9rem", marginTop: "10px" }}>Your payment history will appear here</p>
        </div>
      ) : (
        <div style={{ maxHeight: "400px", overflowY: "auto" }}>
          {transactions.map((transaction, index) => (
            <div
              key={index}
              style={{
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                borderRadius: "12px",
                padding: "16px",
                marginBottom: "12px",
                transition: "all 0.3s ease",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  marginBottom: "10px",
                }}
              >
                <div>
                  <h3 style={{ color: "#e0e0e0", fontSize: "1.1rem", margin: "0 0 5px 0" }}>
                    {transaction.type === "sent"
                      ? `To: ${transaction.receiver.name}`
                      : `From: ${transaction.sender.name}`}
                  </h3>
                  <p style={{ color: "#b0b0b0", fontSize: "0.9rem", margin: 0 }}>{formatDate(transaction.timestamp)}</p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <p style={{ color: "#78dbff", fontSize: "1.2rem", fontWeight: "600", margin: "0 0 5px 0" }}>
                    ${transaction.amount}
                  </p>
                  <span
                    style={{
                      color: getStatusColor(transaction.status),
                      fontSize: "0.8rem",
                      fontWeight: "500",
                      textTransform: "uppercase",
                    }}
                  >
                    {transaction.status}
                  </span>
                </div>
              </div>

              {transaction.transactionId && (
                <p style={{ color: "#888", fontSize: "0.8rem", margin: "5px 0 0 0" }}>
                  ID: {transaction.transactionId}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
