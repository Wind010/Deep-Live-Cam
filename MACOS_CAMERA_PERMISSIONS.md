# macOS Camera Permission Fix

## Problem
On macOS, OpenCV requires explicit camera permissions to access the webcam. When Deep-Live-Cam tries to initialize the camera without permissions, it fails with repeated error messages:

```
OpenCV: not authorized to capture video (status 0), requesting...
OpenCV: camera failed to properly initialize!
```

## Solution
The application has been updated to:

1. **Detect permission issues early** - Check camera permissions before attempting to use the camera
2. **Provide clear instructions** - Display step-by-step guidance on how to grant permissions
3. **Avoid permission spam** - Don't repeatedly probe cameras during startup

## How to Grant Camera Permissions

### Method 1: System Settings (Recommended)
1. Open **System Settings** (or System Preferences on older macOS)
2. Go to **Privacy & Security** → **Camera**
3. Enable camera access for your terminal application:
   - Terminal.app
   - iTerm.app
   - Or your Python executable

### Method 2: Reset Permissions
If your terminal doesn't appear in the camera permissions list:

1. Close the Deep-Live-Cam application
2. Open Terminal and run:
   ```bash
   tccutil reset Camera
   ```
3. Restart the application - it will prompt for camera access

### Method 3: Run from App Bundle
Some users prefer running Python from an application bundle that already has camera permissions. This can be useful for development environments.

## Technical Details

### Changes Made

#### `modules/video_capture.py`
- Added `_check_macos_camera_permission()` method to detect permission status
- Modified `start()` method to check permissions on macOS before initializing camera
- Displays helpful error message with instructions when permissions are missing
- Uses `cv2.CAP_AVFOUNDATION` backend explicitly for macOS compatibility

#### `modules/ui.py`
- Updated `get_available_cameras()` to avoid probing cameras on startup
- Returns default camera indices without testing to prevent permission spam
- Validation happens only when user actually starts the live preview

## Testing

You can test the camera permission handling with:

```bash
./test_camera_fix.py
```

This will check if camera permissions are properly configured and provide guidance if not.

## Troubleshooting

**Still getting permission errors?**
- Make sure you've restarted the application after granting permissions
- Check that the correct application is enabled in Camera settings
- Some security software may block camera access - check your security settings

**Camera works in other apps but not Deep-Live-Cam?**
- Different Python installations may need separate permissions
- Try running with the full Python path: `/usr/local/bin/python3 run.py`

**Using a virtual environment?**
- The permission is tied to the Python executable
- You may need to grant permission to the venv's Python binary

## Additional Resources

For more information about macOS camera permissions:
- [Apple's Privacy Documentation](https://support.apple.com/guide/mac-help/control-access-to-your-camera-mchlf6d108da/mac)
- [OpenCV Camera Access on macOS](https://github.com/opencv/opencv/issues)
