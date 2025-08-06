from rest_framework import permissions

from .models import Contributor, Project


class IsProjectContributor(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur est contributeur du projet"""

    def has_permission(self, request, _):
        """Vérifie si l'utilisateur est authentifié"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, _, obj):
        """Vérifie si l'utilisateur est contributeur du projet"""
        if hasattr(obj, "project"):
            # Pour les issues et comments
            return Contributor.objects.filter(
                user=request.user, project=obj.project
            ).exists()
        elif isinstance(obj, Project):
            # Pour les projets
            return Contributor.objects.filter(user=request.user, project=obj).exists()
        return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Permission pour permettre à l'auteur de modifier/supprimer, lecture pour les autres"""

    def has_permission(self, request, _):
        """Vérifie si l'utilisateur est authentifié"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, _, obj):
        """Vérifie les permissions sur l'objet"""
        # Lecture autorisée pour tous les contributeurs
        if request.method in permissions.SAFE_METHODS:
            return True

        # Modification/suppression uniquement pour l'auteur
        return obj.author == request.user


class IsProjectAuthorOrReadOnly(permissions.BasePermission):
    """Permission spéciale pour les projets - l'auteur peut tout faire"""

    def has_permission(self, request, _):
        """Vérifie si l'utilisateur est authentifié"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, _, obj):
        """Vérifie les permissions sur le projet"""
        # Lecture autorisée pour tous les contributeurs
        if request.method in permissions.SAFE_METHODS:
            return Contributor.objects.filter(user=request.user, project=obj).exists()

        # Modification/suppression uniquement pour l'auteur
        return obj.author == request.user


class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    """Permission spéciale pour les commentaires"""

    def has_permission(self, request, _):
        """Vérifie si l'utilisateur est authentifié"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie les permissions sur le commentaire"""
        # Lecture autorisée pour tous les contributeurs du projet
        if request.method in permissions.SAFE_METHODS:
            return Contributor.objects.filter(
                user=request.user, project=obj.issue.project
            ).exists()

        # Modification/suppression uniquement pour l'auteur du commentaire
        return obj.author == request.user


class IsIssueAuthorOrReadOnly(permissions.BasePermission):
    """Permission spéciale pour les issues"""

    def has_permission(self, request, view):
        """Vérifie si l'utilisateur est authentifié"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie les permissions sur l'issue"""
        # Lecture autorisée pour tous les contributeurs du projet
        if request.method in permissions.SAFE_METHODS:
            return Contributor.objects.filter(
                user=request.user, project=obj.project
            ).exists()

        # Modification/suppression uniquement pour l'auteur de l'issue
        return obj.author == request.user


class IsUserOwnerOrReadOnly(permissions.BasePermission):
    """Permission pour les utilisateurs - lecture pour tous, modification uniquement pour le propriétaire"""

    def has_permission(self, request, view):
        """Vérifie si l'utilisateur est authentifié"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie les permissions sur l'utilisateur"""
        # Lecture autorisée pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True

        # Modification/suppression uniquement pour le propriétaire du compte
        return obj == request.user
