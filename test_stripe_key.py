#!/usr/bin/env python
"""
Simple Stripe API test
Run this to verify your Stripe keys work correctly
"""

import stripe
import sys

def test_stripe_key(secret_key):
    """Test if a Stripe secret key is valid and active"""
    
    if not secret_key:
        print("❌ No secret key provided")
        return False
        
    if not (secret_key.startswith('sk_test_') or secret_key.startswith('sk_live_')):
        print("❌ Invalid key format. Should start with sk_test_ or sk_live_")
        return False
        
    # Set the key
    stripe.api_key = secret_key
    
    key_type = "LIVE" if secret_key.startswith('sk_live_') else "TEST"
    print(f"Testing {key_type} key: {secret_key[:12]}...")
    
    try:
        # Test 1: Retrieve account info
        account = stripe.Account.retrieve()
        print(f"✅ Account connection successful")
        print(f"   Account ID: {account.id}")
        print(f"   Country: {account.country}")
        print(f"   Charges enabled: {account.charges_enabled}")
        print(f"   Payouts enabled: {account.payouts_enabled}")
        
        if not account.charges_enabled:
            print(f"⚠️  WARNING: Account cannot accept charges yet")
            return False
            
        # Test 2: Try creating a test checkout session  
        test_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Test Product'},
                    'unit_amount': 1000,  # $10.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
        )
        
        print(f"✅ Checkout session creation successful")
        print(f"   Session ID: {test_session.id}")
        print(f"   Payment status: {test_session.payment_status}")
        
        return True
        
    except stripe.AuthenticationError as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("   Check that your secret key is correct")
        return False
        
    except stripe.PermissionError as e:
        print(f"❌ Permission denied: {str(e)}")  
        print("   Your account may not be fully activated")
        return False
        
    except Exception as e:
        print(f"❌ Stripe API error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("=== STRIPE API KEY TESTER ===")
    print()
    
    # Test with command line argument or prompt
    if len(sys.argv) > 1:
        secret_key = sys.argv[1]
    else:
        secret_key = input("Enter your Stripe secret key: ").strip()
    
    if test_stripe_key(secret_key):
        print()
        print("🎉 SUCCESS! Your Stripe key is working correctly.")
        print("   The checkout API should work with this key.")
    else:
        print()
        print("💥 FAILED! There's an issue with your Stripe configuration.")
        print("   Check the Stripe dashboard or contact Stripe support.")
        
    print()
    print("Next steps:")
    print("1. Set STRIPE_API_KEY environment variable in production")
    print("2. Restart your Django application") 
    print("3. Test the marketplace checkout process")