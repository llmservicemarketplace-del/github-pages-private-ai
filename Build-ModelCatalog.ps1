$ErrorActionPreference = "Stop"

$catalogPath = Join-Path $PWD "catalog.json"

$headers = @{
    "User-Agent" = "PrivateAI-Catalog-Builder"
    "Accept"     = "application/json"
}

$models = @(
    @{
        id="light-qwen"; tier="Light"; family="Qwen"
        label="Qwen 2.5 3B - Light"
        repo="Qwen/Qwen2.5-3B-Instruct-GGUF"
        ram=4.0; gated=$false
        license="Qwen License"
        license_url="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF"
        blurb="Fast everyday assistant for questions, writing, and explanations."
    },
    @{
        id="light-gemma"; tier="Light"; family="Gemma"
        label="Gemma 3 1B - Light"
        repo="unsloth/gemma-3-1b-it-GGUF"
        ram=4.0; gated=$true
        license="Gemma Terms"
        license_url="https://ai.google.dev/gemma/terms"
        blurb="Compact Google model for everyday writing and general assistance."
    },
    @{
        id="light-llama"; tier="Light"; family="Llama"
        label="Llama 3.2 1B - Light"
        repo="unsloth/Llama-3.2-1B-Instruct-GGUF"
        ram=4.0; gated=$true
        license="Llama Community License"
        license_url="https://www.llama.com/llama-downloads/"
        blurb="Small multilingual assistant for lightweight local use."
    },
    @{
        id="light-deepseek"; tier="Light"; family="DeepSeek"
        label="DeepSeek R1 Distill 1.5B - Light"
        repo="unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF"
        ram=4.0; gated=$false
        license="MIT"
        license_url="https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
        blurb="Compact reasoning-focused model for basic logic and technical questions."
    },

    @{
        id="standard-qwen"; tier="Standard"; family="Qwen"
        label="Qwen 2.5 7B - Standard"
        repo="bartowski/Qwen2.5-7B-Instruct-GGUF"
        ram=8.0; gated=$false
        license="Qwen License"
        license_url="https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF"
        blurb="Balanced general assistant for most modern computers."
    },
    @{
        id="standard-gemma"; tier="Standard"; family="Gemma"
        label="Gemma 3 4B - Standard"
        repo="unsloth/gemma-3-4b-it-GGUF"
        ram=8.0; gated=$true
        license="Gemma Terms"
        license_url="https://ai.google.dev/gemma/terms"
        blurb="Balanced writing, explanation, and everyday assistant performance."
    },
    @{
        id="standard-llama"; tier="Standard"; family="Llama"
        label="Llama 3.2 3B - Standard"
        repo="unsloth/Llama-3.2-3B-Instruct-GGUF"
        ram=8.0; gated=$true
        license="Llama Community License"
        license_url="https://www.llama.com/llama-downloads/"
        blurb="General-purpose multilingual assistant for everyday local use."
    },
    @{
        id="standard-deepseek"; tier="Standard"; family="DeepSeek"
        label="DeepSeek R1 Distill 7B - Standard"
        repo="unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF"
        ram=8.0; gated=$false
        license="MIT"
        license_url="https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
        blurb="Stronger reasoning and technical assistance for daily professional use."
    },

    @{
        id="advanced-qwen"; tier="Advanced"; family="Qwen"
        label="Qwen 2.5 14B - Advanced"
        repo="bartowski/Qwen2.5-14B-Instruct-GGUF"
        ram=16.0; gated=$false
        license="Qwen License"
        license_url="https://huggingface.co/Qwen/Qwen2.5-14B-Instruct-GGUF"
        blurb="Higher-quality reasoning, writing, coding, and mathematics."
    },
    @{
        id="advanced-gemma"; tier="Advanced"; family="Gemma"
        label="Gemma 3 12B - Advanced"
        repo="unsloth/gemma-3-12b-it-GGUF"
        ram=16.0; gated=$true
        license="Gemma Terms"
        license_url="https://ai.google.dev/gemma/terms"
        blurb="Larger Gemma model for detailed writing and stronger explanations."
    },
    @{
        id="advanced-llama"; tier="Advanced"; family="Llama"
        label="Llama 3.1 8B - Advanced"
        repo="unsloth/Llama-3.1-8B-Instruct-GGUF"
        ram=16.0; gated=$true
        license="Llama Community License"
        license_url="https://www.llama.com/llama-downloads/"
        blurb="Strong general-purpose multilingual assistant for capable systems."
    },
    @{
        id="advanced-deepseek"; tier="Advanced"; family="DeepSeek"
        label="DeepSeek R1 Distill 14B - Advanced"
        repo="unsloth/DeepSeek-R1-Distill-Qwen-14B-GGUF"
        ram=16.0; gated=$false
        license="MIT"
        license_url="https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
        blurb="Advanced reasoning and coding assistance for powerful desktops."
    },

    @{
        id="heavy-qwen"; tier="Heavy"; family="Qwen"
        label="Qwen 2.5 32B - Heavy"
        repo="bartowski/Qwen2.5-32B-Instruct-GGUF"
        ram=32.0; gated=$false
        license="Qwen License"
        license_url="https://huggingface.co/Qwen/Qwen2.5-32B-Instruct-GGUF"
        blurb="Large local model for advanced workstations and complex reasoning."
    },
    @{
        id="heavy-gemma"; tier="Heavy"; family="Gemma"
        label="Gemma 3 27B - Heavy"
        repo="unsloth/gemma-3-27b-it-GGUF"
        ram=32.0; gated=$true
        license="Gemma Terms"
        license_url="https://ai.google.dev/gemma/terms"
        blurb="Large Gemma model intended for high-memory desktop workstations."
    },
    @{
        id="heavy-llama"; tier="Heavy"; family="Llama"
        label="Llama 3.3 70B - Heavy"
        repo="bartowski/Llama-3.3-70B-Instruct-GGUF"
        ram=48.0; gated=$true
        license="Llama Community License"
        license_url="https://www.llama.com/llama-downloads/"
        blurb="Large general-purpose assistant for high-end workstations."
    },
    @{
        id="heavy-deepseek"; tier="Heavy"; family="DeepSeek"
        label="DeepSeek R1 Distill 32B - Heavy"
        repo="unsloth/DeepSeek-R1-Distill-Qwen-32B-GGUF"
        ram=32.0; gated=$false
        license="MIT"
        license_url="https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
        blurb="Large reasoning-focused model for advanced technical work."
    }
)

