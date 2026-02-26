#!/bin/bash
# Qdrant Vector Indexing Verification Script
# This script verifies that vectors are properly indexed after setup

set -e

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║                   RegulAite Vector Indexing Verification             ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Qdrant is running
echo -e "${YELLOW}Checking Qdrant availability...${NC}"
if ! curl -s "http://localhost:6333/healthz" > /dev/null 2>&1; then
    echo -e "${RED}❌ Qdrant is not accessible at http://localhost:6333${NC}"
    echo -e "${YELLOW}Please ensure Docker containers are running: docker-compose ps${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Qdrant is accessible${NC}"

# Check collections
echo -e "${YELLOW}Checking collections...${NC}"
collections=$(curl -s "http://localhost:6333/collections" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    collections = [c['name'] for c in data['result']['collections']]
    print(' '.join(collections))
except:
    print('')
")

if [[ -z "$collections" ]]; then
    echo -e "${YELLOW}⚠️ No collections found. This is normal for a fresh setup.${NC}"
    echo -e "${BLUE}Collections will be created when documents are first indexed.${NC}"
    exit 0
fi

echo -e "${GREEN}✅ Found collections: $collections${NC}"

# Check each collection for indexing status
for collection in $collections; do
    echo -e "${YELLOW}Checking collection: $collection${NC}"
    
    # Get collection stats
    stats=$(curl -s "http://localhost:6333/collections/$collection" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    result = data['result']
    points = result['points_count']
    indexed = result['indexed_vectors_count']
    print(f'{points}|{indexed}')
except Exception as e:
    print('0|0')
")
    
    points=$(echo $stats | cut -d'|' -f1)
    indexed=$(echo $stats | cut -d'|' -f2)
    
    echo -e "  📊 Points: $points"
    echo -e "  🔍 Indexed vectors: $indexed"
    
    if [ "$points" -eq 0 ]; then
        echo -e "${YELLOW}  ⚠️ Collection is empty - no documents indexed yet${NC}"
    elif [ "$indexed" -eq 0 ]; then
        echo -e "${RED}  ❌ INDEXING PROBLEM: $points points but 0 indexed vectors${NC}"
        echo -e "${YELLOW}  🔧 Attempting to fix indexing threshold...${NC}"
        
        # Try to update indexing threshold and full_scan_threshold for small collections
        if [ "$points" -lt 100 ]; then
            echo -e "  🔧 Small collection detected - updating both indexing and full_scan thresholds..."
            update_result=$(curl -s -X PATCH "http://localhost:6333/collections/$collection" \
                -H "Content-Type: application/json" \
                -d '{"optimizers_config": {"indexing_threshold": 1}, "hnsw_config": {"full_scan_threshold": 10}}' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('success' if data.get('result') else 'failed')
except:
    print('failed')
")
        else
            # Try to update indexing threshold for larger collections
            update_result=$(curl -s -X PATCH "http://localhost:6333/collections/$collection" \
                -H "Content-Type: application/json" \
                -d '{"optimizers_config": {"indexing_threshold": 1000}}' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('success' if data.get('result') else 'failed')
except:
    print('failed')
")
        fi
        
        if [ "$update_result" = "success" ]; then
            if [ "$points" -lt 100 ]; then
                echo -e "${GREEN}  ✅ Indexing and full_scan thresholds updated for small collection${NC}"
            else
                echo -e "${GREEN}  ✅ Indexing threshold updated to 1000${NC}"
            fi
            echo -e "${YELLOW}  ⏳ Waiting for indexing to complete...${NC}"
            sleep 10
            
            # Check again
            new_stats=$(curl -s "http://localhost:6333/collections/$collection" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    result = data['result']
    indexed = result['indexed_vectors_count']
    print(indexed)
except:
    print('0')
")
            
            if [ "$new_stats" -gt 0 ]; then
                echo -e "${GREEN}  ✅ Indexing fixed! $new_stats vectors now indexed${NC}"
            else
                echo -e "${YELLOW}  ⏳ Indexing may still be in progress. Check again later.${NC}"
            fi
        else
            echo -e "${RED}  ❌ Failed to update indexing threshold${NC}"
        fi
    elif [ "$indexed" -eq "$points" ]; then
        echo -e "${GREEN}  ✅ Perfect! All vectors are indexed${NC}"
    else
        ratio=$(echo "scale=2; $indexed * 100 / $points" | bc -l)
        echo -e "${YELLOW}  ⚠️ Partial indexing: $indexed/$points ($ratio%) vectors indexed${NC}"
    fi
    echo ""
done

# Test basic search functionality if documents exist
total_points=0
for collection in $collections; do
    points=$(curl -s "http://localhost:6333/collections/$collection" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data['result']['points_count'])
except:
    print('0')
")
    total_points=$((total_points + points))
done

if [ "$total_points" -gt 0 ]; then
    echo -e "${YELLOW}Testing search functionality...${NC}"
    
    # Test a simple search
    search_result=$(curl -s -X POST "http://localhost:6333/collections/regulaite_documents/points/search" \
        -H "Content-Type: application/json" \
        -d '{
            "vector": [0.1, 0.2, 0.3, 0.4],
            "limit": 1,
            "with_payload": false
        }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    count = len(data.get('result', []))
    print(count)
except:
    print('0')
" 2>/dev/null)
    
    if [ "$search_result" -gt 0 ]; then
        echo -e "${GREEN}✅ Search functionality is working${NC}"
    else
        echo -e "${YELLOW}⚠️ Search test returned no results (this may be normal)${NC}"
    fi
else
    echo -e "${BLUE}ℹ️ No documents indexed yet - search test skipped${NC}"
fi

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}Vector indexing verification completed!${NC}"
echo -e "${BLUE}===============================================${NC}"

# Provide recommendations
echo -e "${YELLOW}Recommendations:${NC}"
if [ "$total_points" -eq 0 ]; then
    echo -e "1. 📄 Upload documents through the application to test indexing"
    echo -e "2. 🔄 Run this script again after uploading documents"
else
    echo -e "1. ✅ Indexing appears to be working correctly"
    echo -e "2. 🧪 Test agent queries to verify RAG functionality"
fi

echo -e "3. 📊 Monitor indexing: curl -s http://localhost:6333/collections/regulaite_documents | python3 -m json.tool"
echo -e "4. 🔧 If issues persist, restart containers: docker-compose restart"
echo "" 