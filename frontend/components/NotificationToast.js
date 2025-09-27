"use client"

import { useState, useEffect } from "react"

export default function NotificationToast({ message, type, duration = 5000, onClose }) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(onClose, 300) // Wait for fade out animation
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, onClose])

  if (!isVisible) return null

  const getToastStyle = () => {
    const baseStyle = {
      position: "fixed",
      top: "20px",
      right: "20px",
      padding: "16px 20px",
      borderRadius: "12px",
      color: "white",
      fontWeight: "500",
      fontSize: "0.95rem",
      zIndex: 1001,
      minWidth: "300px",
      maxWidth: "400px",
      boxShadow: "0 10px 25px rgba(0, 0, 0, 0.3)",
      animation: isVisible ? "slideInRight 0.3s ease-out" : "slideOutRight 0.3s ease-in",
      display: "flex",
      alignItems: "center",
      gap: "12px",
    }

    switch (type) {
      case "success":
        return { ...baseStyle, background: "linear-gradient(135deg, #4CAF50, #45a049)" }
      case "error":
        return { ...baseStyle, background: "linear-gradient(135deg, #f44336, #d32f2f)" }
      case "warning":
        return { ...baseStyle, background: "linear-gradient(135deg, #ff9800, #f57c00)" }
      default:
        return { ...baseStyle, background: "linear-gradient(135deg, #667eea, #764ba2)" }
    }
  }

  const getIcon = () => {
    switch (type) {
      case "success":
        return "✅"
      case "error":
        return "❌"
      case "warning":
        return "⚠️"
      default:
        return "ℹ️"
    }
  }

  return (
    <>
      <style jsx>{`
        @keyframes slideInRight {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        
        @keyframes slideOutRight {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(100%);
            opacity: 0;
          }
        }
      `}</style>

      <div style={getToastStyle()}>
        <span style={{ fontSize: "1.2rem" }}>{getIcon()}</span>
        <span style={{ flex: 1 }}>{message}</span>
        <button
          onClick={() => {
            setIsVisible(false)
            setTimeout(onClose, 300)
          }}
          style={{
            background: "none",
            border: "none",
            color: "white",
            fontSize: "1.2rem",
            cursor: "pointer",
            padding: "0",
            opacity: "0.7",
            transition: "opacity 0.2s",
          }}
          onMouseEnter={(e) => (e.target.style.opacity = "1")}
          onMouseLeave={(e) => (e.target.style.opacity = "0.7")}
        >
          ×
        </button>
      </div>
    </>
  )
}