function Get-GgufFile {
    param(
        [Parameter(Mandatory)]
        [string]$Repo
    )

    Write-Host "Checking $Repo..."

    $apiUrl = "https://huggingface.co/api/models/$Repo"

    try {
        $response = Invoke-RestMethod `
            -Uri $apiUrl `
            -Headers $headers `
            -Method Get
    }
    catch {
        throw "Could not read Hugging Face repository: $Repo"
    }

    $files = @($response.siblings)

    $preferred = $files |
        Where-Object {
            $_.rfilename -match '(?i)Q4_K_M.*\.gguf$'
        } |
        Sort-Object {
            $_.rfilename.Length
        } |
        Select-Object -First 1

    if (-not $preferred) {
        $preferred = $files |
            Where-Object {
                $_.rfilename -match '(?i)Q4.*\.gguf$'
            } |
            Sort-Object {
                $_.rfilename.Length
            } |
            Select-Object -First 1
    }

    if (-not $preferred) {
        throw "No Q4 GGUF file was found in $Repo"
    }

    $filename = $preferred.rfilename

    $fileApi = "https://huggingface.co/api/models/$Repo/tree/main"

    $tree = Invoke-RestMethod `
        -Uri $fileApi `
        -Headers $headers `
        -Method Get

    $fileInfo = $tree |
        Where-Object {
            $_.path -eq $filename
        } |
        Select-Object -First 1

    $sizeBytes = 0

    if ($fileInfo -and $fileInfo.size) {
        $sizeBytes = [double]$fileInfo.size
    }

    return @{
        filename = $filename
        url = "https://huggingface.co/$Repo/resolve/main/$([uri]::EscapeDataString($filename))?download=true"
        size_gb = if ($sizeBytes -gt 0) {
            [math]::Round($sizeBytes / 1GB, 2)
        }
        else {
            0
        }
    }
}

$output = @()

foreach ($model in $models) {
    try {
        $file = Get-GgufFile -Repo $model.repo

        $output += [ordered]@{
            id = $model.id
            tier = $model.tier
            family = $model.family
            label = $model.label
            blurb = $model.blurb
            repo_id = $model.repo
            filename = $file.filename
            url = $file.url
            sha256 = ""
            download_gb = $file.size_gb
            ram_gb = $model.ram
            license = $model.license
            license_url = $model.license_url
            enabled = $true
            platforms = @("windows", "macos")
            gated = [bool]$model.gated
            runtime = "llama.cpp"
            context_length = 8192
            runtime_args = @()
        }

        Write-Host "  Found: $($file.filename)"
    }
    catch {
        Write-Warning $_

        $output += [ordered]@{
            id = $model.id
            tier = $model.tier
            family = $model.family
            label = $model.label
            blurb = $model.blurb
            repo_id = $model.repo
            filename = ""
            url = ""
            sha256 = ""
            download_gb = 0
            ram_gb = $model.ram
            license = $model.license
            license_url = $model.license_url
            enabled = $false
            platforms = @("windows", "macos")
            gated = [bool]$model.gated
            runtime = "llama.cpp"
            context_length = 8192
            runtime_args = @()
        }
    }
}

$catalog = [ordered]@{
    version = 3
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    models = $output
}

$json = $catalog | ConvertTo-Json -Depth 12

[System.IO.File]::WriteAllText(
    $catalogPath,
    $json,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host ""
Write-Host "Catalog written to:"
Write-Host $catalogPath

