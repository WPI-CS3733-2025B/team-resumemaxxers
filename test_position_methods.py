#!/usr/bin/env python
"""Quick test to verify Position methods exist"""
from app import create_app
from app.main.models import Position

app = create_app()
with app.app_context():
    print("Testing Position class methods...")
    print(f"Position has is_full method: {hasattr(Position, 'is_full')}")
    print(f"Position has get_approved_count method: {hasattr(Position, 'get_approved_count')}")
    
    # Test with a sample position
    pos = Position.query.first()
    if pos:
        print(f"\nTesting with position: {pos.name}")
        print(f"Team size: {pos.team_size}")
        print(f"Approved count: {pos.get_approved_count()}")
        print(f"Is full: {pos.is_full()}")
    else:
        print("\nNo positions in database to test with")
