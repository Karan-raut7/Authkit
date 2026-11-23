import requests

BASE_URL = "http://127.0.0.1:8000/v1/auth"

EMAIL = "karan2@gmail.com.com"
PASSWORD = "11111111"


def main():
    # Step 1: Log in and obtain a refresh token.
    login_response = requests.post(
        f"{BASE_URL}/login",
        json={
            "email": EMAIL,
            "password": PASSWORD,
        },
        timeout=10,
    )

    print("Login status:", login_response.status_code)

    if login_response.status_code != 200:
        print("Login response:", login_response.text)
        raise SystemExit(
            "Login failed. Check your test account credentials."
        )

    refresh_token = login_response.json()["refresh_token"]

    print("Login successful! Testing refresh rate limit...\n")

    # Step 2: Test refresh-token rotation and rate limiting.
    for attempt in range(1, 16):
        response = requests.post(
            f"{BASE_URL}/refresh",
            json={"refresh_token": refresh_token},
            timeout=10,
        )

        print(f"Attempt {attempt}: HTTP {response.status_code}")

        if response.status_code == 429:
            print("Rate limit reached!")
            break

        if response.status_code != 200:
            print("Request failed:", response.text)
            break

        # Use the newly issued token after successful rotation.
        refresh_token = response.json()["refresh_token"]

    else:
        print("\nNo rate limit was reached within 15 attempts.")


if __name__ == "__main__":
    main()
