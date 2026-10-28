def user_profile(request):
    profile = None

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except (
            request.user.__class__.profile.RelatedObjectDoesNotExist
        ):
            profile = None

    return {
        "user_profile": profile,
    }