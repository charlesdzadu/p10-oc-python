from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Comment, Contributor, Issue, Project, User


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les utilisateurs avec validation RGPD"""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "age",
            "can_be_contacted",
            "can_data_be_shared",
            "created_time",
            "updated_time",
        ]
        read_only_fields = ["id", "created_time", "updated_time"]

    def validate_age(self, value):
        """Validation de l'âge selon RGPD"""
        if value < 15:
            raise serializers.ValidationError(
                "L'utilisateur doit avoir au moins 15 ans selon le RGPD"
            )
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création d'utilisateurs"""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "age",
            "can_be_contacted",
            "can_data_be_shared",
        ]

    def validate(self, attrs):
        """Validation des mots de passe"""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return attrs

    def create(self, validated_data):
        """Création d'un utilisateur avec mot de passe hashé"""
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class ProjectSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les projets"""

    author = UserSerializer(read_only=True)
    contributors_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "type",
            "author",
            "contributors_count",
            "created_time",
            "updated_time",
        ]
        read_only_fields = ["id", "author", "created_time", "updated_time"]

    def get_contributors_count(self, obj):
        """Compte le nombre de contributeurs"""
        return obj.contributors.count()


class ContributorSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les contributeurs"""

    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Contributor
        fields = ["id", "user", "project", "created_time"]
        read_only_fields = ["id", "created_time"]


class ContributorCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour ajouter un contributeur"""

    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Contributor
        fields = ["user_id", "project"]

    def validate(self, attrs):
        """Validation que l'utilisateur existe"""
        user_id = attrs.get("user_id")
        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur introuvable")
        return attrs

    def create(self, validated_data):
        """Création d'un contributeur"""
        user_id = validated_data.pop("user_id")
        user = User.objects.get(id=user_id)
        return Contributor.objects.create(user=user, **validated_data)


class IssueSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les problèmes"""

    author = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "status",
            "tag",
            "project",
            "author",
            "assigned_to",
            "comments_count",
            "created_time",
            "updated_time",
        ]
        read_only_fields = ["id", "author", "created_time", "updated_time"]

    def get_comments_count(self, obj):
        """Compte le nombre de commentaires"""
        return obj.comments.count()


class IssueCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création de problèmes"""

    assigned_to_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Issue
        fields = [
            "title",
            "description",
            "priority",
            "status",
            "tag",
            "project",
            "assigned_to_id",
        ]

    def validate_assigned_to_id(self, value):
        """Validation que l'utilisateur assigné est un contributeur du projet"""
        if value:
            try:
                user = User.objects.get(id=value)
                project = self.context.get("project")
                if project and not project.contributors.filter(user=user).exists():
                    raise serializers.ValidationError(
                        "L'utilisateur assigné doit être un contributeur du projet"
                    )
            except User.DoesNotExist:
                raise serializers.ValidationError("Utilisateur introuvable")
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les commentaires"""

    author = UserSerializer(read_only=True)
    issue = IssueSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "uuid",
            "description",
            "issue",
            "author",
            "created_time",
            "updated_time",
        ]
        read_only_fields = ["id", "uuid", "author", "created_time", "updated_time"]


class CommentCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création de commentaires"""

    class Meta:
        model = Comment
        fields = ["description", "issue"]
