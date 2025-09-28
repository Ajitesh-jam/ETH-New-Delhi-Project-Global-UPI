import { NextResponse } from "next/server"

export async function POST(request) {
  try {
    const { message } = await request.json()

    // Get your AI agent URL from environment variables
    const AI_AGENT_URL = "http://0.0.0.0:8001"

    if (!AI_AGENT_URL) {
      console.log("[v0] AI_AGENT_URL not configured, using mock response")
      // Mock response for development when the agent server isn't running
      return NextResponse.json({
        response: getMockResponse(message),
        status: "success",
      })
    }

    // --- Step 1: Send the initial request to start the agent process ---
    console.log("[v0] Sending initial request to AI agent at:", `${AI_AGENT_URL}/api/send-request`)
    const startResponse = await fetch(`${AI_AGENT_URL}/api/send-request`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      // The payload our Python server expects
      body: JSON.stringify({ query: message }),
    })

    if (!startResponse.ok) {
      throw new Error(`AI Agent start request failed with status: ${startResponse.status}`)
    }

    const startData = await startResponse.json()
    const { request_id } = startData

    if (!request_id) {
      throw new Error("AI Agent did not return a valid request_id.")
    }

    console.log(`[v0] Task started with request_id: ${request_id}`)

    // --- Step 2: Poll for the result using the request_id ---
    const maxAttempts = 15 // Max 15 attempts
    const pollInterval = 2000 // 2 seconds between attempts (total timeout ~30s)

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      // Wait for the specified interval before the next poll
      await new Promise(resolve => setTimeout(resolve, pollInterval))

      console.log(`[v0] Polling for result... (Attempt ${attempt + 1})`)
      const pollResponse = await fetch(`${AI_AGENT_URL}/api/get-response/${request_id}`)

      if (pollResponse.ok) {
        const pollData = await pollResponse.json()
        
        // If the agent is done, send the final response and exit
        if (pollData.status === "complete") {
          console.log("[v0] AI agent final response received")
          return NextResponse.json({
            response: pollData.analysis_result || "Process complete, but no response content.",
            status: "success",
          })
        }
        // If status is "waiting", the loop will continue to the next attempt
      } else {
        // If a poll request fails, we'll log it but continue trying
        console.warn(`[v0] Polling request failed with status: ${pollResponse.status}`)
      }
    }
    
    // If the loop completes without a "complete" status, the request has timed out
    throw new Error("Request timed out. The agent took too long to respond.")

  } catch (error) {
    console.error("[v0] Chat API error:", error)
    return NextResponse.json(
      {
        response: "I'm experiencing some technical difficulties right now. Please try again in a moment.",
        status: "error",
        error: error.message,
      },
      { status: 500 },
    )
  }
}

// Mock responses for development/testing (No changes needed here)
function getMockResponse(message) {
  const lowerMessage = message.toLowerCase()
  if (lowerMessage.includes("payment")) {
    return "I can help with payments! What do you need?"
  }
  if (lowerMessage.includes("rate")) {
    return "The current exchange rate is competitive. How much would you like to convert?"
  }
  return "Hello! How can I assist you with GlobalPay today?"
}