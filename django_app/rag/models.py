from django.db import models
from pgvector.django import VectorField

# 1. 벡터 테스트용 테이블

class VectorTest(models.Model):
    content = models.TextField()
    embedding = VectorField(dimensions=384) 
    created_at = models.DateTimeField(auto_now_add=True)

# 2. 일반 정형 데이터 테스트용 테이블

class Member(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    joined_at = models.DateTimeField(auto_now_add=True)