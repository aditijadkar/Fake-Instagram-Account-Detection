import instaloader
import os

def get_instagram_data(username):
    # Check for login credentials.
    IG_USERNAME = os.getenv("IG_USERNAME")
    IG_PASSWORD = os.getenv("IG_PASSWORD")
    if not (IG_USERNAME and IG_PASSWORD):
        print("No login credentials provided. Please set IG_USERNAME and IG_PASSWORD environment variables.")
        return {"error": "No login credentials provided. Please set IG_USERNAME and IG_PASSWORD environment variables for reliable analysis."}

    try:
        loader = instaloader.Instaloader()
        loader.context.do_not_save_session = False  # Enable saving/loading sessions

        # Update the session headers with a realistic User-Agent.
        # Use loader.context._session since loader.context.session is not available.
        loader.context._session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/112.0.0.0 Safari/537.36'
            )
        })

        # Attempt to load an existing session.
        try:
            loader.load_session_from_file(IG_USERNAME)
            print("Session loaded from file.")
        except Exception as e:
            print("No session file found or failed to load session, logging in now.")
            loader.login(IG_USERNAME, IG_PASSWORD)
            loader.save_session_to_file()
            print(f"Logged in successfully as {IG_USERNAME} and session saved.")

        # Attempt to load the target profile.
        profile = instaloader.Profile.from_username(loader.context, username)

        # Helper function to count numeric characters.
        def count_numeric_chars(s):
            return sum(c.isdigit() for c in s)

        user_name = profile.username
        full_name = profile.full_name or ""
        bio = profile.biography or ""
        external_url = profile.external_url or ""

        # Compute ratios and counts.
        username_len = len(user_name)
        fullname_len = len(full_name)
        nums_length_username = count_numeric_chars(user_name) / username_len if username_len > 0 else 0.0
        nums_length_fullname = count_numeric_chars(full_name) / fullname_len if fullname_len > 0 else 0.0
        fullname_words = len(full_name.split()) if full_name else 0
        name_equals_username = 1 if full_name.strip().lower() == user_name.lower() else 0
        description_length = len(bio)
        has_external_url = 1 if external_url.strip() else 0
        is_private = 1 if profile.is_private else 0
        has_profile_pic = 1 if getattr(profile, "profile_pic_url", None) else 0

        data = {
            "username": user_name,
            "profile_pic": has_profile_pic,
            "nums_length_username": nums_length_username,
            "fullname_words": fullname_words,
            "nums_length_fullname": nums_length_fullname,
            "name_equals_username": name_equals_username,
            "description_length": description_length,
            "external_url": has_external_url,
            "private": is_private,
            "posts": profile.mediacount,
            "followers": profile.followers,
            "following": profile.followees,
        }
        return data

    except instaloader.exceptions.ProfileNotExistsException:
        return {"error": "Profile not found"}
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        if "Could not find \"window._sharedData\"" in error_msg:
            return {"error": "Login challenge required. Please complete the login challenge manually and try again."}
        if "Please wait a few minutes" in error_msg:
            return {"error": "Rate limit reached. Please try again in a few minutes."}
        return {"error": error_msg}

if __name__ == "__main__":
    username = input("Enter Instagram username: ")
    result = get_instagram_data(username)
    print(result)
