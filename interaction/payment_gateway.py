import razorpay
import os
import uuid
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

KEY_ID = os.getenv("RAZORPAY_KEY_ID")
KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

if not KEY_ID or not KEY_SECRET:
    raise ValueError("Razorpay credentials (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET) are not set in environment variables.")


try:
    client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
except Exception as e:
    logging.error(f"Failed to initialize Razorpay client: {e}")
    client = None

def initiate_and_confirm_upi_payment(amount_inr: float, description: str = "Payment Request", timeout_seconds: int = 180) -> dict:

    if not client:
        return {'status': 'error', 'message': 'Razorpay client not initialized.'}

    if not isinstance(amount_inr, (int, float)) or amount_inr <= 0:
        return {'status': 'error', 'message': 'Invalid amount. Must be a positive number.'}

    amount_in_paise = int(amount_inr * 100)

    try:
        payment_link_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "accept_partial": False,
            "description": description,
            "reference_id": f"agent_{uuid.uuid4().hex[:10]}"
        }
        logging.info(f"Creating payment link for INR {amount_inr:.2f}")
        link = client.payment_link.create(payment_link_data)
        payment_link_id = link['id']
        payment_url = link['short_url']

        print(f"\n--- ACTION REQUIRED ---\n"
              f"Please complete the test payment by visiting this URL:\n"
              f"{payment_url}\n"
              f"-----------------------\n")
        
        start_time = time.time()
        logging.info(f"Waiting for payment confirmation for link {payment_link_id}. Timeout: {timeout_seconds}s")
        
        while time.time() - start_time < timeout_seconds:
            link_status = client.payment_link.fetch(payment_link_id)
            
            if link_status['status'] == 'paid':
               
                payment_id = link_status.get('payments', [{}])[0].get('payment_id', None)
                logging.info(f"Payment successful! Status: 'paid'. Payment ID: {payment_id}")
                return {
                    'status': 'success',
                    'message': 'Payment confirmed successfully.',
                    'payment_id': payment_id,
                    'amount_paid': link_status['amount_paid'] / 100
                }
            elif link_status['status'] == 'expired':
                logging.warning("Payment link expired before payment was made.")
                return {'status': 'error', 'message': 'Payment link expired.'}
            
            
            time.sleep(5)
        
        logging.warning(f"Timeout reached. Payment was not completed in {timeout_seconds} seconds.")
        return {'status': 'error', 'message': 'Payment not completed within the time limit.'}

    except Exception as e:
        logging.error(f"Razorpay API Error: {e}")
        return {'status': 'error', 'message': str(e)}


def send_bank_transfer(amount_inr: float, recipient_details: dict) -> dict:
   
    if not client:
        return {'status': 'error', 'message': 'Razorpay client not initialized.'}
    required_keys = ['name', 'email', 'account_number', 'ifsc']
    if not all(key in recipient_details for key in required_keys):
        return {'status': 'error', 'message': f'Recipient details missing one of: {required_keys}'}
    if not isinstance(amount_inr, (int, float)) or amount_inr <= 0:
        return {'status': 'error', 'message': 'Invalid amount. Must be a positive number.'}
    amount_in_paise = int(amount_inr * 100)
    try:
        logging.info(f"Creating contact for {recipient_details['name']}")
        contact = client.contact.create({'name': recipient_details['name'],'email': recipient_details['email'],'contact': '9999999999','type': 'employee'})
        contact_id = contact['id']
        logging.info(f"Creating fund account for {contact_id}")
        fund_account = client.fund_account.create({'contact_id': contact_id,'account_type': 'bank_account','bank_account': {'name': recipient_details['name'],'ifsc': recipient_details['ifsc'],'account_number': recipient_details['account_number']}})
        fund_account_id = fund_account['id']
        logging.info(f"Initiating payout of INR {amount_inr:.2f} to {fund_account_id}")
        payout = client.payout.create({"account_number": KEY_ID,"fund_account_id": fund_account_id,"amount": amount_in_paise,"currency": "INR","mode": "IMPS","purpose": "agent_transfer","queue_if_low_balance": True,"reference_id": f"agent_payout_{uuid.uuid4().hex[:10]}","narration": "Payment from AI Agent"})
        return {'status': 'success','payout_id': payout['id'],'payout_status': payout['status']}
    except Exception as e:
        logging.error(f"Razorpay API Error during bank transfer: {e}")
        return {'status': 'error', 'message': str(e)}


# if __name__ == "__main__":
#     print("--- Running Payment Function Examples ---")


#     print("\n[1] Requesting a payment of INR 10.00 and waiting for confirmation...")
#     request_result = initiate_and_confirm_upi_payment(amount_inr=10.00, description="Test Payment Confirmation", timeout_seconds=60)
#     print(f"    Final Result: {request_result}")
    
#     if request_result['status'] == 'success':
#         print(f"   Agent can now proceed, payment {request_result['payment_id']} is confirmed.")
#     else:
#         print(f" Agent should handle the failure: {request_result['message']}")

#     print("\n" + "-"*40 + "\n")

#     print("[2] Sending a bank transfer of INR 50.75...")
#     beneficiary_info = {
#         'name': 'Test Beneficiary',
#         'email': 'test.beneficiary@example.com',
#         'account_number': '2323230000000001',
#         'ifsc': 'UTIB0000000'
#     }
#     transfer_result = send_bank_transfer(amount_inr=50.75, recipient_details=beneficiary_info)
#     print(f"    Result: {transfer_result}")
#     if transfer_result['status'] == 'success':
#         print(f"Payout successfully initiated with ID: {transfer_result['payout_id']}")