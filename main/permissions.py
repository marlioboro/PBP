EDITOR_GROUP_NAME = 'Editor'


def is_editor(user):
    return (
        user.is_authenticated
        and user.groups.filter(name=EDITOR_GROUP_NAME).exists()
    )


def can_update_portfolio(user):
    return user.is_superuser or is_editor(user)
