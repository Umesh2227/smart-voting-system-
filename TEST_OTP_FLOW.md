# OTP Verification Flow Test Guide

## Quick Test Steps

### Step 1: Start the Application
```bash
cd c:\Users\manju\OneDrive\Attachments\Desktop\Smart-Voting-System-main (1)\Smart-Voting-System-main
python code/main.py
```

The app will start at: **http://localhost:5000**

---

### Step 2: Register as Voter (if not already registered)

1. Go to Home page
2. Click "Register as Voter" 
3. Fill in details:
   - **Aadhar ID**: 123456789012 (or unique number)
   - **First Name**: Test
   - **Last Name**: Voter
   - **Phone**: 9999999999 (Important! Must be 10 digits)
   - **Email**: test@example.com
   - **Age**: 25
4. Click Submit
5. You'll see "Registration successful"

---

### Step 3: Login

1. Go to "Vote Now"
2. Enter **Aadhar ID**: 123456789012
3. Click Submit
4. You'll see candidates list

---

### Step 4: Select Candidate (THIS TRIGGERS OTP)

1. You'll see a list of candidates
2. **Click on a candidate name**
3. Click "Next" button
4. **You should now see the OTP verification page** ← This is what you're testing!

If you see the OTP page, the feature is **WORKING** ✅

---

### Step 5: Enter OTP

On the OTP page:
- You'll see a message saying OTP was sent to your phone
- If SMS failed, you'll see the OTP code displayed (e.g., "OTP: 123456")
- Enter the 6-digit code in the input field
- Click "Verify OTP"

---

### Step 6: Confirm Vote

1. You'll be taken to the Confirm Vote page
2. You'll see the candidate details
3. Click "Confirm Vote"
4. Vote is recorded!

---

## 🔍 Troubleshooting

### I don't see the OTP page after selecting candidate

**Check these:**

1. **Phone number missing?**
   - Go back to home
   - Click "Update Profile"
   - Enter a 10-digit phone number
   - Try voting again

2. **No flash messages appearing?**
   - Clear browser cache
   - Restart Flask application
   - Try again

3. **Error message?**
   - Check Flask console for error details
   - Phone number must be exactly 10 digits

---

## 📱 Testing with Different Scenarios

### Scenario 1: SMS Works (Best Case)
- Phone receives SMS with OTP
- User enters OTP code from SMS
- Vote confirmed

### Scenario 2: SMS Fails (Fallback)
- User sees message: "OTP generated but SMS could not be sent. OTP: 123456"
- User enters the displayed OTP code
- Vote confirmed

### Scenario 3: Wrong OTP (Security Test)
- User enters wrong code
- System shows: "Invalid OTP. 2 attempts remaining"
- User can try 2 more times
- After 3 wrong attempts, must request new OTP

### Scenario 4: OTP Expires (Security Test)
- Wait 10+ minutes after OTP is sent
- Try to verify
- System shows: "OTP expired. Please request a new one."
- User must start voting flow again

---

## ✅ How to Verify It's Working

Check for these signs:

- [ ] After selecting candidate, redirects to OTP page (not directly to confirm)
- [ ] OTP page shows message about phone number
- [ ] OTP input field is numeric only
- [ ] Submit button works
- [ ] Wrong OTP shows error message
- [ ] Correct OTP redirects to confirm vote page
- [ ] Vote is recorded in database

If all these work, **OTP is fully integrated!** ✅

---

## 🐛 Debug Mode

To see OTP values in console:

Open Flask console after selecting candidate - you'll see:
```
Generated OTP: 123456 for aadhar: 123456789012
```

This OTP is also displayed if SMS fails.

---

## 📊 Test Results Template

| Step | Expected | Actual | Pass/Fail |
|------|----------|--------|-----------|
| Register voter with phone | Success | | ✓/✗ |
| Login with aadhar | Show candidates | | ✓/✗ |
| Select candidate | Redirect to OTP page | | ✓/✗ |
| OTP page loads | Show OTP form | | ✓/✗ |
| Enter wrong OTP | Show error | | ✓/✗ |
| Enter correct OTP | Redirect to confirm | | ✓/✗ |
| Confirm vote | Show success | | ✓/✗ |
| Check database | Vote recorded | | ✓/✗ |

---

## 🎯 Final Verification

The OTP feature is **ADDED AND WORKING** if:

✅ You see the OTP verification page after selecting a candidate
✅ You can enter a 6-digit code
✅ Valid OTP redirects to confirm vote
✅ Invalid OTP shows error message
✅ Vote is recorded after OTP verification

**If all above are true, OTP is fully integrated!** 🎉

---

**Questions?** Check OTP_QUICK_START.md for more details.
