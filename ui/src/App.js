import React from "react";

function App() {
  const startPayment = async () => {
    try {
      const orderRes = await fetch("http://localhost:8080/create-order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount: 400, currency: "INR", receipt: "receipt-13" }),
      });

      const orderData = await orderRes.json();
      if (!orderRes.ok || !orderData?.success) {
        console.error("Failed to create order:", orderData);
        alert(orderData?.message || "Failed to create order");
        return;
      }

      const order = orderData.order || {};

      const key = process.env.REACT_APP_RAZORPAY_KEY_ID;
      if (!key) {
        alert("Razorpay key is not found");
        return;
      }

      if (!window.Razorpay) {
        alert("Razorpay script not loaded. Check index.html includes the checkout script.");
        return;
      }
      const amountPaise = Math.round(order.amount * 100);
      const options = {
        key,
        amount: amountPaise,
        currency: order.currency,
        name: "Crypto",
        description: "Test Transaction",
        order_id: order.id,
        handler: async function (response) {
          const verifyRes = await fetch("http://localhost:8080/verify-payment", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(response),
          });
          const verifyData = await verifyRes.json();
          alert("Payment Status: " + (verifyData?.status || "unknown"));
        },
        
 
  
        prefill: {
          name: "Test User",
          email: "test@example.com",
          contact: "9999999999",
          vpa: "axl@upi"
        },
        method: {
    netbanking: true,
    card: true,
    upi: true,
        wallet: true,
      },
        theme: { color: "#3399cc" },
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (err) {
      console.error("Payment init error:", err);
      alert("Something went wrong starting the payment.");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Razorpay Payment Demo</h1>
      <button onClick={startPayment}>Pay ₹500</button>
    </div>
  );
}

export default App;
