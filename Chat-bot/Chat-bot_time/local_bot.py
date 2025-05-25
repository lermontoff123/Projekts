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

# Модель инструментов
def agent_with_tools(input_text: str):
    # Запрос времени
    if input_text.lower() in ["время", "час", "time"]:
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
    print("Бот запущен. Введите 'выход' для завершения.\The bot is running. Enter 'exit' to complete.")
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
            elif isinstance(msg, dict) and "utc" in msg:  # Ответ от инструмента
                print(f"Бот: Текущее время UTC - {msg['utc']}")
                history.append(AIMessage(content=f"Текущее время: {msg['utc']}"))
