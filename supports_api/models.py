from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
import uuid

class User(AbstractUser):
    """Modèle utilisateur avec gestion RGPD et consentement"""
    age = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(15, "L'utilisateur doit avoir au moins 15 ans selon le RGPD")]
    )
    can_be_contacted = models.BooleanField(default=False, help_text="Consentement pour être contacté")
    can_data_be_shared = models.BooleanField(default=False, help_text="Consentement pour partager les données")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.username

    def clean(self):
        """Validation RGPD pour les utilisateurs non-superuser"""
        from django.core.exceptions import ValidationError
        if not self.is_superuser and (self.age is None or self.age < 15):
            raise ValidationError("L'utilisateur doit avoir au moins 15 ans selon le RGPD")

class Project(models.Model):
    """Modèle pour les projets"""
    PROJECT_TYPES = [
        ('back-end', 'Back-end'),
        ('front-end', 'Front-end'),
        ('iOS', 'iOS'),
        ('Android', 'Android'),
    ]
    
    title = models.CharField(max_length=128)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=PROJECT_TYPES)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_projects')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    def __str__(self):
        return self.title

class Contributor(models.Model):
    """Modèle pour les contributeurs d'un projet"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contributors')
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contributeur"
        verbose_name_plural = "Contributeurs"
        unique_together = ['user', 'project']

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"

class Issue(models.Model):
    """Modèle pour les problèmes/tâches d'un projet"""
    PRIORITY_CHOICES = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Élevée'),
    ]
    
    STATUS_CHOICES = [
        ('To Do', 'À faire'),
        ('In Progress', 'En cours'),
        ('Finished', 'Terminé'),
    ]
    
    TAG_CHOICES = [
        ('BUG', 'Bug'),
        ('FEATURE', 'Fonctionnalité'),
        ('TASK', 'Tâche'),
    ]
    
    title = models.CharField(max_length=128)
    description = models.TextField()
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='To Do')
    tag = models.CharField(max_length=7, choices=TAG_CHOICES)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_issues')
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_issues'
    )
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Problème"
        verbose_name_plural = "Problèmes"

    def __str__(self):
        return self.title

class Comment(models.Model):
    """Modèle pour les commentaires d'un problème"""
    description = models.TextField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_comments')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"

    def __str__(self):
        return f"Commentaire de {self.author.username} sur {self.issue.title}"
