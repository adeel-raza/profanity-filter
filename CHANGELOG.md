# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- Fixed false positive word matching - changed from substring matching to exact whole-word matching
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

