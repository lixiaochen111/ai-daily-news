#!/bin/bash
# Manual test script for AI filter integration
# Tests the complete pipeline with sample data

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}AI Filter Integration Test${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Check for required environment variables
echo -e "${YELLOW}Checking environment...${NC}"

if [ -z "$EASYROUTER_API_KEY" ]; then
    echo -e "${RED}ERROR: EASYROUTER_API_KEY not set${NC}"
    echo "Please set the API key:"
    echo "  export EASYROUTER_API_KEY='your-key-here'"
    exit 1
fi

echo -e "${GREEN}✓ EASYROUTER_API_KEY is set${NC}"

# Check if AI filter is enabled
AI_FILTER_ENABLED=${AI_FILTER_ENABLED:-1}
if [ "$AI_FILTER_ENABLED" = "1" ]; then
    echo -e "${GREEN}✓ AI_FILTER_ENABLED=1 (active)${NC}"
else
    echo -e "${YELLOW}⚠ AI_FILTER_ENABLED=$AI_FILTER_ENABLED (disabled)${NC}"
    echo "  To enable: export AI_FILTER_ENABLED=1"
fi

echo ""

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${YELLOW}Project root: ${PROJECT_ROOT}${NC}"
echo ""

# Check Python environment
echo -e "${YELLOW}Checking Python environment...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: python3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"

# Check virtual environment
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${GREEN}✓ Virtual environment found${NC}"
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo -e "${YELLOW}⚠ No virtual environment found at .venv${NC}"
fi

echo ""

# Run Python unit tests first
echo -e "${BLUE}--------------------------------------------------${NC}"
echo -e "${BLUE}Step 1: Running Unit Tests${NC}"
echo -e "${BLUE}--------------------------------------------------${NC}"

cd "$PROJECT_ROOT"

if python3 -m pytest tests/test_integration.py -v --tb=short; then
    echo -e "${GREEN}✓ Unit tests passed${NC}"
else
    echo -e "${RED}✗ Unit tests failed${NC}"
    exit 1
fi

echo ""

# Create test data file
echo -e "${BLUE}--------------------------------------------------${NC}"
echo -e "${BLUE}Step 2: Creating Test Data${NC}"
echo -e "${BLUE}--------------------------------------------------${NC}"

TEST_DATA_FILE="/tmp/ai_filter_test_data.json"

cat > "$TEST_DATA_FILE" <<'EOF'
[
  {
    "title": "GPT-5 Model Announcement",
    "link": "https://openai.com/blog/gpt-5",
    "source": {
      "name": "OpenAI Blog",
      "url": "https://openai.com/blog"
    },
    "description": "OpenAI announces GPT-5 with breakthrough capabilities",
    "published": "2026-05-17T10:00:00Z"
  },
  {
    "title": "AI Startup Raises $100M Series B",
    "link": "https://techcrunch.com/ai-startup-funding",
    "source": {
      "name": "TechCrunch",
      "url": "https://techcrunch.com"
    },
    "description": "New artificial intelligence company secures major funding round",
    "published": "2026-05-17T09:00:00Z"
  },
  {
    "title": "Building Production LLM Applications",
    "link": "https://news.ycombinator.com/item?id=40123456",
    "source": {
      "name": "Hacker News",
      "url": "https://news.ycombinator.com"
    },
    "description": "Best practices for deploying large language models in production",
    "published": "2026-05-17T08:00:00Z"
  },
  {
    "title": "JavaScript Framework Update v2.0",
    "link": "https://example.com/js-framework",
    "source": {
      "name": "Dev Blog",
      "url": "https://example.com"
    },
    "description": "New version of popular JavaScript framework released",
    "published": "2026-05-17T07:00:00Z"
  }
]
EOF

echo -e "${GREEN}✓ Test data created at $TEST_DATA_FILE${NC}"
echo -e "${YELLOW}  Items: 4 (Tier 0: 1, Tier 1: 1, Tier 2: 2)${NC}"
echo ""

# Run the filter
echo -e "${BLUE}--------------------------------------------------${NC}"
echo -e "${BLUE}Step 3: Running AI Filter${NC}"
echo -e "${BLUE}--------------------------------------------------${NC}"

OUTPUT_FILE="/tmp/ai_filter_test_data_filtered.json"

if python3 -m scripts.ai_filter.main_filter "$TEST_DATA_FILE"; then
    echo -e "${GREEN}✓ Filter completed successfully${NC}"
else
    echo -e "${RED}✗ Filter failed${NC}"
    exit 1
fi

echo ""

# Analyze results
echo -e "${BLUE}--------------------------------------------------${NC}"
echo -e "${BLUE}Step 4: Analyzing Results${NC}"
echo -e "${BLUE}--------------------------------------------------${NC}"

if [ ! -f "$OUTPUT_FILE" ]; then
    echo -e "${RED}ERROR: Output file not found at $OUTPUT_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Output file: $OUTPUT_FILE${NC}"
echo ""

# Count results using Python
python3 << EOF
import json
import sys

try:
    with open('$OUTPUT_FILE', 'r', encoding='utf-8') as f:
        items = json.load(f)

    print(f"Total items after filtering: {len(items)}")
    print()

    # Analyze by tier
    tier_counts = {}
    for item in items:
        tier = item.get('ai_metadata', {}).get('tier', 'unknown')
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    print("Distribution by tier:")
    for tier in sorted(tier_counts.keys()):
        count = tier_counts[tier]
        print(f"  Tier {tier}: {count} items")

    print()
    print("Sample items:")
    for i, item in enumerate(items[:3], 1):
        title = item.get('title', 'N/A')
        tier = item.get('ai_metadata', {}).get('tier', 'N/A')
        source = item.get('source', {}).get('name', 'N/A')
        print(f"  {i}. [{source}] {title} (Tier {tier})")

    sys.exit(0)

except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
EOF

ANALYSIS_EXIT=$?

echo ""

# Final summary
echo -e "${BLUE}==================================================${NC}"
if [ $ANALYSIS_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed successfully!${NC}"
    echo -e "${BLUE}==================================================${NC}"
    echo ""
    echo -e "Test files created:"
    echo -e "  Input:  ${YELLOW}$TEST_DATA_FILE${NC}"
    echo -e "  Output: ${YELLOW}$OUTPUT_FILE${NC}"
    echo ""
    echo -e "To manually test with real API (skipped in unit tests):"
    echo -e "  ${YELLOW}pytest tests/test_integration.py::TestIntegrationFilters::test_integration_with_real_api -v -s${NC}"
    exit 0
else
    echo -e "${RED}✗ Tests failed${NC}"
    echo -e "${BLUE}==================================================${NC}"
    exit 1
fi
