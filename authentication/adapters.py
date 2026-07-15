from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from profil.models import UserProfile


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = sociallogin.user
        user.email = data.get("email", "")

        if sociallogin.account.provider == "google":
            user.first_name = data.get("given_name", "")
            user.last_name = data.get("family_name", "")

        if hasattr(user, "username") and not user.username:
            base_username = user.email.split("@")[0]
            user.username = base_username[:30]

        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        if sociallogin.account.provider == "google":
            first_name = sociallogin.account.extra_data.get("given_name", "")
            last_name = sociallogin.account.extra_data.get("family_name", "")

            if first_name and not user.first_name:
                user.first_name = first_name
            if last_name and not user.last_name:
                user.last_name = last_name

        if hasattr(user, "username") and not user.username:
            user.username = user.email.split("@")[0][:30]

        user.is_email_verified = True
        user.save()

        try:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                profile.save()
        except Exception as exc:
            print(f"Error creating profile: {exc}")

        return user