import os
import json
import pyotp
from SmartApi import SmartConnect

# GitHub Secrets se credentials read karna
api_key = os.environ.get("ANGEL_API_KEY")
client_id = os.environ.get("ANGEL_CLIENT_ID")
pwd = os.environ.get("ANGEL_PIN")
totp_secret = os.environ.get("ANGEL_TOTP_SECRET")

def run_trading_bot():
    try:
        # Automated 2FA TOTP generate karna
        totp = pyotp.TOTP(totp_secret).now()
        
        # SmartAPI Instance
        smart_api = SmartConnect(api_key=api_key)
        
        # Login Process
        data = smart_api.generateSession(client_id, pwd, totp)
        
        if data['status']:
            print("Successfully Logged in to Angel One SmartAPI!")
            auth_token = data['data']['jwtToken']
            feed_token = smart_api.getfeedToken()
            
            # Yahan par F&O / Options Data, Order Block aur FVG calculation logical logic chalega
            # Abhi ke liye test payload output ready karte hain:
            output_data = {
                "status": "success",
                "message": "Institutional Dashboard Backend Active",
                "timestamp": str(data.get("servertime", ""))
            }
            
            # Data ko JSON format mein save karna (frontend starpulse.in ke liye)
            with open("data.json", "w") as f:
                json.dump(output_data, f, indent=4)
                
            print("data.json successfully generated!")
        else:
            print(f"Login Failed: {data.get('message')}")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    run_trading_bot()
