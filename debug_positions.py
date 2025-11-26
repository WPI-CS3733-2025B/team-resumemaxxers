#!/usr/bin/env python
"""Debug script to check position status"""
from app import create_app
from app.main.models import Position, Application

app = create_app()
with app.app_context():
    positions = Position.query.all()
    
    print("=" * 60)
    print("POSITION STATUS DEBUG")
    print("=" * 60)
    
    for pos in positions:
        print(f"\nPosition: {pos.name}")
        print(f"  Team size: {pos.team_size}")
        print(f"  Total applications: {len(pos.applications)}")
        
        # Check each application
        approved_apps = []
        for app in pos.applications:
            print(f"    - Application {app.id}: status='{app.status}'")
            if app.status == 'approved':
                approved_apps.append(app.id)
        
        print(f"  Approved applications: {len(approved_apps)} - IDs: {approved_apps}")
        print(f"  get_approved_count(): {pos.get_approved_count()}")
        print(f"  is_full(): {pos.is_full()}")
        print(f"  Should be full: {pos.get_approved_count() >= pos.team_size}")
