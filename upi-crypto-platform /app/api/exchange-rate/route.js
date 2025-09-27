// API route for exchange rates
import { NextResponse } from "next/server"
import aiAgentService from "../../../services/aiAgentService"

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)
    const fromCurrency = searchParams.get("from") || "INR"
    const toCurrency = searchParams.get("to") || "USD"

    const exchangeData = await aiAgentService.getExchangeRate(fromCurrency, toCurrency)

    return NextResponse.json({
      from: fromCurrency,
      to: toCurrency,
      rate: exchangeData.rate,
      lastUpdated: exchangeData.lastUpdated,
      source: "ai-agent",
    })
  } catch (error) {
    console.error("Exchange rate error:", error)

    return NextResponse.json(
      {
        error: "Failed to fetch exchange rate",
        message: error.message,
      },
      { status: 500 },
    )
  }
}
