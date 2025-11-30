"""
TROUBLESHOOTING GUIDE FOR FULL POSITION FEATURE
================================================

Run this to see what's happening:
python diagnostic_full.py

WHAT TO CHECK:
1. Are you logged in as FACULTY? (FULL badge only shows to faculty)
2. Is the position actually full? (approved count >= team_size)
3. Have you cleared your browser cache?

WHERE TO SEE THE FULL BADGE:
============================

FOR FACULTY:
- Faculty Dashboard: /faculty/<faculty_id>/index
  - Shows position cards with FULL badge next to position name
  - Shows "(X approved)" count next to team size

- Application List: /student_list/<position_id>/view
  - Header shows "FULL" badge if position is full
  - Shows "X approved / Y needed" count
  - Each application card shows "Position FULL" badge

FOR STUDENTS:
- Student Dashboard: /student/<student_id>/index
  - Full positions are HIDDEN (won't show up at all)
  
- Position Detail: /position/<position_id>/view
  - If position is full, redirects back with error message

- Apply to Position: /student/<position_id>/apply
  - If position is full, shows error and redirects
"""

from app import create_app
from app.main.models import Position, Faculty, Student

app = create_app()
with app.app_context():
    print("="*70)
    print("FULL POSITION DIAGNOSTIC")
    print("="*70)
    
    # Get all positions
    positions = Position.query.all()
    full_positions = [p for p in positions if p.is_full()]
    available_positions = [p for p in positions if not p.is_full()]
    
    print(f"\n📊 POSITION STATUS OVERVIEW:")
    print(f"   Total positions: {len(positions)}")
    print(f"   Full positions: {len(full_positions)}")
    print(f"   Available positions: {len(available_positions)}")
    
    if full_positions:
        print(f"\n🔴 FULL POSITIONS (should show FULL badge for faculty):")
        for pos in full_positions:
            print(f"\n   Position: {pos.name}")
            print(f"   Faculty: {pos.faculty.firstname} {pos.faculty.lastname}")
            print(f"   Team size: {pos.team_size}")
            print(f"   Approved: {pos.get_approved_count()}")
            print(f"   Status: ⚠️ FULL")
            print(f"   URL: http://127.0.0.1:5000/position/{pos.id}/view")
    else:
        print(f"\n✅ No full positions - all have space available")
    
    print(f"\n" + "="*70)
    print("TESTING INSTRUCTIONS:")
    print("="*70)
    print("""
1. Make sure Flask is running: flask run
2. Open browser and login as FACULTY
3. Go to faculty dashboard
4. Look for positions with red FULL badge
    
If you don't see any full positions:
- The positions might not actually be full yet
- Approve more applications until approved count = team size
""")
    
    # Show which faculty have positions
    faculties = Faculty.query.all()
    print(f"\n👤 FACULTY ACCOUNTS (login as one of these):")
    for fac in faculties[:5]:
        pos_count = len(fac.positions)
        full_count = sum(1 for p in fac.positions if p.is_full())
        print(f"   {fac.username} - {pos_count} positions ({full_count} full)")
