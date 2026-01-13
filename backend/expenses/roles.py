def get_user_role(user):
    if not user or not user.is_authenticated:
        return None
    names = set(user.groups.values_list("name", flat=True))
    if "finance" in names:
        return "finance"
    if "manager" in names:
        return "manager"
    return "employee"
