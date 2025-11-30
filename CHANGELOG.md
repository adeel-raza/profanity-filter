# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2025-11-30

### Fixed
- **Subtitle alignment issues**: Simplified subtitle processing to prevent timing misalignment when profanity segments are removed from early parts of videos
  - Removed complex subtitle clipping logic that caused subtitles to appear late
  - Subtitles that overlap with removed segments are now removed entirely instead of being clipped
  - Fixed issue where non-profane subtitles were disappearing incorrectly
  - Improved timestamp adjustment accuracy for remaining subtitles

### Changed
- Simplified subtitle processing logic for better reliability
- Both SRT and VTT subtitle processing now use consistent overlap removal approach

## [2.0.0] - 2025-11-30

### Added
- **Phrase detection**: Added detection for complete profanity phrases, not just individual words
  - Now detects "fuck you", "shit head", "ass hole", "mother fucker", and other common profanity combinations
  - Prevents partial removal where only part of a phrase gets filtered (e.g., removing "fuck" but leaving "you")

### Fixed
- **Incomplete profanity removal**: Fixed issue where profanity phrases like "fuck you" were only partially filtered, leaving residual sound
- **Enhanced detection reliability**: Improved profanity detection with dialog enhancement, quality checking, and automatic model upgrading
- **Web interface detection**: Updated Gradio app to use the same enhanced detection as CLI

### Changed
- Increased default phrase merging gap to 2.0 seconds for better phrase detection
- Added 150ms padding around detected segments for complete removal
- CLI and web interface now use consistent detection parameters

## [1.5.0] - 2025-11-30

### Fixed
- **Hugging Face Spaces deployment**: Fixed configuration errors preventing proper deployment
  - Corrected malformed YAML configuration in README.md
  - Fixed SyntaxErrors from non-ASCII characters (em dashes, en dashes, etc.)
  - Fixed bare markdown text causing Python parsing errors
  - Updated to use AudioProfanityDetectorFast for better performance

### Changed
- **UI improvements**: Enhanced user interface for better user experience
  - Moved upload section to top of interface for immediate access
  - Changed to side-by-side layout (inputs left, outputs right)
  - Improved visual hierarchy and user flow

### Technical
- Switched from AudioProfanityDetector to AudioProfanityDetectorFast
- Added dialog enhancement, auto-upgrade, and quality checking features

## [1.2.0] - 2025-11-30

### Fixed
- **False positive word matching**: Changed from substring matching to exact whole-word matching
  - Prevents false positives like "house" matching "whore"
  - Prevents "hour" and "shouldn't" from being incorrectly detected as profanity
  - Improved accuracy of profanity detection

### Changed
- Updated word matching logic to use exact matches only
- Improved documentation to reflect improved accuracy

## [1.0.0] - 2025-01-XX

### Added
- Initial release of Movie Profanity Filter
- AI-powered audio transcription using OpenAI Whisper
- Comprehensive profanity detection with 1,132+ words
- Automatic video editing with FFmpeg
- Subtitle cleaning and timestamp synchronization
- Batch processing support
- CPU-optimized processing (no GPU required)
- Privacy-first local processing
- Support for SRT and VTT subtitle formats

### Features
- Fast processing (7-15 minutes for 2-hour movie)
- Whole-word matching for accurate detection
- Case-insensitive profanity detection
- Automatic subtitle timestamp adjustment after video cuts
- Manual timestamp removal option
- Multiple Whisper model size options

