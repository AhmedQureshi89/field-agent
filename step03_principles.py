"""
STEP 03 · Lesson 3 · Transparency and control, in code

The design principles become three small features:
  /status   -> the agent says what it is, which model it runs, and what it may do   (transparency)
  /prompt   -> show the system prompt;  /prompt <text>  replaces it                 (control)
  /off /on  -> the agent stops acting until you turn it back on                     (control, always-visible status)

Run:   python step03_principles.py
"""
from core import BASE_URL, MODEL, run_agent

SYSTEM = "You are Field Agent. Say when you are unsure. Keep answers under 80 words."

if __name__ == "__main__":
    messages = [{"role": "system", "content": SYSTEM}]
    enabled = True
    print("Field Agent (AI). Commands: /status /prompt [new text] /off /on quit")
    while True:
        user = input(f"\n[{'ON ' if enabled else 'OFF'}] you > ").strip()
        if user in {"quit", "exit"}:
            break
        if user == "/status":
            print(f"I am an AI agent · model {MODEL} · endpoint {BASE_URL} · tools: none yet · enabled={enabled}")
        elif user.startswith("/prompt"):
            new = user[len("/prompt"):].strip()
            if new:
                messages[0]["content"] = new
                print("system prompt updated")
            else:
                print("system prompt:", messages[0]["content"])
        elif user == "/off":
            enabled = False
            print("agent paused. Nothing will be sent to the model until /on")
        elif user == "/on":
            enabled = True
            print("agent active")
        elif user:
            if not enabled:
                print("(paused) turn me on with /on")
                continue
            messages.append({"role": "user", "content": user})
            run_agent(messages, tool_names=[])
