def get_user_avatar_path(instance, filename):
    """
    Generate a unique path for user avatar uploads.
    Example: users/1/avatars/avatar.jpg
    """
    return f"users/{instance.pk}/avatars/{filename}"


def send_activate_user_email(user):
    pass
