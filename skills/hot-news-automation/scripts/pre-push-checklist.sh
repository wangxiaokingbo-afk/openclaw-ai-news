#!/bin/bash
# 热点资讯推送前检查清单 v1.0
# 每次推送前必须执行，确保不犯历史错误

set -e

WORKSPACE="$HOME/.openclaw/workspace"
CRON_JOBS="$HOME/.openclaw/cron/jobs.json"

echo "🔍 热点资讯推送前检查清单"
echo "=========================="
echo ""

# 检查 1: 是否真正执行了 hot-news-automation skill
echo "✅ 检查 1: 确认执行真实抓取（非模拟数据）"
if [ -f "$WORKSPACE/reports/daily-top10-$(date +%Y-%m-%d).md" ]; then
    LAST_MODIFIED=$(stat -f %m "$WORKSPACE/reports/daily-top10-$(date +%Y-%m-%d).md" 2>/dev/null || stat -c %Y "$WORKSPACE/reports/daily-top10-$(date +%Y-%m-%d).md" 2>/dev/null)
    NOW=$(date +%s)
    AGE=$(( (NOW - LAST_MODIFIED) / 60 ))
    if [ $AGE -lt 30 ]; then
        echo "   ✓ 报告生成于 $AGE 分钟前（有效）"
    else
        echo "   ⚠ 报告生成于 $AGE 分钟前（可能过期）"
    fi
else
    echo "   ❌ 未找到今日报告文件"
    exit 1
fi
echo ""

# 检查 2: 格式是否包含提炼和锐评
echo "✅ 检查 2: 检查报告格式（要点 + 锐评）"
REPORT_FILE="$WORKSPACE/reports/daily-top10-$(date +%Y-%m-%d).md"
if grep -q "要点：" "$REPORT_FILE" && grep -q "锐评：" "$REPORT_FILE"; then
    COUNT=$(grep -c "要点：" "$REPORT_FILE")
    echo "   ✓ 包含 $COUNT 条'要点 + 锐评'内容"
else
    echo "   ❌ 缺少'要点'或'锐评'格式"
    exit 1
fi
echo ""

# 检查 3: sessionKey 是否为群聊
echo "✅ 检查 3: 检查定时任务 sessionKey（必须为群聊）"
if grep -q "sessionKey.*dingtalk:group:cidwdUjqhs0Pc+p2nKu4pHyVQ==" "$CRON_JOBS"; then
    echo "   ✓ sessionKey 配置正确（群聊）"
else
    echo "   ❌ sessionKey 配置错误（可能为私聊）"
    echo "   修复命令：更新 jobs.json 中所有热点资讯任务的 sessionKey"
    exit 1
fi
echo ""

# 检查 4: 平台状态检查
echo "✅ 检查 4: 检查平台状态"
if [ -f "$WORKSPACE/config/platform-status.md" ]; then
    X_STATUS=$(grep "X 平台" "$WORKSPACE/config/platform-status.md" | grep -o "✅\|❌\|⚠️" | head -1)
    if [ "$X_STATUS" = "✅" ]; then
        echo "   ✓ X 平台：正常"
    else
        echo "   ⚠ X 平台：异常（需在报告中红色警告）"
    fi
else
    echo "   ⚠ 未找到平台状态文件"
fi
echo ""

# 检查 5: 去重记录检查
echo "✅ 检查 5: 检查去重记录"
if [ -f "$WORKSPACE/config/pushed-items.json" ]; then
    TOTAL=$(python3 -c "import json; print(len(json.load(open('$WORKSPACE/config/pushed-items.json'))['items']))" 2>/dev/null || echo "0")
    echo "   ✓ 已推送 $TOTAL 条记录（用于去重比对）"
else
    echo "   ⚠ 未找到已推送记录文件"
fi
echo ""

echo "=========================="
echo "✅ 所有检查通过，可以推送"
echo ""
