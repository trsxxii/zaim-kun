# !!!!
# 実行前に必ずDockerを立ち上げること
# !!!!

# ==== 変数を定義 ====
$ProjectId = "adept-bond-386013"                        # Google Cloud プロジェクト ID
$Region = "asia-northeast1"                             # Cloud Run サービスのリージョン
$RepositoryName = "zaim-checker-repo"                   # Artifact Registry のリポジトリ名
$ImageName = "zaim-checker"                             # Docker イメージの名前
$Tag = "latest"                                         # Docker イメージのタグ
$JobName = "zaim-checker-run-job"                       # Cloud Run Jobs のジョブ名
$EnvSecretName = "projects/741240541320/secrets/zaim-checker-secret"            # Secret Manager に登録された .env シークレット名
$SaSecretName = "projects/741240541320/secrets/zaim-checker-service-account"    # Secret Manager に登録されたサービスアカウント JSON シークレット名
$Image = "$Region-docker.pkg.dev/$ProjectId/$RepositoryName/${ImageName}:$Tag"

# ==== 初期セットアップ ====
Write-Host "Setting up Google Cloud project..."
gcloud config set project $ProjectId
gcloud config set run/region $Region

# ==== Docker イメージをビルド ====
Write-Host "Building Docker image..."
docker build -t $Image .

# ==== Artifact Registry にイメージをプッシュ ====
Write-Host "Authenticating Docker to Artifact Registry..."
gcloud auth configure-docker "$Region-docker.pkg.dev"

Write-Host "Pushing Docker image to Artifact Registry..."
docker push $Image

# ==== Cloud Run Jobs のジョブを更新 & 即時実行 ====
gcloud run jobs update $JobName `
    --execute-now `
    --image $Image `
    --set-secrets "/etc/secrets/env/.env=${EnvSecretName}:latest" `
    --set-secrets "/etc/secrets/service-account/service-account.json=${SaSecretName}:latest" `

Write-Host "Deployment completed! 🚀"
