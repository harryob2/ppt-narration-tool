# Vercel Deployment Checklist

## Pre-Deployment Checklist

- [ ] All files are in the correct locations:
  - [ ] `api/app.py` - Main Flask application
  - [ ] `api/templates/` - HTML templates
  - [ ] `api/static/` - Static files (including mic.png)
  - [ ] `requirements.txt` - Python dependencies
  - [ ] `vercel.json` - Vercel configuration

- [ ] Dependencies are correct:
  - [ ] All required packages in `requirements.txt`
  - [ ] No duplicate entries
  - [ ] Compatible versions

- [ ] Code is serverless-compatible:
  - [ ] No file system operations (using in-memory storage)
  - [ ] No persistent sessions
  - [ ] Proper error handling

## Deployment Steps

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy the application**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new
   - Confirm deployment settings
   - Wait for build to complete

## Post-Deployment Verification

- [ ] Check the deployment URL works
- [ ] Test the health endpoint: `https://your-app.vercel.app/health`
- [ ] Test file upload functionality
- [ ] Verify download functionality

## Troubleshooting Common Issues

### FUNCTION_INVOCATION_FAILED Error

1. **Check Vercel Function Logs**:
   - Go to Vercel Dashboard
   - Select your project
   - Go to Functions tab
   - Check the logs for specific error messages

2. **Common Causes**:
   - Missing dependencies in `requirements.txt`
   - File size too large (max 50MB)
   - Import errors
   - File path issues

3. **Solutions**:
   - Add missing dependencies to `requirements.txt`
   - Reduce file size limits
   - Check import paths
   - Verify file structure

### Import Errors

- Ensure all imports are correct
- Check that `api/app.py` can find templates and static files
- Verify Python version compatibility (3.11)

### File Upload Issues

- Check file size limits
- Verify supported file types
- Ensure proper error handling in the code

## Local Testing

Before deploying, test locally:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**:
   ```bash
   python api/app.py
   ```

3. **Test endpoints**:
   ```bash
   python test_local.py
   ```

## Environment Variables

If needed, set environment variables in Vercel Dashboard:
- Go to Project Settings
- Environment Variables section
- Add any required variables

## Monitoring

After deployment:
- Monitor function execution times
- Check for memory usage issues
- Watch for timeout errors
- Monitor error rates 