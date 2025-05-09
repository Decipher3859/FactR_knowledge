PROJECT_PATH="/home/damn/apprehendData/01_Projekte/FactR"
VAULT_PATH="/$PROJECT_PATH/FactR_vault"
CHATGPT_URL="https://chat.openai.com"

code "$PROJECT_PATH"

obsidian "$VAULT_PATH" &

firefor "$CHATGPT_URL" &
