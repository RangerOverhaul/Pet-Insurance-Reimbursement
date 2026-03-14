from datetime import timedelta
from django.db import models
from django.utils import timezone
from users.models import User


class Pet(models.Model):
    class Species(models.TextChoices):
        DOG = "DOG", "Dog"
        CAT = "CAT", "Cat"
        BIRD = "BIRD", "Bird"
        FISH = "FISH", "Fish"
        RABBIT = "RABBIT", "Rabbit"
        HAMSTER = "HAMSTER", "Hamster"
        GUINEA_PIG = "GUINEA_PIG", "Guinea Pig"
        TURTLE = "TURTLE", "Turtle"
        FERRET = "FERRET", "Ferret"
        SNAKE = "SNAKE", "Snake"
        LIZARD = "LIZARD", "Lizard"
        OTHER = "OTHER", "Other"

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pets")
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=10, choices=Species.choices)
    birth_date = models.DateField()
    coverage_start = models.DateField(default=timezone.now)
    coverage_end = models.DateField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.coverage_end = self.coverage_start + timedelta(days=365)
        super().save(*args, **kwargs)

    @property
    def is_coverage_active(self):
        today = timezone.now().date()
        return self.coverage_start <= today <= self.coverage_end

    def is_date_covered(self, date):
        return self.coverage_start <= date <= self.coverage_end

    def __str__(self):
        return f"{self.name} ({self.species}) — {self.owner.email}"