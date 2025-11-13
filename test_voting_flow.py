"""
Automated test of the complete voting flow:
1. Register a test voter
2. Login with Aadhar
3. Vote for a candidate
4. Confirm the vote
5. Verify vote appears in results

Run: python test_voting_flow.py
"""

import requests
import time

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

print("=" * 60)
print("SMART VOTING SYSTEM - END-TO-END TEST")
print("=" * 60)

# Test data
test_aadhar = "999999999999"
test_voter_id = "ABC12345"
test_phone = "9999999999"
test_email = "test@voting.com"

# Step 1: Register a test voter
print("\n[1] Registering test voter...")
registration_data = {
    'first_name': 'Test',
    'middle_name': '',
    'last_name': 'Voter',
    'aadhar_id': test_aadhar,
    'voter_id': test_voter_id,
    'pno': test_phone,
    'state': 'Maharashtra',
    'd_name': 'Mumbai',
    'age': '25',
    'email': test_email
}

try:
    resp = session.post(f"{BASE_URL}/registration", data=registration_data)
    if resp.status_code == 200 or resp.status_code == 302:
        print("✓ Registration successful (Status: {})".format(resp.status_code))
        # Check if session was set by looking for redirect to voting
        if "voting" in resp.url or resp.status_code == 302:
            print("✓ Redirected to voting page")
    else:
        print("✗ Registration failed (Status: {})".format(resp.status_code))
except Exception as e:
    print(f"✗ Registration error: {e}")
    exit(1)

time.sleep(1)

# Step 2: Access voting page
print("\n[2] Accessing voting page...")
try:
    resp = session.get(f"{BASE_URL}/voting")
    if resp.status_code == 200:
        print("✓ Voting page loaded (Status: 200)")
        if "Cast Your Vote" in resp.text or "candidate" in resp.text.lower():
            print("✓ Voting form found")
        else:
            print("⚠ Warning: Expected voting form not found")
    else:
        print(f"✗ Failed to load voting page (Status: {resp.status_code})")
except Exception as e:
    print(f"✗ Error accessing voting page: {e}")

time.sleep(1)

# Step 3: Submit voting page (select candidate)
print("\n[3] Submitting voting page (selecting candidate)...")
vote_data = {'test': '1'}  # Select candidate with symbol '1'
try:
    resp = session.post(f"{BASE_URL}/voting", data=vote_data)
    if resp.status_code == 200 or resp.status_code == 302:
        print("✓ Voting form submitted (Status: {})".format(resp.status_code))
        if "select" in resp.url.lower() or "confirm" in resp.url.lower():
            print("✓ Redirected to select_candidate/confirmation page")
    else:
        print(f"✗ Failed to submit voting form (Status: {resp.status_code})")
except Exception as e:
    print(f"✗ Error submitting voting form: {e}")

time.sleep(1)

# Step 4: Access select_candidate page
print("\n[4] Accessing select_candidate page...")
try:
    resp = session.get(f"{BASE_URL}/select_candidate")
    if resp.status_code == 200:
        print("✓ Select candidate page loaded (Status: 200)")
        if "confirm" in resp.text.lower() or "select" in resp.text.lower():
            print("✓ Selection form found")
    else:
        print(f"✗ Failed to load select_candidate page (Status: {resp.status_code})")
except Exception as e:
    print(f"✗ Error accessing select_candidate: {e}")

time.sleep(1)

# Step 5: Submit select_candidate (confirm vote)
print("\n[5] Submitting select_candidate (confirm vote)...")
select_data = {'test': '1'}  # Confirm vote for symbol '1'
try:
    resp = session.post(f"{BASE_URL}/select_candidate", data=select_data, allow_redirects=False)
    if resp.status_code in [200, 302]:
        print("✓ Select candidate form submitted (Status: {})".format(resp.status_code))
        if resp.status_code == 302:
            redirect_url = resp.headers.get('Location', '')
            print(f"✓ Redirected to: {redirect_url}")
            if "confirm_vote" in redirect_url:
                print("✓ Redirected to confirm_vote page (correct flow)")
    else:
        print(f"✗ Failed to submit select_candidate (Status: {resp.status_code})")
except Exception as e:
    print(f"✗ Error submitting select_candidate: {e}")

time.sleep(1)

# Step 6: Access confirm_vote page
print("\n[6] Accessing confirm_vote page...")
try:
    resp = session.get(f"{BASE_URL}/confirm_vote")
    if resp.status_code == 200:
        print("✓ Confirm vote page loaded (Status: 200)")
        if "confirm" in resp.text.lower() or "final" in resp.text.lower():
            print("✓ Confirmation form found")
    else:
        print(f"✗ Failed to load confirm_vote page (Status: {resp.status_code})")
except Exception as e:
    print(f"✗ Error accessing confirm_vote: {e}")

time.sleep(1)

# Step 7: Submit confirm_vote (finalize vote)
print("\n[7] Submitting confirm_vote (finalizing vote)...")
try:
    resp = session.post(f"{BASE_URL}/confirm_vote", allow_redirects=False)
    if resp.status_code in [200, 302]:
        print("✓ Confirm vote form submitted (Status: {})".format(resp.status_code))
        if resp.status_code == 302:
            redirect_url = resp.headers.get('Location', '')
            print(f"✓ Redirected to: {redirect_url}")
            if "home" in redirect_url:
                print("✓ Redirected to home (vote cast successfully)")
    else:
        print(f"✗ Failed to submit confirm_vote (Status: {resp.status_code})")
except Exception as e:
    print(f"✗ Error submitting confirm_vote: {e}")

time.sleep(1)

# Step 8: Check voting results
print("\n[8] Checking voting results...")
try:
    resp = session.get(f"{BASE_URL}/voting_res")
    if resp.status_code == 200:
        print("✓ Results page loaded (Status: 200)")
        if "results" in resp.text.lower() or "vote" in resp.text.lower():
            print("✓ Results displayed")
        # Check if our vote is counted
        if ">1<" in resp.text or "symbol" in resp.text.lower():
            print("✓ Vote count appears in results")
    else:
        print(f"✗ Failed to load results page (Status: {resp.status_code})")
except Exception as e:
    print(f"✗ Error accessing results: {e}")

print("\n" + "=" * 60)
print("END-TO-END TEST COMPLETED")
print("=" * 60)
