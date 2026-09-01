from database.project_memory_repository import (
    save_project_memory,
    get_project_memory,
    search_project_memory,
    get_project_context
)


PROJECT_ID = 6


print("\n========== SAVE 1 ==========")

result = save_project_memory(
    project_id=PROJECT_ID,
    memory_type="character",
    content="Hinata wears an orange jersey."
)

print(result)


print("\n========== SAVE 2 ==========")

result = save_project_memory(
    project_id=PROJECT_ID,
    memory_type="character",
    content="Hinata wears an orange jersey."
)

print(result)


print("\n========== GET MEMORY ==========")

memories = get_project_memory(
    PROJECT_ID
)

for memory in memories:
    print(dict(memory))


print("\n========== SEARCH ==========")

results = search_project_memory(
    PROJECT_ID,
    "Hinata"
)

for result in results:
    print(dict(result))


print("\n========== CONTEXT ==========")

context = get_project_context(
    PROJECT_ID
)

print("PROJECT:")
print(dict(context["project"]))

print("\nMEMORIES:")

for memory in context["memories"]:
    print(dict(memory))

print("\nPANELS:")

for panel in context["panels"]:
    print(dict(panel))

print("\nGENERATED REFERENCES:")

for reference in context["generated_references"]:
    print(dict(reference))