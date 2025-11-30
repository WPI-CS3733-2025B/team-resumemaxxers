#!/usr/bin/env python
"""Test if the position template renders FULL badge correctly"""
from app import create_app
from app.main.models import Position, Faculty
from flask import render_template_string

app = create_app()
with app.app_context():
    # Get a full position
    positions = Position.query.all()
    full_positions = [p for p in positions if p.is_full()]
    
    print("="*60)
    print("TESTING TEMPLATE RENDERING")
    print("="*60)
    
    if full_positions:
        pos = full_positions[0]
        print(f"\nTesting with FULL position: {pos.name}")
        print(f"Team size: {pos.team_size}")
        print(f"Approved count: {pos.get_approved_count()}")
        print(f"Is full: {pos.is_full()}")
        
        # Simulate faculty user
        faculty = Faculty.query.first()
        
        # Test the template logic
        template = """
        Position: {{ position.name }}
        {% if position.is_full() %}
        Status: FULL
        {% else %}
        Status: Available
        {% endif %}
        Approved: {{ position.get_approved_count() }} / {{ position.team_size }}
        """
        
        result = render_template_string(template, position=pos)
        print("\nTemplate output:")
        print(result)
        
    else:
        print("\nNo full positions found in database!")
        print("Create a position with team_size=1 and approve 1 application to test.")
