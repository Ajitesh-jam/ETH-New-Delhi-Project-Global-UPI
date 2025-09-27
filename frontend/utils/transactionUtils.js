// Utility functions for transaction management

export const saveTransaction = (transactionData) => {
  try {
    const existing = JSON.parse(localStorage.getItem("cryptopay_transactions") || "[]")
    const newTransaction = {
      ...transactionData,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
    }

    existing.unshift(newTransaction) // Add to beginning

    // Keep only last 50 transactions
    if (existing.length > 50) {
      existing.splice(50)
    }

    localStorage.setItem("cryptopay_transactions", JSON.stringify(existing))
    return newTransaction
  } catch (error) {
    console.error("Error saving transaction:", error)
    return null
  }
}

export const getTransactions = () => {
  try {
    return JSON.parse(localStorage.getItem("cryptopay_transactions") || "[]")
  } catch (error) {
    console.error("Error loading transactions:", error)
    return []
  }
}

export const validateAccountNumber = (accountNumber) => {
  // Basic validation for account number
  const cleaned = accountNumber.replace(/\s/g, "")
  return cleaned.length >= 9 && cleaned.length <= 18 && /^\d+$/.test(cleaned)
}

export const validateIFSC = (ifsc) => {
  // IFSC format: 4 letters + 7 digits
  const ifscRegex = /^[A-Z]{4}0[A-Z0-9]{6}$/
  return ifscRegex.test(ifsc.toUpperCase())
}

export const formatCurrency = (amount, currency = "USD") => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

export const generateTransactionId = () => {
  const timestamp = Date.now()
  const random = Math.floor(Math.random() * 10000)
  return `TXN${timestamp}${random}`
}

export const maskAccountNumber = (accountNumber) => {
  if (!accountNumber || accountNumber.length < 4) return accountNumber
  const visible = accountNumber.slice(-4)
  const masked = "*".repeat(accountNumber.length - 4)
  return masked + visible
}

export const getTransactionStatus = (transaction) => {
  // Mock status logic - in real app, this would check with backend
  const now = new Date()
  const transactionTime = new Date(transaction.timestamp)
  const timeDiff = now - transactionTime

  // Simulate processing time
  if (timeDiff < 30000) {
    // Less than 30 seconds
    return "pending"
  } else if (transaction.amount > 1000 && Math.random() < 0.1) {
    return "failed" // 10% failure rate for large amounts
  } else {
    return "success"
  }
}
