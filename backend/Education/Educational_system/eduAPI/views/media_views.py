import os
import mimetypes
import urllib.parse
import glob
from django.http import HttpResponse, FileResponse, JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def serve_file(request):
    """
    Endpoint to serve files with proper CORS headers and content type detection
    """
    try:
        file_path = request.GET.get('file', '')
        if not file_path:
            return JsonResponse({'error': 'No file path provided'}, status=400)
        
        # Print the requested file path for debugging
        print(f"Requested file: {file_path}")
        
        # Decode URL-encoded file path
        file_path = urllib.parse.unquote(file_path)
        
        # Clean the file path to prevent directory traversal attacks
        file_path = os.path.normpath(file_path).lstrip('/')
        
        # If file_path starts with 'media/', remove it since MEDIA_ROOT already points to that directory
        if file_path.startswith('media/'):
            file_path = file_path[6:]
        
        # Construct absolute path
        absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
        print(f"Looking for file at absolute path: {absolute_path}")
        
        # Check if file exists and is safe to access
        if not os.path.exists(absolute_path) or not os.path.isfile(absolute_path):
            print(f"File not found at {absolute_path}")
            
            # Try to find similar files in the same directory as a fallback
            try:
                directory = os.path.dirname(absolute_path)
                filename = os.path.basename(absolute_path)
                
                # Extract base name without extension for more flexible matching
                name_parts = os.path.splitext(filename)
                base_name = name_parts[0].split('_')[0]  # Get the first part before any underscore
                extension = name_parts[1] if len(name_parts) > 1 else ''
                
                print(f"Searching for similar files with base name: {base_name} and extension: {extension}")
                
                # Look for files with similar names
                if os.path.exists(directory):
                    similar_files = glob.glob(f"{directory}/{base_name}*{extension}")
                    if similar_files:
                        # Use the first matching file
                        absolute_path = similar_files[0]
                        print(f"Found similar file as fallback: {absolute_path}")
                    else:
                        print(f"No similar files found in {directory}")
                        
                        # List all files in directory for debugging
                        all_files = os.listdir(directory)
                        print(f"Files in directory: {all_files}")
                        
                        return JsonResponse({
                            'error': 'File not found', 
                            'requested': file_path,
                            'available_files': all_files
                        }, status=404)
                else:
                    print(f"Directory {directory} does not exist")
                    return JsonResponse({'error': f'Directory not found: {directory}'}, status=404)
            except Exception as search_err:
                print(f"Error searching for similar files: {str(search_err)}")
                return JsonResponse({'error': 'File not found and error searching for alternatives'}, status=404)
        
        print(f"Will serve file from: {absolute_path}")
        
        # Determine the content type based on file extension
        content_type, encoding = mimetypes.guess_type(absolute_path)
        if not content_type:
            # Default to binary application/octet-stream if type can't be determined
            content_type = 'application/octet-stream'
            
        print(f"Detected content type: {content_type}")
        
        # Get filename for Content-Disposition header
        filename = os.path.basename(absolute_path)
        
        # Use FileResponse which is optimized for file serving
        response = FileResponse(open(absolute_path, 'rb'), content_type=content_type)
        
        # Set appropriate Content-Disposition
        # For PDFs and images, we can use 'inline' to display in browser
        if content_type in ['application/pdf', 'image/jpeg', 'image/png', 'image/gif']:
            response['Content-Disposition'] = f'inline; filename="{filename}"'
        else:
            # For other files, suggest download
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Add CORS headers
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        print(f"Successfully serving file from {absolute_path}")
        return response
        
    except Exception as e:
        print(f"Error serving file: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'message': 'Error serving file, see server logs for details'
        }, status=500)

# Keep the old function name for backward compatibility
serve_pdf = serve_file 

@api_view(['GET'])
@permission_classes([AllowAny])
def direct_download(request, filename):
    """
    Direct download endpoint for files by base name
    """
    try:
        print(f"Direct download requested for: {filename}")
        
        # Search for files with this base name in lesson_files directory
        lesson_files_dir = os.path.join(settings.MEDIA_ROOT, 'lesson_files')
        
        # Split filename to get base name and extension
        if '.' in filename:
            base_name, extension = filename.split('.', 1)
        else:
            base_name = filename
            extension = ''
        
        print(f"Looking for files with base name: {base_name}, extension: {extension}")
        
        # Look for matching files
        matching_files = []
        if os.path.exists(lesson_files_dir):
            # If extension is provided, look for exact extension
            if extension:
                pattern = f"{lesson_files_dir}/{base_name}*.{extension}"
                matching_files = glob.glob(pattern)
                
            # If no matching files or no extension provided, try any extension
            if not matching_files:
                pattern = f"{lesson_files_dir}/{base_name}*"
                matching_files = glob.glob(pattern)
        
        # If we found matches, serve the first one
        if matching_files:
            absolute_path = matching_files[0]
            print(f"Found matching file: {absolute_path}")
            
            # Determine content type
            content_type, encoding = mimetypes.guess_type(absolute_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Get actual filename for the Content-Disposition header
            actual_filename = os.path.basename(absolute_path)
            
            # Serve the file
            response = FileResponse(open(absolute_path, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{actual_filename}"'
            response['X-Content-Type-Options'] = 'nosniff'
            
            # Add CORS headers
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            
            print(f"Serving file: {absolute_path}")
            return response
        else:
            # List all available files for debugging
            available_files = []
            if os.path.exists(lesson_files_dir):
                available_files = os.listdir(lesson_files_dir)
            
            print(f"No matching files found. Available files: {available_files}")
            return JsonResponse({
                'error': 'File not found', 
                'requested': filename,
                'available_files': available_files
            }, status=404)
            
    except Exception as e:
        print(f"Error in direct_download: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500) 