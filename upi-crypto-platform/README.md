# CryptoPay - Global UPI Platform

A modern, dark-themed cryptocurrency payment platform built with Next.js that enables global UPI-style transactions with AI-powered processing.

## Features

- 🌍 **Global Payments**: Send money from INR to USD anywhere in the world
- ⚡ **Lightning Fast**: Instant transactions with minimal latency
- 🔒 **Secure**: Bank-grade security with end-to-end encryption
- 💰 **Low Fees**: Very low transaction fees for international transfers
- 📱 **QR Code Integration**: Scan QR codes for seamless payments
- 🤖 **AI-Powered**: Intelligent transaction processing with Python AI agent
- 📊 **Real-time Tracking**: Live transaction status and history
- 🎨 **Modern UI**: Dark theme with smooth animations and responsive design

## Tech Stack

- **Frontend**: Next.js 14 (JavaScript)
- **Styling**: Custom CSS (no Tailwind)
- **QR Code**: qrcode library for generation, jsQR for scanning
- **AI Integration**: Python AI agent via REST API
- **Storage**: LocalStorage for transaction history
- **Camera**: WebRTC for QR code scanning

## Getting Started

### Prerequisites

- Node.js 18+ 
- Your Python AI agent running (optional for development)

### Installation

1. Clone the repository
\`\`\`bash
git clone <your-repo-url>
cd upi-crypto-platform
\`\`\`

2. Install dependencies
\`\`\`bash
npm install
\`\`\`

3. Set up environment variables (optional)
\`\`\`bash
# Create .env.local file
NEXT_PUBLIC_AI_AGENT_URL=http://localhost:8000
NEXT_PUBLIC_AI_AGENT_KEY=your-api-key
\`\`\`

4. Run the development server
\`\`\`bash
npm run dev
\`\`\`

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## AI Agent Integration

### Python AI Agent Setup

Your Python AI agent should expose these endpoints:

\`\`\`python
# POST /api/process-payment
# Processes payment transactions
{
  "transaction": {
    "sender": { "name": "...", "account": "...", "ifsc": "..." },
    "receiver": { "name": "...", "account": "...", "ifsc": "..." },
    "amount": 100.00,
    "currency": "USD"
  }
}

# Response
{
  "success": true,
  "transaction_id": "TXN123456789",
  "status": "success",
  "message": "Payment processed successfully",
  "fees": 2.00,
  "estimated_time": "2-3 minutes"
}
\`\`\`

\`\`\`python
# POST /api/validate-transaction
# Validates transaction data
{
  "sender": {...},
  "receiver": {...},
  "amount": 100.00
}

# Response
{
  "valid": true,
  "warnings": [],
  "risk_score": "low"
}
\`\`\`

\`\`\`python
# GET /api/exchange-rate?from=INR&to=USD
# Gets current exchange rates
{
  "rate": 0.012,
  "last_updated": "2024-01-01T00:00:00Z"
}
\`\`\`

### Fallback Mode

If your AI agent is not available, the platform will:
- Use mock responses for development
- Show appropriate error messages
- Maintain full UI functionality

## Project Structure

\`\`\`
├── app/
│   ├── api/           # API routes
│   ├── pay/           # Payment page
│   ├── receive/       # Receive page
│   └── page.js        # Landing page
├── components/        # Reusable components
├── services/          # AI agent service
├── utils/            # Utility functions
└── public/           # Static assets
\`\`\`

## Key Components

- **Landing Page**: Main entry point with payment options
- **Pay Page**: Camera-based QR code scanning and payment processing
- **Receive Page**: Bank details input and QR code generation
- **AI Agent Service**: Handles communication with Python AI agent
- **Transaction Utils**: Payment validation and history management

## Customization

### Styling
All styles are in `app/globals.css` - no external CSS frameworks used.

### AI Agent URL
Update `NEXT_PUBLIC_AI_AGENT_URL` in your environment variables.

### Payment Limits
Modify validation rules in `utils/transactionUtils.js`.

## Deployment

### Vercel (Recommended)
\`\`\`bash
npm run build
# Deploy to Vercel
\`\`\`

### Docker
\`\`\`dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
\`\`\`

## Security Considerations

- Input validation on all forms
- HTTPS required for camera access
- Environment variables for sensitive data
- Transaction amount limits
- IFSC code format validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the GitHub issues
- Review the AI agent integration guide
- Ensure camera permissions are granted
- Verify environment variables are set correctly
