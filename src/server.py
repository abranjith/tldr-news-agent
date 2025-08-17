"""Flask web server for browsing news reports."""

from pathlib import Path
from typing import Optional
from datetime import datetime
import markdown
from flask import Flask, render_template, request, send_from_directory, abort

from .config_loader import ConfigLoader

app = Flask(__name__)

# Initialize config loader
config_loader = ConfigLoader()


@app.template_filter('timestamp_to_date')
def timestamp_to_date(timestamp: float) -> str:
    """Convert timestamp to readable date format."""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M')
    except (ValueError, OSError):
        return 'Unknown'


@app.template_filter('file_size')
def file_size(size_bytes: int) -> str:
    """Convert file size in bytes to human readable format."""
    try:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    except (ValueError, TypeError):
        return 'Unknown'


def get_reports_directory(dir_path: Optional[str] = None) -> Path:
    """Get the reports directory path from config or parameter."""
    if dir_path:
        # Set it as absolute path and check if it exists
        return Path(dir_path)
    
    output_config = config_loader.get_output_config()
    directory = output_config.get('directory', './reports')
    return Path(directory).resolve()


def get_report_files(reports_dir: Path) -> list[dict]:
    """Get all report files from the directory."""
    if not reports_dir.exists():
        return []
    
    files = []
    for file in reports_dir.glob('*.md'):
        stat = file.stat()
        files.append({
            'name': file.stem,  # filename without extension
            'filename': file.name,  # full filename with extension
            'path': file,
            'size': stat.st_size,
            'modified_time': stat.st_mtime
        })
    
    # Sort files by modification time (newest first)
    files.sort(key=lambda x: x['modified_time'], reverse=True)
    return files


@app.route('/')
def index():
    """Index page that lists all report files."""
    dir_path = request.args.get('dir_path').strip() if request.args.get('dir_path') else None
    print(dir_path)
    
    try:
        reports_dir = get_reports_directory(dir_path)
        files = get_report_files(reports_dir)
        
        return render_template(
            'index.html',
            files=files,
            directory=str(reports_dir),
            total_files=len(files)
        )
    except Exception as e:
        return render_template(
            'error.html',
            error=f"Error accessing reports directory: {str(e)}"
        ), 500


@app.route('/<filename>')
def serve_file(filename: str):
    """Serve individual report files."""
    dir_path = request.args.get('dir_path').strip() if request.args.get('dir_path') else None
    
    try:
        reports_dir = get_reports_directory(dir_path)
        
        # Check if file exists
        file_path = reports_dir / filename
        if not file_path.exists() or not file_path.is_file():
            abort(404)
        
        # If it's a markdown file and client prefers HTML rendering
        if filename.endswith('.md') and request.args.get('format') != 'raw':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert markdown to HTML
            html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
            
            return render_template(
                'report.html',
                filename=filename,
                title=file_path.stem.replace('_', ' ').title(),
                content=html_content,
                file_path=file_path,
                reports_dir=reports_dir
            )
        
        return send_from_directory(reports_dir, filename)
    except Exception as e:
        return render_template(
            'error.html',
            error=f"Error serving file: {str(e)}"
        ), 500


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return {'status': 'healthy', 'message': 'TL;DR News Agent server is running'}


@app.errorhandler(404)
def not_found(error):
    """Custom 404 page."""
    return render_template('error.html', error='File not found'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
