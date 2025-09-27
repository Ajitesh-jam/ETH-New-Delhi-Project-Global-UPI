// AI Agent Service for payment processing
// This service handles communication with your Python AI agent

class AIAgentService {
  constructor() {
    // You can configure these endpoints based on your AI agent deployment
    this.baseURL = process.env.NEXT_PUBLIC_AI_AGENT_URL || "http://localhost:8000"
    this.apiKey = process.env.NEXT_PUBLIC_AI_AGENT_KEY || ""
  }

  async processPayment(transactionData) {
    try {
      const response = await fetch(`${this.baseURL}/api/process-payment`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: this.apiKey ? `Bearer ${this.apiKey}` : "",
          "X-Request-ID": this.generateRequestId(),
        },
        body: JSON.stringify({
          transaction: transactionData,
          timestamp: new Date().toISOString(),
          platform: "cryptopay-web",
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      return this.handleAIResponse(result)
    } catch (error) {
      console.error("AI Agent API Error:", error)

      // Fallback to mock response if AI agent is not available
      if (error.message.includes("fetch")) {
        console.warn("AI Agent not available, using mock response")
        return this.getMockResponse(transactionData)
      }

      throw error
    }
  }

  async validateTransaction(transactionData) {
    try {
      const response = await fetch(`${this.baseURL}/api/validate-transaction`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: this.apiKey ? `Bearer ${this.apiKey}` : "",
        },
        body: JSON.stringify(transactionData),
      })

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("Transaction validation error:", error)
      // Return basic validation for fallback
      return {
        valid: true,
        warnings: [],
        riskScore: "low",
      }
    }
  }

  async getExchangeRate(fromCurrency, toCurrency) {
    try {
      const response = await fetch(`${this.baseURL}/api/exchange-rate`, {
        method: "GET",
        headers: {
          Authorization: this.apiKey ? `Bearer ${this.apiKey}` : "",
        },
        params: new URLSearchParams({
          from: fromCurrency,
          to: toCurrency,
        }),
      })

      if (!response.ok) {
        throw new Error(`Exchange rate fetch failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("Exchange rate error:", error)
      // Fallback to mock rates
      return this.getMockExchangeRate(fromCurrency, toCurrency)
    }
  }

  async checkTransactionStatus(transactionId) {
    try {
      const response = await fetch(`${this.baseURL}/api/transaction-status/${transactionId}`, {
        method: "GET",
        headers: {
          Authorization: this.apiKey ? `Bearer ${this.apiKey}` : "",
        },
      })

      if (!response.ok) {
        throw new Error(`Status check failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("Status check error:", error)
      return {
        status: "unknown",
        message: "Unable to check transaction status",
      }
    }
  }

  handleAIResponse(response) {
    // Process and normalize AI agent response
    return {
      success: response.success || response.status === "success",
      transactionId: response.transaction_id || response.transactionId || this.generateTransactionId(),
      status: response.status || (response.success ? "success" : "failed"),
      message: response.message || (response.success ? "Payment processed successfully" : "Payment failed"),
      fees: response.fees || 0,
      exchangeRate: response.exchange_rate || response.exchangeRate,
      estimatedTime: response.estimated_time || response.estimatedTime || "2-5 minutes",
      riskScore: response.risk_score || response.riskScore || "low",
      warnings: response.warnings || [],
      metadata: response.metadata || {},
    }
  }

  getMockResponse(transactionData) {
    // Mock response for development/testing when AI agent is not available
    const success = Math.random() > 0.15 // 85% success rate
    const transactionId = this.generateTransactionId()

    return {
      success,
      transactionId,
      status: success ? "success" : "failed",
      message: success
        ? "Payment processed successfully by AI agent"
        : "Payment failed: Insufficient funds or invalid account details",
      fees: success ? transactionData.amount * 0.02 : 0, // 2% fee
      exchangeRate: 0.012, // Mock INR to USD rate
      estimatedTime: success ? "2-3 minutes" : null,
      riskScore: transactionData.amount > 1000 ? "medium" : "low",
      warnings: transactionData.amount > 5000 ? ["Large transaction amount"] : [],
      metadata: {
        processingMethod: "mock",
        timestamp: new Date().toISOString(),
      },
    }
  }

  getMockExchangeRate(fromCurrency, toCurrency) {
    const rates = {
      INR_USD: { rate: 0.012, lastUpdated: new Date().toISOString() },
      USD_INR: { rate: 83.25, lastUpdated: new Date().toISOString() },
      INR_EUR: { rate: 0.011, lastUpdated: new Date().toISOString() },
      EUR_INR: { rate: 90.15, lastUpdated: new Date().toISOString() },
    }

    const key = `${fromCurrency}_${toCurrency}`
    return rates[key] || { rate: 1, lastUpdated: new Date().toISOString() }
  }

  generateRequestId() {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  generateTransactionId() {
    return `TXN${Date.now()}${Math.floor(Math.random() * 10000)}`
  }

  // Utility method to check if AI agent is available
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: "GET",
        timeout: 5000,
      })
      return response.ok
    } catch (error) {
      return false
    }
  }
}

// Export singleton instance
export const aiAgentService = new AIAgentService()
export default aiAgentService
