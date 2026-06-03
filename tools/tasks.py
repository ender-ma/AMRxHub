# from celery import shared_task
# from django.utils import timezone
# from .models import AnalysisHistory

# @shared_task
# def run_analysis(analysis_id):
#     """
#     Background task to run analysis
#     """
#     try:
#         # Get the analysis object
#         analysis = AnalysisHistory.objects.get(id=analysis_id)
        
#         # Update status to processing
#         analysis.status = 'processing'
#         analysis.save()
        
#         # Perform the actual analysis
#         # In a real-world scenario, you would call your analysis code here
#         # For demonstration, we'll just simulate a successful analysis
        
#         # Simulate processing time
#         import time
#         time.sleep(5)  # Simulate 5 seconds of processing
        
#         # Update status to completed
#         analysis.status = 'completed'
#         analysis.completed_at = timezone.now()
#         analysis.save()
        
#         return f"Analysis {analysis_id} completed successfully"
        
#     except AnalysisHistory.DoesNotExist:
#         return f"Analysis {analysis_id} not found"
#     except Exception as e:
#         # Try to update the analysis status if possible
#         try:
#             analysis = AnalysisHistory.objects.get(id=analysis_id)
#             analysis.status = 'failed'
#             analysis.error_message = str(e)
#             analysis.completed_at = timezone.now()
#             analysis.save()
#         except:
#             pass
        
#         return f"Analysis {analysis_id} failed: {str(e)}"