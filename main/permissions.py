from rest_framework.permissions import BasePermission, SAFE_METHODS


EDITOR_GROUP_NAME = 'Editor'


def is_editor(user):
    return (
        user.is_authenticated
        and user.groups.filter(name=EDITOR_GROUP_NAME).exists()
    )


def can_update_portfolio(user):
    return user.is_superuser or is_editor(user)


class IsPortfolioOwnerOrReadOnly(BasePermission):
    message = 'Only the portfolio owner can change projects.'

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    message = 'Only the portfolio owner or an editor can change experiences.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        return request.method in ('PUT', 'PATCH') and is_editor(request.user)
