from sqlalchemy.orm import Session

from models import (
    Employee,
    EmployeeCompetency,
    Course,
    CourseCompetency
)


def get_recommendations(
    employee_id: int,
    db: Session
):
    """
    Generate personalized course recommendations
    based on the employee's competency gaps.
    """

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        return None

    # Get employee competency data
    competency_data = (
        db.query(EmployeeCompetency)
        .filter(
            EmployeeCompetency.employee_id == employee_id
        )
        .all()
    )

    # Store only competencies where a gap exists
    gaps = {}

    for item in competency_data:

        gap = item.required_level - item.current_level

        if gap > 0:
            gaps[item.competency_id] = {
                "competency_name": item.competency.name,
                "current_level": item.current_level,
                "required_level": item.required_level,
                "gap": gap
            }

    # Get all courses
    courses = db.query(Course).all()

    recommendations = []

    for course in courses:

        course_competencies = (
            db.query(CourseCompetency)
            .filter(
                CourseCompetency.course_id == course.id
            )
            .all()
        )

        best_match = None

        for mapping in course_competencies:

            competency_id = mapping.competency_id

            if competency_id not in gaps:
                continue

            gap_data = gaps[competency_id]

            # Recommendation score
            #
            # Bigger competency gap = higher priority
            # Higher course coverage = better match

            score = (
                gap_data["gap"] *
                mapping.coverage
            ) / 100

            if best_match is None or score > best_match["score"]:

                best_match = {
                    "competency": gap_data["competency_name"],
                    "current_level": gap_data["current_level"],
                    "required_level": gap_data["required_level"],
                    "gap": round(gap_data["gap"], 2),
                    "coverage": mapping.coverage,
                    "score": round(score, 2)
                }

        if best_match:

            # Determine priority
            if best_match["score"] >= 25:
                priority = "High"
            elif best_match["score"] >= 15:
                priority = "Medium"
            else:
                priority = "Low"

            reason = (
                f"Your {best_match['competency']} competency "
                f"is {best_match['current_level']}%, while your role "
                f"requires {best_match['required_level']}%. "
                f"This course covers approximately "
                f"{best_match['coverage']}% of that competency."
            )

            recommendations.append({
                "course_id": course.id,
                "course_title": course.title,
                "difficulty": course.difficulty,
                "duration": course.duration,
                "competency": best_match["competency"],
                "current_level": best_match["current_level"],
                "required_level": best_match["required_level"],
                "gap": best_match["gap"],
                "coverage": best_match["coverage"],
                "priority_score": best_match["score"],
                "priority": priority,
                "reason": reason
            })

    # Highest priority first
    recommendations.sort(
        key=lambda x: x["priority_score"],
        reverse=True
    )

    return recommendations