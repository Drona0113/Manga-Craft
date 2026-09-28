from database.project_repository import get_projects
from database.conversation_repository import (
    create_conversation,
    get_conversation,
    save_message,
    get_messages
)


projects = get_projects()

if not projects:
    print("❌ No projects found.")
    exit()


project = projects[0]

print("\n========== PROJECT ==========")
print("ID:", project["id"])
print("NAME:", project["name"])


print("\n========== CREATE CONVERSATION ==========")

conversation_id = create_conversation(project["id"])

print("Conversation ID:", conversation_id)


print("\n========== SAVE MESSAGES ==========")

save_message(
    conversation_id,
    "user",
    "Analyze this manga panel."
)

save_message(
    conversation_id,
    "assistant",
    "Sure! I can analyze the panel."
)


print("\n========== GET CONVERSATION ==========")

conversation = get_conversation(project["id"])

print(dict(conversation))


print("\n========== GET MESSAGES ==========")

messages = get_messages(conversation_id)

for message in messages:
    print(dict(message))