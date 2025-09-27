// API route for payment processing
import { NextResponse } from "next/server"
import aiAgentService from "../../../services/aiAgentService"

export async function POST(request) {
  try {
    const transactionData = await request.json()

    // Validate required fields
    if (!transactionData.sender || !transactionData.receiver || !transactionData.amount) {
      return NextResponse.json({ error: "Missing required transaction data" }, { status: 400 })
    }

    // Validate transaction with AI agent
    const validation = await aiAgentService.validateTransaction(transactionData)

    if (!validation.valid) {
      return NextResponse.json(
        {
          error: "Transaction validation failed",
          details: validation.errors || [],
        },
        { status: 400 },
      )
    }

    // Process payment through AI agent
    const result = await aiAgentService.processPayment(transactionData)

    // Log transaction (in production, save to database)
    console.log("Payment processed:", {
      transactionId: result.transactionId,
      amount: transactionData.amount,
      status: result.status,
      timestamp: new Date().toISOString(),
    })

    return NextResponse.json(result)
  } catch (error) {
    console.error("Payment processing error:", error)

    return NextResponse.json(
      {
        error: "Payment processing failed",
        message: error.message || "Internal server error",
      },
      { status: 500 },
    )
  }
}

export async function GET(request) {
  // Health check endpoint
  try {
    const isHealthy = await aiAgentService.healthCheck()

    return NextResponse.json({
      status: "ok",
      aiAgent: isHealthy ? "connected" : "disconnected",
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    return NextResponse.json({ status: "error", message: error.message }, { status: 500 })
  }
}
