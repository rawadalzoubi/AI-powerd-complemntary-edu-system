from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import secrets
import string
from ..models.user_model import User

@staff_member_required
@require_POST
def reset_advisor_password(request, user_id):
    """Reset advisor password and return new password"""
    try:
        advisor = get_object_or_404(User, id=user_id, role='advisor')
        
        # Generate secure random password
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        new_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        # Set new password
        advisor.set_password(new_password)
        advisor.save()
        
        messages.success(
            request, 
            f'🔑 Password reset for {advisor.get_full_name()}. New password: <strong>{new_password}</strong>'
        )
        
        # Redirect back to admin changelist
        return redirect('admin:eduAPI_user_changelist')
        
    except User.DoesNotExist:
        messages.error(request, '❌ Advisor not found.')
        return redirect('admin:eduAPI_user_changelist')
    except Exception as e:
        messages.error(request, f'❌ Error resetting password: {str(e)}')
        return redirect('admin:eduAPI_user_changelist')

@staff_member_required
def advisor_stats(request):
    """Get advisor statistics"""
    total_advisors = User.objects.filter(role='advisor').count()
    active_advisors = User.objects.filter(role='advisor', is_active=True).count()
    inactive_advisors = total_advisors - active_advisors
    
    return JsonResponse({
        'total_advisors': total_advisors,
        'active_advisors': active_advisors,
        'inactive_advisors': inactive_advisors
    })