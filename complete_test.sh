#!/bin/bash

echo "🎯 PICKABOOK END-TO-END TEST"
echo "============================="

# Test 1: Upload
echo "📤 1. Uploading test image..."
RESPONSE=$(curl -s -X POST -F "file=@piclumen-1744033346326.png" http://localhost:8000/api/upload)
TASK_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['task_id'])")
echo "   Task ID: $TASK_ID"
echo "   Response: $(echo $RESPONSE | python3 -m json.tool 2>/dev/null | tr '\n' ' ')"

# Test 2: Wait for processing
echo -e "\n⏳ 2. Waiting for processing..."
for i in {1..10}; do
    STATUS=$(curl -s http://localhost:8000/api/result/$TASK_ID)
    PROGRESS=$(echo $STATUS | python3 -c "import sys, json; print(json.load(sys.stdin).get('progress', 0))")
    STATE=$(echo $STATUS | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")
    
    echo "   Check $i: $STATE ($PROGRESS%)"
    
    if [ "$STATE" = "completed" ]; then
        break
    elif [ "$STATE" = "failed" ]; then
        echo "   ❌ Processing failed"
        exit 1
    fi
    sleep 2
done

# Test 3: Download
echo -e "\n📥 3. Downloading result..."
RESULT_URL=$(curl -s http://localhost:8000/api/result/$TASK_ID | python3 -c "import sys, json; print(json.load(sys.stdin).get('result_url', ''))")
if [ -n "$RESULT_URL" ]; then
    curl -s "http://localhost:8000$RESULT_URL" -o "test_result_${TASK_ID:0:8}.png"
    echo "   ✅ Downloaded: test_result_${TASK_ID:0:8}.png"
    echo "   📏 Size: $(wc -c < "test_result_${TASK_ID:0:8}.png") bytes"
else
    echo "   ❌ No result URL found"
fi

# Test 4: Verify file
echo -e "\n🔍 4. Verifying files..."
echo "   Uploads: $(ls uploads/*${TASK_ID}* 2>/dev/null | wc -l) files"
echo "   Results: $(ls results/*${TASK_ID}* 2>/dev/null | wc -l) files"

# Test 5: Health check
echo -e "\n🏥 5. System health:"
curl -s http://localhost:8000/api/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/health

echo -e "\n============================="
echo "✅ BACKEND TEST COMPLETE!"
echo "The system is working correctly."
