import os
import sys
import sqlite3
import importlib.util
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

app = FastAPI(title="Self-Paced Learning Core Engine")

COURSES = {}
DB_PATH = "data.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_courses():
    global COURSES
    COURSES = {}
    
    # Locate courses directory
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
        
    courses_dir = os.path.join(parent_dir, "courses")
    if os.path.exists(courses_dir):
        for filename in os.listdir(courses_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                file_path = os.path.join(courses_dir, filename)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    
                    course_id = getattr(mod, "COURSE_ID", module_name)
                    COURSES[course_id] = {
                        "id": course_id,
                        "title": getattr(mod, "COURSE_TITLE", module_name.capitalize()),
                        "description": getattr(mod, "COURSE_DESCRIPTION", ""),
                        "curriculum": getattr(mod, "CURRICULUM_DATA", [])
                    }
                except Exception as e:
                    print(f"[-] Failed to load course '{filename}': {e}")

# Initial load on bootstrap
load_courses()

@app.get("/api/courses")
def get_courses():
    # Dynamic reload on each request to make local developer testing instant
    load_courses()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT course_id, module_id, section_id FROM progress")
    rows = cursor.fetchall()
    conn.close()
    
    progress_by_course = {}
    for row in rows:
        c_id = row["course_id"]
        if c_id not in progress_by_course:
            progress_by_course[c_id] = set()
        progress_by_course[c_id].add((row["module_id"], row["section_id"]))
        
    output = []
    for c_id, course in COURSES.items():
        total_sections = len(course["curriculum"]) * 5
        completed_count = len(progress_by_course.get(c_id, []))
        percentage = int((completed_count / total_sections) * 100) if total_sections > 0 else 0
        
        output.append({
            "id": c_id,
            "title": course["title"],
            "description": course["description"],
            "total_modules": len(course["curriculum"]),
            "completed_sections": completed_count,
            "total_sections": total_sections,
            "percentage": percentage
        })
    return output

@app.get("/api/courses/{course_id}/curriculum")
def get_curriculum(course_id: str):
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT module_id, section_id FROM progress WHERE course_id = ?", (course_id,))
    rows = cursor.fetchall()
    conn.close()
    
    completed_map = {}
    for row in rows:
        m_id = row["module_id"]
        s_id = row["section_id"]
        if m_id not in completed_map:
            completed_map[m_id] = []
        completed_map[m_id].append(s_id)
        
    output = []
    for m in COURSES[course_id]["curriculum"]:
        output.append({
            "id": m["id"],
            "title": m["title"],
            "completed_sections": completed_map.get(m["id"], [])
        })
    return output

@app.get("/api/courses/{course_id}/modules/{module_id}")
def get_module(course_id: str, module_id: int):
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    course = COURSES[course_id]
    module = next((m for m in course["curriculum"] if m["id"] == module_id), None)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT section_id FROM progress WHERE course_id = ? AND module_id = ?", (course_id, module_id))
    completed_sections = [row["section_id"] for row in cursor.fetchall()]
    conn.close()
    
    return {
        "id": module["id"],
        "title": module["title"],
        "theory": module["theory"],
        "commands": module["commands"],
        "examples": module["examples"],
        "exercise": module["exercise"],
        "insight": module["insight"],
        "completed_sections": completed_sections
    }

@app.post("/api/courses/{course_id}/modules/{module_id}/toggle-progress")
def toggle_progress(course_id: str, module_id: int, section: str = Query(...)):
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    valid_sections = ["theory", "commands", "examples", "exercise", "insight"]
    if section not in valid_sections:
        raise HTTPException(status_code=400, detail="Invalid section value")
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM progress WHERE course_id = ? AND module_id = ? AND section_id = ?", (course_id, module_id, section))
    exists = cursor.fetchone() is not None
    
    if exists:
        cursor.execute("DELETE FROM progress WHERE course_id = ? AND module_id = ? AND section_id = ?", (course_id, module_id, section))
        completed = False
    else:
        cursor.execute("INSERT INTO progress (course_id, module_id, section_id) VALUES (?, ?, ?)", (course_id, module_id, section))
        completed = True
        
    conn.commit()
    conn.close()
    return {"course_id": course_id, "module_id": module_id, "section": section, "completed": completed}

@app.get("/api/search")
def search_all(q: str = Query("", min_length=1)):
    if not q:
        return {"results": []}
        
    term = q.lower()
    results = []
    
    # Global search across all integrated tracks
    for c_id, course in COURSES.items():
        for m in course["curriculum"]:
            matches = []
            for field in ["theory", "commands", "examples", "exercise", "insight"]:
                content = m[field]
                if term in content.lower():
                    start = max(0, content.lower().find(term) - 40)
                    end = min(len(content), start + len(term) + 80)
                    snippet = "..." + content[start:end].replace("\n", " ") + "..."
                    matches.append({
                        "section": field.capitalize(),
                        "snippet": snippet
                    })
            if term in m["title"].lower() or matches:
                results.append({
                    "type": "curriculum",
                    "course_id": c_id,
                    "course_title": course["title"],
                    "id": m["id"],
                    "title": m["title"],
                    "matches": matches
                })
                
    return {"results": results}

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
