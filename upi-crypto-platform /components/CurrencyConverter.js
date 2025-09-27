"use client"

import { useState, useEffect } from "react"

export default function CurrencyConverter() {
  const [amount, setAmount] = useState("")
  const [fromCurrency, setFromCurrency] = useState("INR")
  const [toCurrency, setToCurrency] = useState("USD")
  const [convertedAmount, setConvertedAmount] = useState(null)
  const [exchangeRate, setExchangeRate] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  // Mock exchange rates (in a real app, you'd fetch from an API)
  const mockRates = {
    INR_USD: 0.012,
    USD_INR: 83.25,
    INR_EUR: 0.011,
    EUR_INR: 90.15,
    USD_EUR: 0.92,
    EUR_USD: 1.09,
  }

  const convertCurrency = async () => {
    if (!amount || amount <= 0) return

    setIsLoading(true)

    try {
      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 500))

      const rateKey = `${fromCurrency}_${toCurrency}`
      const rate = mockRates[rateKey] || 1

      setExchangeRate(rate)
      setConvertedAmount((Number.parseFloat(amount) * rate).toFixed(2))
    } catch (error) {
      console.error("Currency conversion error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (amount) {
      const debounceTimer = setTimeout(convertCurrency, 500)
      return () => clearTimeout(debounceTimer)
    } else {
      setConvertedAmount(null)
      setExchangeRate(null)
    }
  }, [amount, fromCurrency, toCurrency])

  return (
    <div className="form-container">
      <h2 style={{ textAlign: "center", marginBottom: "25px", color: "#78dbff", fontSize: "1.5rem" }}>
        Currency Converter
      </h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr auto 1fr",
          gap: "15px",
          alignItems: "end",
          marginBottom: "20px",
        }}
      >
        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">From</label>
          <select value={fromCurrency} onChange={(e) => setFromCurrency(e.target.value)} className="form-input">
            <option value="INR">INR (₹)</option>
            <option value="USD">USD ($)</option>
            <option value="EUR">EUR (€)</option>
          </select>
        </div>

        <div style={{ padding: "10px", color: "#78dbff", fontSize: "1.2rem" }}>⇄</div>

        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">To</label>
          <select value={toCurrency} onChange={(e) => setToCurrency(e.target.value)} className="form-input">
            <option value="USD">USD ($)</option>
            <option value="INR">INR (₹)</option>
            <option value="EUR">EUR (€)</option>
          </select>
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Amount</label>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="form-input"
          placeholder={`Enter amount in ${fromCurrency}`}
          min="0"
          step="0.01"
        />
      </div>

      {(convertedAmount || isLoading) && (
        <div
          style={{
            background: "rgba(120, 219, 255, 0.1)",
            padding: "20px",
            borderRadius: "12px",
            border: "1px solid rgba(120, 219, 255, 0.2)",
            textAlign: "center",
            marginTop: "20px",
          }}
        >
          {isLoading ? (
            <div>
              <div className="loading-spinner" style={{ margin: "0 auto 10px" }}></div>
              <p style={{ color: "#b0b0b0" }}>Converting...</p>
            </div>
          ) : (
            <div>
              <p style={{ fontSize: "1.8rem", fontWeight: "600", color: "#78dbff", margin: "0 0 10px 0" }}>
                {convertedAmount} {toCurrency}
              </p>
              <p style={{ color: "#e0e0e0", fontSize: "0.9rem" }}>
                1 {fromCurrency} = {exchangeRate} {toCurrency}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
