#!/usr/bin/env python3

# Test the tuple unpacking syntax
type_keywords = {
    "change order": ("TYPE_CHANGEORDER", 5),
    "statement of work": ("TYPE_SOW", 3),
}

# Test unpacking
for keyword, (category, weight) in type_keywords.items():
    print(f"Keyword: {keyword}, Category: {category}, Weight: {weight}")

print("Syntax test passed!")