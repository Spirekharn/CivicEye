from django.contrib import admin
from .models import Complaint, ComplaintStatusHistory, SurveyReport, ComplaintFeedback

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display  = ('id','title','category','status','priority','city_corp','department','citizen','created_at')
    list_filter   = ('status','category','priority','city_corp')
    search_fields = ('title','location_text')
    readonly_fields = ('created_at','updated_at','city_corp')

admin.site.register(ComplaintStatusHistory)
admin.site.register(SurveyReport)
admin.site.register(ComplaintFeedback)
