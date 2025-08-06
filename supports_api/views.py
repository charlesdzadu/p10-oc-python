from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from .models import User, Project, Contributor, Issue, Comment
from .serializers import (
    UserSerializer, UserCreateSerializer, ProjectSerializer, 
    ContributorSerializer, ContributorCreateSerializer,
    IssueSerializer, IssueCreateSerializer,
    CommentSerializer, CommentCreateSerializer
)
from .permissions import (
    IsProjectAuthorOrReadOnly,
    IsIssueAuthorOrReadOnly, IsCommentAuthorOrReadOnly
)

class StandardResultsSetPagination(PageNumberPagination):
    """Pagination standard pour optimiser les performances (green code)"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@extend_schema_view(
    list=extend_schema(
        summary="Lister tous les utilisateurs",
        description="Récupère la liste paginée de tous les utilisateurs. Nécessite une authentification.",
        tags=['users']
    ),
    create=extend_schema(
        summary="Créer un nouvel utilisateur",
        description="Crée un nouvel utilisateur avec validation RGPD (âge minimum 15 ans).",
        tags=['users'],
        examples=[
            OpenApiExample(
                'Exemple création utilisateur',
                value={
                    "username": "nouveau_utilisateur",
                    "email": "user@example.com",
                    "password": "mot_de_passe_securise",
                    "password_confirm": "mot_de_passe_securise",
                    "age": 25,
                    "can_be_contacted": True,
                    "can_data_be_shared": False
                }
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Récupérer un utilisateur",
        description="Récupère les détails d'un utilisateur spécifique.",
        tags=['users']
    ),
    update=extend_schema(
        summary="Modifier un utilisateur",
        description="Modifie complètement un utilisateur.",
        tags=['users']
    ),
    partial_update=extend_schema(
        summary="Modifier partiellement un utilisateur",
        description="Modifie partiellement un utilisateur.",
        tags=['users']
    ),
    destroy=extend_schema(
        summary="Supprimer un utilisateur",
        description="Supprime un utilisateur (droit à l'oubli RGPD).",
        tags=['users']
    )
)
class UserViewSet(viewsets.ModelViewSet):
    """Vue pour la gestion des utilisateurs avec RGPD"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        """Utilise le bon sérialiseur selon l'action"""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        """Permissions spéciales pour les utilisateurs"""
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @extend_schema(
        summary="Gérer le profil utilisateur",
        description="Permet de consulter et modifier le profil utilisateur (RGPD).",
        tags=['users'],
        methods=['GET'],
        responses={200: UserSerializer}
    )
    @extend_schema(
        summary="Modifier le profil utilisateur",
        description="Modifie le profil utilisateur avec validation RGPD.",
        tags=['users'],
        methods=['PUT', 'PATCH'],
        request=UserSerializer,
        responses={200: UserSerializer, 400: None}
    )
    @action(detail=True, methods=['get', 'put', 'patch'])
    def profile(self, request, pk=None):
        """Gestion du profil utilisateur (RGPD)"""
        user = self.get_object()
        
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Supprimer le compte (droit à l'oubli)",
        description="Supprime complètement le compte utilisateur selon le RGPD.",
        tags=['users'],
        responses={204: None, 403: None}
    )
    @action(detail=True, methods=['delete'])
    def delete_account(self, request, pk=None):
        """Droit à l'oubli (RGPD)"""
        user = self.get_object()
        if user == request.user:
            user.delete()
            return Response({"message": "Compte supprimé avec succès"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)








""" Project ViewSet """
@extend_schema_view(
    list=extend_schema(
        summary="Lister les projets",
        description="Récupère la liste paginée des projets de l'utilisateur connecté.",
        tags=['projects']
    ),
    create=extend_schema(
        summary="Créer un nouveau projet",
        description="Crée un nouveau projet et ajoute l'utilisateur comme contributeur.",
        tags=['projects'],
        examples=[
            OpenApiExample(
                'Exemple création projet',
                value={
                    "title": "Mon Projet",
                    "description": "Description du projet",
                    "type": "back-end"
                }
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Récupérer un projet",
        description="Récupère les détails d'un projet spécifique.",
        tags=['projects']
    ),
    update=extend_schema(
        summary="Modifier un projet",
        description="Modifie complètement un projet (auteur uniquement).",
        tags=['projects']
    ),
    partial_update=extend_schema(
        summary="Modifier partiellement un projet",
        description="Modifie partiellement un projet (auteur uniquement).",
        tags=['projects']
    ),
    destroy=extend_schema(
        summary="Supprimer un projet",
        description="Supprime un projet (auteur uniquement).",
        tags=['projects']
    )
)
class ProjectViewSet(viewsets.ModelViewSet):
    """Vue pour la gestion des projets"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Filtre les projets selon les contributeurs"""
        return Project.objects.filter(contributors__user=self.request.user).distinct()

    def perform_create(self, serializer):
        """Crée le projet et ajoute l'auteur comme contributeur"""
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)

    @extend_schema(
        summary="Lister les contributeurs",
        description="Récupère la liste des contributeurs d'un projet.",
        tags=['projects'],
        responses={200: ContributorSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def contributors(self, request, pk=None):
        """Liste des contributeurs d'un projet"""
        project = self.get_object()
        contributors = project.contributors.all()
        serializer = ContributorSerializer(contributors, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Ajouter un contributeur",
        description="Ajoute un contributeur au projet (auteur uniquement).",
        tags=['projects'],
        request=ContributorCreateSerializer,
        responses={201: ContributorSerializer, 400: None, 403: None}
    )
    @action(detail=True, methods=['post'])
    def add_contributor(self, request, pk=None):
        """Ajouter un contributeur au projet"""
        project = self.get_object()
        
        # Seul l'auteur peut ajouter des contributeurs
        if project.author != request.user:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ContributorCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {"error": "Ce contributeur existe déjà dans ce projet"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
""" Issue ViewSet """
@extend_schema_view(
    list=extend_schema(
        summary="Lister les problèmes",
        description="Récupère la liste paginée des problèmes des projets de l'utilisateur.",
        tags=['issues']
    ),
    create=extend_schema(
        summary="Créer un nouveau problème",
        description="Crée un nouveau problème dans un projet.",
        tags=['issues'],
        examples=[
            OpenApiExample(
                'Exemple création problème',
                value={
                    "title": "Bug critique",
                    "description": "Description du problème",
                    "priority": "HIGH",
                    "status": "To Do",
                    "tag": "BUG",
                    "project": 1,
                    "assigned_to_id": 2
                }
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Récupérer un problème",
        description="Récupère les détails d'un problème spécifique.",
        tags=['issues']
    ),
    update=extend_schema(
        summary="Modifier un problème",
        description="Modifie complètement un problème (auteur uniquement).",
        tags=['issues']
    ),
    partial_update=extend_schema(
        summary="Modifier partiellement un problème",
        description="Modifie partiellement un problème (auteur uniquement).",
        tags=['issues']
    ),
    destroy=extend_schema(
        summary="Supprimer un problème",
        description="Supprime un problème (auteur uniquement).",
        tags=['issues']
    )
)
class IssueViewSet(viewsets.ModelViewSet):
    """Vue pour la gestion des problèmes"""
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsIssueAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Filtre les issues selon les projets de l'utilisateur"""
        return Issue.objects.filter(project__contributors__user=self.request.user).distinct()

    def get_serializer_class(self):
        """Utilise le bon sérialiseur selon l'action"""
        if self.action == 'create':
            return IssueCreateSerializer
        return IssueSerializer

    def perform_create(self, serializer):
        """Crée l'issue avec l'auteur"""
        serializer.save(author=self.request.user)

    @extend_schema(
        summary="Lister les commentaires",
        description="Récupère la liste des commentaires d'un problème.",
        tags=['issues'],
        responses={200: CommentSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Liste des commentaires d'une issue"""
        issue = self.get_object()
        comments = issue.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)



""" Comment ViewSet """
@extend_schema_view(
    list=extend_schema(
        summary="Lister les commentaires",
        description="Récupère la liste paginée des commentaires des projets de l'utilisateur.",
        tags=['comments']
    ),
    create=extend_schema(
        summary="Créer un nouveau commentaire",
        description="Crée un nouveau commentaire sur un problème.",
        tags=['comments'],
        examples=[
            OpenApiExample(
                'Exemple création commentaire',
                value={
                    "description": "Commentaire sur le problème",
                    "issue": 1
                }
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Récupérer un commentaire",
        description="Récupère les détails d'un commentaire spécifique (par UUID).",
        tags=['comments']
    ),
    update=extend_schema(
        summary="Modifier un commentaire",
        description="Modifie complètement un commentaire (auteur uniquement).",
        tags=['comments']
    ),
    partial_update=extend_schema(
        summary="Modifier partiellement un commentaire",
        description="Modifie partiellement un commentaire (auteur uniquement).",
        tags=['comments']
    ),
    destroy=extend_schema(
        summary="Supprimer un commentaire",
        description="Supprime un commentaire (auteur uniquement).",
        tags=['comments']
    )
)
class CommentViewSet(viewsets.ModelViewSet):
    """Vue pour la gestion des commentaires"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'uuid'

    def get_queryset(self):
        """Filtre les commentaires selon les projets de l'utilisateur"""
        return Comment.objects.filter(issue__project__contributors__user=self.request.user).distinct()

    def get_serializer_class(self):
        """Utilise le bon sérialiseur selon l'action"""
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        """Crée le commentaire avec l'auteur"""
        serializer.save(author=self.request.user)
    
    def get_object(self):
        """Récupère un commentaire par UUID au lieu de l'ID par défaut"""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        uuid_value = self.kwargs[lookup_url_kwarg]
        
        try:
            return get_object_or_404(Comment, uuid=uuid_value)
        except ValueError:
            # Si l'UUID n'est pas valide, retourner une erreur 400
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"'{uuid_value}' n'est pas un UUID valide")
