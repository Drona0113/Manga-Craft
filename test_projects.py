#test_projects.py
import time
from database.project_repository import (
    create_project,
    get_projects,
    get_project,
    update_project,
    delete_project
)


print("\n========== CREATE ==========")

project_id = create_project("My First Manga")

print("Created project ID:", project_id)


print("\n========== GET ALL ==========")

projects = get_projects()

for project in projects:
    print(dict(project))


print("\n========== GET ONE ==========")

project = get_project(project_id)

print(dict(project))

time.sleep(2)

print("\n========== UPDATE ==========")

update_project(
    project_id,
    "My Updated Manga"
)

print(dict(get_project(project_id)))


print("\n========== DELETE ==========")

delete_project(project_id)

print("After delete:", get_project(project_id))