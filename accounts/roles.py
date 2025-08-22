
def roles(request):
    return {"roles": get_roles(request.user)}

# used by context processor to make roles available for templates
# without repeating boilerplate in views


def get_roles(user):
    """Return a consistent roles dict for templates & code."""
    if not user.is_authenticated:
        return {
            "student": False, "teacher": False, "admin": False,
            "list": [],
        }

    # Try to pull group names once
    # cache on the user to avoid repeated db hits
    if not hasattr(user, "_role_names"):
        names = set(user.groups.values_list("name", flat=True))
        if user.is_superuser:  # treat superusers as 'admin'
            names.add("admin")
        user._role_names = names

    roles = {
        "student": "student" in user._role_names,
        "teacher": "teacher" in user._role_names,
        "admin":   "admin" in user._role_names,
    }
    ROLE_KEYS = ("student", "teacher", "admin")
    roles["list"] = [r for r in ROLE_KEYS if roles.get(r)]
    return roles
