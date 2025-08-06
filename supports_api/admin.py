from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Comment, Contributor, Issue, Project, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin personnalisé pour le modèle User avec gestion RGPD"""

    list_display = (
        "username",
        "email",
        "age",
        "can_be_contacted",
        "can_data_be_shared",
        "is_active",
    )
    list_filter = ("can_be_contacted", "can_data_be_shared", "is_active", "is_staff")
    search_fields = ("username", "email")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        ("RGPD", {"fields": ("age", "can_be_contacted", "can_data_be_shared")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("RGPD", {"fields": ("age", "can_be_contacted", "can_data_be_shared")}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin pour les projets"""

    list_display = ("title", "type", "author", "created_time", "contributors_count")
    list_filter = ("type", "created_time")
    search_fields = ("title", "description", "author__username")
    ordering = ("-created_time",)
    readonly_fields = ("created_time", "updated_time")

    def contributors_count(self, obj):
        """Compte le nombre de contributeurs"""
        return obj.contributors.count()

    contributors_count.short_description = "Contributeurs"


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    """Admin pour les contributeurs"""

    list_display = ("user", "project", "created_time")
    list_filter = ("created_time", "project__type")
    search_fields = ("user__username", "project__title")
    ordering = ("-created_time",)
    readonly_fields = ("created_time",)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Admin pour les problèmes"""

    list_display = (
        "title",
        "project",
        "author",
        "assigned_to",
        "priority",
        "status",
        "tag",
        "created_time",
    )
    list_filter = ("priority", "status", "tag", "created_time", "project__type")
    search_fields = (
        "title",
        "description",
        "author__username",
        "assigned_to__username",
    )
    ordering = ("-created_time",)
    readonly_fields = ("created_time", "updated_time")
    list_select_related = ("project", "author", "assigned_to")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin pour les commentaires"""

    list_display = ("uuid", "issue", "author", "created_time")
    list_filter = ("created_time", "issue__project__type")
    search_fields = ("description", "author__username", "issue__title")
    ordering = ("-created_time",)
    readonly_fields = ("uuid", "created_time", "updated_time")
    list_select_related = ("issue", "author")
