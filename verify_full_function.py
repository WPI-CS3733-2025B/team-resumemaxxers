#!/usr/bin/env python
"""Verify the full position functionality is working"""
from app import create_app
from app.main.models import Position, Application

app = create_app()
with app.app_context():
    print("="*60)
    print("TESTING POSITION FULL FUNCTIONALITY")
    print("="*60)
    
    # Get all positions
    positions = Position.query.all()
    print(f"\nTotal positions in database: {len(positions)}")
    
    for pos in positions:
        approved_count = pos.get_approved_count()
        is_full = pos.is_full()
        
        print(f"\n{'='*60}")
        print(f"Position: {pos.name}")
        print(f"Team size: {pos.team_size}")
        print(f"Total applications: {len(pos.applications)}")
        print(f"Approved applications: {approved_count}")
        print(f"Is full: {is_full}")
        
        if approved_count > 0:
            print("\nApproved applicants:")
            for app in pos.applications:
                if app.status == 'approved':
                    print(f"  - {app.student.firstname} {app.student.lastname}")
        
        if is_full:
            print("\n⚠️  THIS POSITION IS FULL - Should be hidden from students!")
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)
