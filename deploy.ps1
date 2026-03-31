# Deployment script for Google Cloud Run
write-host "Starting Google Cloud Run Deployment for Green Code Engine..." -ForegroundColor Green

# Ensure gcloud is initialized
write-host "Checking gcloud CLI..." -ForegroundColor Yellow
gcloud --version
if ($LASTEXITCODE -ne 0) {
    write-host "Google Cloud SDK (gcloud) is not installed or not in PATH." -ForegroundColor Red
    write-host "Download it here: https://cloud.google.com/sdk/docs/install" -ForegroundColor Cyan
    exit
}

# Prompt user for project ID
$PROJECT_ID = Read-Host -Prompt "Enter your GCP Project ID"

# Deploy securely
write-host "Deploying to Cloud Run. Please answer any prompts from the Google Cloud CLI." -ForegroundColor Yellow
write-host "NOTE: When asked, allow unauthenticated invocations so the website is public." -ForegroundColor Cyan

gcloud run deploy green-code-engine `
    --source . `
    --project $PROJECT_ID `
    --region us-central1 `
    --allow-unauthenticated

write-host "Deployment process complete!" -ForegroundColor Green
write-host "IMPORTANT: Remember to add your GEMINI_API_KEY as an Environment Variable in the Cloud Run web console." -ForegroundColor Red
