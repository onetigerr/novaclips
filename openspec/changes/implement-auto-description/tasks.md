## 1. Processing Updates
- [ ] 1.1 Modify `Uniquifier` to save `.srt` file to `clean_dir` (do not delete temp subs).

## 2. Content Preparation Logic
- [ ] 2.1 Implement `FrameExtractor` (ffmpeg: extract 4 frames).
- [ ] 2.2 Implement `CollageMaker` (Pillow: merge frames horizontally).
- [ ] 2.3 Implement `DescriptionGenerator` (Groq API: Vision + Text -> Description).
- [ ] 2.4 Implement `FileRenamer` (Rename OS file + Update DB path).

## 3. Pipeline Integration
- [ ] 3.1 Implement `novaclips prepare` command.
- [ ] 3.2 Update `novaclips upload` to use metadata from DB.

## 4. Verification
- [ ] 4.1 Verify `prepare` flow on video without subs.
- [ ] 4.2 Verify `prepare` flow on video with subs.
- [ ] 4.3 Verify `upload` populates description field.
