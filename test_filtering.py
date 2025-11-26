#!/usr/bin/env python
"""Test that full positions are filtered for students"""
from app import create_app
from app.main.models import Position

app = create_app()
with app.app_context():
    all_positions = Position.query.all()
    
    print("\n" + "=" * 60)
    print("TESTING STUDENT VIEW FILTERING")
    print("=" * 60)
    
    print(f"\nTotal positions in database: {len(all_positions)}")
    
    # Simulate what student_index does
    filtered_positions = [pos for pos in all_positions if not pos.is_full()]
    
    print(f"Positions visible to students (not full): {len(filtered_positions)}")
    print(f"Full positions (hidden from students): {len(all_positions) - len(filtered_positions)}")
    
    print("\nFull positions that should be hidden:")
    for pos in all_positions:
        if pos.is_full():
            print(f"  - {pos.name} (team_size={pos.team_size}, approved={pos.get_approved_count()})")
    
    print("\nPositions visible to students:")
    for pos in filtered_positions:
        print(f"  - {pos.name} (team_size={pos.team_size}, approved={pos.get_approved_count()})")
