from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json
import secrets
import string
from ..models.user_model import User

def superuser_required(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'admin')

@user_passes_test(superuser_required)
def advisor_list(request):
    """List all advisors"""
    advisors = User.objects.filter(role='advisor').order_by('-date_joined')
    context = {
        'advisors': advisors,
        'total_advisors': advisors.count(),
        'active_advisors': advisors.filter(is_active=True).count(),
    }
    return render(request, 'advisor_management/advisor_list.html', context)

@user_passes_test(superuser_required)
def create_advisor(request):
    """Create new advisor"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password')
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, f'❌ Email {email} already exists!')
                return redirect('advisor_list')
            
            # Create advisor
            advisor = User.objects.create_user(
                email=email,
                username=email,
                first_name=first_name,
                last_name=last_name,
                role='advisor',
                password=password
            )
            
            messages.success(request, f'✅ Advisor {advisor.get_full_name()} created successfully!')
            return redirect('advisor_list')
            
        except Exception as e:
            messages.error(request, f'❌ Error creating advisor: {str(e)}')
            return redirect('advisor_list')
    
    return render(request, 'advisor_management/create_advisor.html')

@user_passes_test(superuser_required)
def delete_advisor(request, advisor_id):
    """Delete advisor"""
    advisor = get_object_or_404(User, id=advisor_id, role='advisor')
    
    if request.method == 'POST':
        advisor_name = advisor.get_full_name()
        advisor_email = advisor.email
        advisor.delete()
        messages.success(request, f'🗑️ Advisor {advisor_name} ({advisor_email}) deleted successfully!')
        return redirect('advisor_list')
    
    return render(request, 'advisor_management/delete_advisor.html', {'advisor': advisor})

@user_passes_test(superuser_required)
def reset_password(request, advisor_id):
    """Reset advisor password"""
    advisor = get_object_or_404(User, id=advisor_id, role='advisor')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate password input
        if not new_password:
            messages.error(request, '❌ Password is required!')
            return render(request, 'advisor_management/reset_password.html', {'advisor': advisor})
        
        if len(new_password) < 8:
            messages.error(request, '❌ Password must be at least 8 characters long!')
            return render(request, 'advisor_management/reset_password.html', {'advisor': advisor})
        
        if new_password != confirm_password:
            messages.error(request, '❌ Passwords do not match!')
            return render(request, 'advisor_management/reset_password.html', {'advisor': advisor})
        
        # Set new password
        advisor.set_password(new_password)
        advisor.save()
        
        messages.success(
            request, 
            f'🔑 Password successfully reset for {advisor.get_full_name()}!'
        )
        return redirect('advisor_list')
    
    return render(request, 'advisor_management/reset_password.html', {'advisor': advisor})

@user_passes_test(superuser_required)
def toggle_advisor_status(request, advisor_id):
    """Toggle advisor active status"""
    advisor = get_object_or_404(User, id=advisor_id, role='advisor')
    
    advisor.is_active = not advisor.is_active
    advisor.save()
    
    status = "activated" if advisor.is_active else "deactivated"
    messages.success(request, f'✅ Advisor {advisor.get_full_name()} {status} successfully!')
    
    return redirect('advisor_list')

@user_passes_test(superuser_required)
def advisor_stats(request):
    """Get advisor statistics as JSON"""
    advisors = User.objects.filter(role='advisor')
    total = advisors.count()
    active = advisors.filter(is_active=True).count()
    inactive = total - active
    
    return JsonResponse({
        'total_advisors': total,
        'active_advisors': active,
        'inactive_advisors': inactive
    })