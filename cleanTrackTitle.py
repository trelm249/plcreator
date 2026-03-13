import os
import re
import argparse
from pathlib import Path
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.id3 import ID3NoHeaderError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_track_title(title, patterns_to_remove=None):
    """Remove specified patterns from track title."""
    if not title:
        return title
    
    if patterns_to_remove is None:
        patterns_to_remove = [
            r'\s*\(2007 Remaster\)',
            r'\s*\(2009 Remaster\)',
            r'\s*\(Remaster\)',
            r'\s*\(Remastered\)',
            r'\s*\(2007 Remastered\)',
            r'\s*\(2007 Remastered Version\)',
            r'\s*\(Remaster 2007\)',
            r'\s*\(Album Version\)',
            r'\s*\(Digital Remaster\)',
            r'\s*\(New Stereo Mix\)',
            r'\s*\(2007 Stereo Mix\)',
            r'\s*\(Digitally Remastered\)'
        ]
    
    cleaned_title = title
    for pattern in patterns_to_remove:
        cleaned_title = re.sub(pattern, '', cleaned_title, flags=re.IGNORECASE)
    
    # Clean up any extra whitespace
    cleaned_title = re.sub(r'\s+', ' ', cleaned_title).strip()
    
    return cleaned_title

def process_flac_file(file_path, dry_run=False):
    """Process FLAC file to clean track title."""
    try:
        audio = FLAC(file_path)
        
        if 'TITLE' in audio:
            original_title = audio['TITLE'][0]
            cleaned_title = clean_track_title(original_title)
            
            if original_title != cleaned_title:
                logger.info(f"FLAC: {file_path}")
                logger.info(f"  Original: {original_title}")
                logger.info(f"  Cleaned:  {cleaned_title}")
                
                if not dry_run:
                    audio['TITLE'] = [cleaned_title]
                    audio.save()
                    logger.info("  ✓ Updated")
                else:
                    logger.info("  (dry run - not updated)")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error processing FLAC file {file_path}: {e}")
        return False

def process_aac_file(file_path, dry_run=False):
    """Process AAC/M4A file to clean track title."""
    try:
        audio = MP4(file_path)
        
        if '\xa9nam' in audio:  # Title tag in MP4
            original_title = audio['\xa9nam'][0]
            cleaned_title = clean_track_title(original_title)
            
            if original_title != cleaned_title:
                logger.info(f"AAC: {file_path}")
                logger.info(f"  Original: {original_title}")
                logger.info(f"  Cleaned:  {cleaned_title}")
                
                if not dry_run:
                    audio['\xa9nam'] = [cleaned_title]
                    audio.save()
                    logger.info("  ✓ Updated")
                else:
                    logger.info("  (dry run - not updated)")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error processing AAC file {file_path}: {e}")
        return False

def scan_directory(directory, dry_run=False, recursive=True):
    """Scan directory for music files and clean track titles."""
    directory = Path(directory)
    
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory}")
        return
    
    logger.info(f"Scanning directory: {directory}")
    logger.info(f"Recursive: {recursive}, Dry run: {dry_run}")
    
    # File extensions to process
    extensions = {'.flac', '.m4a', '.aac', '.mp4'}
    
    files_processed = 0
    files_updated = 0
    
    # Get files to process
    if recursive:
        files = [f for f in directory.rglob('*') if f.suffix.lower() in extensions and f.is_file()]
    else:
        files = [f for f in directory.iterdir() if f.suffix.lower() in extensions and f.is_file()]
    
    logger.info(f"Found {len(files)} music files to process")
    
    for file_path in files:
        files_processed += 1
        
        # Progress indicator
        if files_processed % 100 == 0:
            logger.info(f"Processed {files_processed}/{len(files)} files...")
        
        try:
            if file_path.suffix.lower() == '.flac':
                if process_flac_file(file_path, dry_run):
                    files_updated += 1
            elif file_path.suffix.lower() in {'.m4a', '.aac', '.mp4'}:
                if process_aac_file(file_path, dry_run):
                    files_updated += 1
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
    
    logger.info(f"Scan complete!")
    logger.info(f"Files processed: {files_processed}")
    logger.info(f"Files updated: {files_updated}")

def main():
    parser = argparse.ArgumentParser(
        description='Remove "(2007 Remaster)" and similar strings from music file track titles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanTrackTitle.py /path/to/music --dry-run
  python cleanTrackTitle.py /path/to/music --recursive
  python cleanTrackTitle.py /path/to/music --no-recursive
  python cleanTrackTitle.py /path/to/album/folder
        """
    )
    
    parser.add_argument('directory', help='Directory containing music files')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--recursive', action='store_true', default=True,
                       help='Recursively scan subdirectories (default)')
    parser.add_argument('--no-recursive', dest='recursive', action='store_false',
                       help='Only scan the specified directory, not subdirectories')
    
    args = parser.parse_args()
    
    # Install required packages check
    try:
        import mutagen
    except ImportError:
        logger.error("This script requires the 'mutagen' package.")
        logger.error("Install it with: pip install mutagen")
        return
    
    scan_directory(args.directory, args.dry_run, args.recursive)

if __name__ == "__main__":
    main()
