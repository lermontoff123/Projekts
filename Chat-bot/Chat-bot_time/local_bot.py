from datetime import datetime, timezone
from langgraph.graph import MessageGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.llms import Ollama
from langgraph.pregel import serve

def get_current_time() -> dict:
    """Возвращает текущее время в удобных форматах"""
    now = datetime.now(timezone.utc)
    return {
        "utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "time_ru": now.strftime("%H:%M"),
        "date_ru": now.strftime("%d.%m.%Y"),
        "time_en": now.strftime("%I:%M %p")
    }

model = Ollama(
    model="mistral",
    system="Ты - двуязычный ассистент. Отвечай на языке пользователя."
)

TIME_PHRASES = {
    # Русские
    "который час", "сколько времени", "текущее время",
    "точное время", "часочки", "сколько на часах",
    # Английские
    "what time is it", "what's the time", "current time",
    "do you have the time", "time please"
}

def agent_with_tools(input_text: str):
    if any(phrase in input_text.lower() for phrase in TIME_PHRASES):
        return {"tool_calls": [{"name": "get_current_time"}]}
    return model.invoke(input_text)

# Инициализация графа
tool_node = ToolNode([get_current_time])
workflow = MessageGraph()
workflow.add_node("agent", agent_with_tools)
workflow.add_node("tools", tool_node)
workflow.add_edge("tools", "agent")
workflow.set_entry_point("agent")

def route_messages(state: list):
    last_message = state[-1]
    if isinstance(last_message, dict) and "tool_calls" in last_message:
        return "tools"
    return "end"

workflow.add_conditional_edges("agent", route_messages)
workflow.set_finish_point("agent")
workflow.set_finish_point("tools")

app = workflow.compile()

def run_chat():
    print("Бот запущен. Введите 'выход' или 'exit' для завершения.")
    print("The bot is running. Enter 'exit' to complete.")
    history = []
    
    while True:
        try:
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
                    time_str = (
                        f"Текущее время: {msg['time_ru']} (UTC)\n"
                        f"Дата: {msg['date_ru']}\n"
                        f"12h format: {msg['time_en']}"
                    )
                    print(f"Бот: {time_str}")
                    history.append(AIMessage(content=time_str))
                    
        except KeyboardInterrupt:
            print("\nЗавершение работы...")
            break

def run_server():
    """Веб-режим работы"""
    serve(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        run_server()
    else:
        run_chat()
