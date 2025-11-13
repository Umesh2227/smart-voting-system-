# OTP Verification - Quick Setup Guide

## What's New?

Your voting system now includes **OTP (One-Time Password) verification** for enhanced security. Every vote must be verified with a 6-digit code sent to the voter's phone before confirmation.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**New Dependency**: `pyotp` - now included in requirements.txt

### 2. Run the Application
```bash
python code/main.py
```

The application will start on `http://localhost:5000`

### 3. Test the Voting Flow

#### Voter Registration:
1. Go to Home → Register as Voter
2. Fill in all details including **phone number** (required for OTP)
3. Submit registration

#### Voting with OTP:
1. Click "Vote Now" or go to `/voting`
2. Log in with Aadhar number
3. Select a candidate
4. You'll be asked to **Enter OTP** before confirming
5. Check your phone for the 6-digit code
6. Enter the OTP in the verification form
7. After verification, confirm your vote
8. Success!

## Voting Flow Diagram

```
┌─────────────────────┐
│   Registration      │
│   (+ Phone Number)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Voter Login      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Select Candidate    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐◄──── NEW STEP
│   Send OTP to Phone │      (OTP sent via SMS)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐◄──── NEW STEP
│ Enter 6-Digit OTP   │      (Voter verifies with phone)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Confirm Vote       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Vote Cast ✓       │
│  (SMS confirmation) │
└─────────────────────┘
```

## OTP Features

### Security
- ✅ 6-digit OTP (sent via SMS)
- ✅ 10-minute validity period
- ✅ Maximum 3 verification attempts
- ✅ Requires phone number in voter profile
- ✅ Session-based (server-side secure)

### User Experience
- ✅ Clear instructions on OTP page
- ✅ Numeric-only input validation
- ✅ Resend OTP option
- ✅ Mobile-friendly interface
- ✅ Informative error messages
- ✅ Back navigation option

### Fallback
- ✅ If SMS fails, OTP is displayed in message
- ✅ Voting can proceed with displayed OTP
- ✅ Non-blocking SMS failures

## Important Notes

### Phone Number Required
- Voter **must have a valid phone number** in their profile
- Phone number should be in Indian format (10 digits)
- Update phone number in `/update` if not provided during registration

### OTP SMS Service
- Uses **fast2sms** API for SMS delivery
- Messages sent within seconds
- Check spam/junk folder if OTP not received
- API key is pre-configured

### Session Timeout
- OTP valid for **10 minutes** only
- After 10 minutes, request a new OTP
- Voter has **3 attempts** to enter correct OTP

## Testing Without SMS (Development)

If SMS service is unavailable during testing:

1. Go to registration and register a voter
2. Start voting process
3. When redirected to OTP page, check the flash message
4. The OTP will be displayed in yellow warning message
5. Use that OTP to verify
6. Continue voting

## Troubleshooting

### Issue: "Valid phone number not found"
**Solution**: Update voter profile with phone number in `/update` route

### Issue: "OTP expired"
**Solution**: Request a new OTP (10-minute validity)

### Issue: "Invalid OTP" (after 3 attempts)
**Solution**: Request a new OTP and try again

### Issue: SMS not received
**Solution**: 
1. Check spam folder
2. Verify phone number is correct
3. Check internet connection
4. Use fallback OTP from flash message

### Issue: Import error for pyotp
**Solution**: Run `pip install -r requirements.txt`

## Configuration

### To Change OTP Parameters:
Edit `code/main.py` in the helper functions:

```python
# Change OTP length (currently 6 digits)
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))  # Change k=6 to desired length

# Change OTP validity (currently 600 seconds = 10 minutes)
if time.time() - otp_time > 600:  # Change 600 to desired seconds

# Change max attempts (currently 3)
if otp_attempts >= 3:  # Change 3 to desired max
```

## Files Modified

1. **requirements.txt** - Added pyotp dependency
2. **code/main.py** - Added OTP routes and functions
3. **code/templates/verify_otp.html** - NEW OTP verification form

## API Endpoints

### New Routes:
- `POST/GET /send_otp` - Initiate OTP sending
- `GET/POST /verify_otp` - OTP verification form and verification logic

### Modified Routes:
- `/select_candidate` - Now redirects to OTP instead of direct confirmation
- `/confirm_vote` - Now requires OTP verification

## Database

No database schema changes required. OTP is stored in:
- **Session storage** (server-side, temporary)
- Not persisted in database
- Automatically cleared after verification or expiry

## Support & Documentation

- Full implementation details: See `OTP_IMPLEMENTATION.md`
- Issue tracking: Check existing templates and routes
- Contact: For SMS API issues, check fast2sms dashboard

---

**Ready to vote with OTP security! 🔐**

For any issues, refer to the implementation guide or check the application logs.
