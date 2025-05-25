from datetime import datetime, timezone
from langgraph.graph import MessageGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.llms import Ollama

# Инструмент для получения времени
def get_current_time() -> dict:
    """Возвращает текущее время UTC"""
    return {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

# Локальная модель
model = Ollama(model="mistral")  # Используем Mistral

russian_time_phrases = [
    "который час",
    "сколько времени",
    "сколько сейчас времени",
    "который сейчас час",
    "подскажите время",
    "мне нужно точное время",
    "текущее время",
    "точное время",
    "часочки",
    "времени не подскажете",
    "можно узнать время",
    "продиктуйте время",
    "сколько на ваших часах",
    "время в данный момент",
    "не подскажете, который час",
    "извините, который сейчас час",
    "скажите, пожалуйста, сколько времени",
    "могли бы вы сказать, который час",
    "какое сейчас время",
    "время суток сейчас",
    "сколько время показывает",
    "время узнать можно"
    ]
english_time_phrases = [
    "what time is it",
    "what's the time",
    "what is the current time",
    "could you tell me the time",
    "do you have the time",
    "time please",
    "got the time",
    "what time do you have",
    "may i know the time",
    "time check",
    "what time is it now",
    "what's the time right now",
    "current time please",
    "can you give me the exact time",
    "could you tell me what time it is",
    "would you mind telling me the time",
    "i need to know the time",
    "what does the clock say"
]

# Модель инструментов
def agent_with_tools(input_text: str):
    normalized_input = input_text.lower().strip(' ?!.,')
    if (normalized_input in russian_time_phrases) or (normalized_input in english_time_phrases):
        return {"tool_calls": [{"name": "get_current_time"}]}
    return model.invoke(input_text)

tool_node = ToolNode([get_current_time])

workflow = MessageGraph()
workflow.add_node("agent", agent_with_tools)
workflow.add_node("tools", tool_node)
workflow.add_edge("tools", "agent")
workflow.set_entry_point("agent")

# Логика маршрутизации
def route_messages(state: list):
    last_message = state[-1]
    if isinstance(last_message, dict) and "tool_calls" in last_message:
        return "tools"
    return "end"

workflow.add_conditional_edges("agent", route_messages)
workflow.set_finish_point("agent")
workflow.set_finish_point("tools")

app = workflow.compile()

# Чат-интерфейс
if __name__ == "__main__":
    print("Бот запущен. Введите 'выход' для завершения.")
    print("The bot is running. Enter 'exit' to complete.")
    history = []

    while True:
        user_input = input("Вы: ")
        if user_input.lower() in ["выход", "exit"]:
            break

        history.append(HumanMessage(content=user_input))
        response = app.invoke(history)

        for msg in response:
            if isinstance(msg, AIMessage):
                print(f"Бот: {msg.content}")
                history.append(msg)
            elif isinstance(msg, dict) and "utc" in msg:  
                print(f"Бот: Текущее время UTC - {msg['utc']}")
                history.append(AIMessage(content=f"Текущее время: {msg['utc']}"))
