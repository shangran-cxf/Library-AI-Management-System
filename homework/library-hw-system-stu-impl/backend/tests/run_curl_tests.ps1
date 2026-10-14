# 图书管理系统作业 - 接口 curl 实测脚本
# 用法：先启动后端（python main.py，监听 8001），再执行本脚本
# 作用：对任务一（续借）与任务二（评论评分）的新接口逐一 curl 调用，并把真实返回写入《接口测试记录.md》

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$base = "http://localhost:8001"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$outFile = Join-Path $root "接口测试记录.md"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$tmpPayload = Join-Path $env:TEMP "hw_curl_payload.json"

$lines = New-Object System.Collections.Generic.List[string]
function W($s) { $lines.Add([string]$s) | Out-Null }

function Invoke-Curl($title, $method, $url, $jsonBody) {
    W "### $title"
    W ""
    W '```bash'
    if ($jsonBody) {
        [System.IO.File]::WriteAllText($tmpPayload, $jsonBody, $utf8)
        W "curl -X $method `"$url`" -H `"Content-Type: application/json`" -d '$jsonBody'"
        W '```'
        $resp = & curl.exe -s -X $method $url -H "Content-Type: application/json" --data-binary "@$tmpPayload"
    } else {
        W "curl -X $method `"$url`""
        W '```'
        $resp = & curl.exe -s -X $method $url
    }
    W ""
    W "**响应：**"
    W ""
    W '```json'
    W ($resp -join "`n")
    W '```'
    W ""
    Write-Host "== $title"
    Write-Host ($resp -join "`n")
    return ($resp -join "`n")
}

W "# 图书管理系统作业 · 接口 curl 实测记录"
W ""
W "> 后端：``python main.py``（http://localhost:8001）  "
W "> 说明：以下命令与返回均为真实执行结果，用于验证任务一（续借）与任务二（评论评分）。"
W ""
W "---"
W ""
W "## 任务一：续借功能"
W ""

Invoke-Curl "1. 登录 zhangsan，获取 user_id" "POST" "$base/api/login" '{"username":"zhangsan","password":"123456"}' | Out-Null
Invoke-Curl "2. 查询 zhangsan 当前在借记录（取 record_id）" "GET" "$base/api/borrow/records/1?status=borrowing" $null | Out-Null
Invoke-Curl "3. 续借《三体》对应记录（record_id=1，默认延长 30 天）" "POST" "$base/api/renew" '{"record_id":1}' | Out-Null
Invoke-Curl "4. 再次续借同一条记录（record_id=1，显式延长 7 天）" "POST" "$base/api/renew" '{"record_id":1,"extend_days":7}' | Out-Null
Invoke-Curl "5. 先归还记录 2，制造'已归还'场景" "POST" "$base/api/return" '{"record_id":2}' | Out-Null
Invoke-Curl "6. 对已归还记录续借 → 应被拒绝（业务错误）" "POST" "$base/api/renew" '{"record_id":2}' | Out-Null
Invoke-Curl "7. 对不存在的记录续借 → 应被拒绝（业务错误）" "POST" "$base/api/renew" '{"record_id":99999}' | Out-Null

W "---"
W ""
W "## 任务二：图书评论与评分"
W ""

Invoke-Curl "8. 登录 lisi，获取 user_id" "POST" "$base/api/login" '{"username":"lisi","password":"123456"}' | Out-Null
Invoke-Curl "9. 按书名检索《三体》，解析 book_id" "GET" "$base/api/books/search?keyword=%E4%B8%89%E4%BD%93" $null | Out-Null
Invoke-Curl "10. zhangsan 为《三体》评分 5 分并写评论" "POST" "$base/api/books/1/reviews" '{"user_id":1,"rating":5,"comment":"太好看了"}' | Out-Null
Invoke-Curl "11. lisi 为《三体》评分 4 分并写评论" "POST" "$base/api/books/1/reviews" '{"user_id":2,"rating":4,"comment":"不错，值得一读"}' | Out-Null
Invoke-Curl "12. 查看《三体》全部评论与平均评分" "GET" "$base/api/books/1/reviews" $null | Out-Null
Invoke-Curl "13. 评分越界（6 分）→ 应被后端拒绝（业务错误）" "POST" "$base/api/books/1/reviews" '{"user_id":1,"rating":6,"comment":"越界评分"}' | Out-Null

[System.IO.File]::WriteAllLines($outFile, $lines, $utf8)
Write-Host ""
Write-Host "已写入：$outFile"
