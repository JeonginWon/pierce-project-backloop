from django.contrib import admin
from .models import VectorTest, Member

# 1. 벡터 테스트 테이블 관리자 화면 설정
@admin.register(VectorTest)
class VectorTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_preview', 'created_at') # 목록에 보여줄 칼럼
    readonly_fields = ('embedding',) # 임베딩은 수정 못하게 막음 (자동생성이니까)

    # 내용이 너무 길면 앞부분만 보여주는 함수
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "내용 미리보기"

# 2. 멤버 테이블 관리자 화면 설정
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'joined_at')