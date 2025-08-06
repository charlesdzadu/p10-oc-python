from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.utils import extend_schema, OpenApiExample
from .views import UserViewSet, ProjectViewSet, IssueViewSet, CommentViewSet

# Configuration du router pour les ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'comments', CommentViewSet, basename='comment')

# Vues d'authentification avec documentation Swagger
class DocumentedTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        summary="Obtenir un token JWT",
        description="Authentifie un utilisateur et retourne un token d'accès et de rafraîchissement.",
        tags=['auth'],
        examples=[
            OpenApiExample(
                'Exemple authentification',
                value={
                    "username": "votre_username",
                    "password": "votre_password"
                }
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "description": "Token d'accès"},
                    "refresh": {"type": "string", "description": "Token de rafraîchissement"}
                }
            },
            401: {"description": "Identifiants invalides"}
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class DocumentedTokenRefreshView(TokenRefreshView):
    @extend_schema(
        summary="Rafraîchir un token JWT",
        description="Rafraîchit un token d'accès expiré en utilisant le token de rafraîchissement.",
        tags=['auth'],
        examples=[
            OpenApiExample(
                'Exemple rafraîchissement',
                value={
                    "refresh": "votre_refresh_token"
                }
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "description": "Nouveau token d'accès"}
                }
            },
            401: {"description": "Token de rafraîchissement invalide"}
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# URLs pour l'authentification JWT
auth_urls = [
    path('token/', DocumentedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', DocumentedTokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns = [
    # Routes pour l'authentification
    path('auth/', include(auth_urls)),
    
    # Routes pour l'API
    path('', include(router.urls)),
] 