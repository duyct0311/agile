import os
import uuid
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

# Cấu hình Client
API_KEY = "push key vào đây"
client = genai.Client(api_key=API_KEY)

# Lấy danh sách mô hình và sắp xếp theo RPM (tiệm cận qua Flash > Pro) và Context Window
AVAILABLE_MODELS = []
try:
    models = list(client.models.list())
    
    def get_model_priority(m):
        name = getattr(m, 'name', str(m)).lower()
        # Ưu tiên 1: RPM (Dòng flash thường có RPM cao hơn pro với tài khoản miễn phí)
        is_flash = 1 if "flash" in name else 0
        # Ưu tiên 2: Context window (input_token_limit)
        context_window = getattr(m, 'input_token_limit', 0) or 0
        return (is_flash, context_window)
    
    models.sort(key=get_model_priority, reverse=True)
    
    for m in models:
        m_name = getattr(m, 'name', str(m))
        actions = getattr(m, 'supported_actions', [])
        if not actions:
            actions = []
        if "generateContent" in actions or "flash" in m_name.lower() or "pro" in m_name.lower():
            AVAILABLE_MODELS.append(m_name)
    
    # Loại bỏ trùng lặp giữ nguyên thứ tự
    AVAILABLE_MODELS = list(dict.fromkeys(AVAILABLE_MODELS))
    if not AVAILABLE_MODELS:
        AVAILABLE_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]
except Exception as e:
    print("Lỗi khi lấy danh sách model:", e)
    AVAILABLE_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]

print("Danh sách model ưu tiên:")
print(AVAILABLE_MODELS)

# Lưu trữ các session chat trong bộ nhớ (để giữ context)
# Cấu trúc: { "session_id": { "chat": <chat_obj>, "model_index": 0 } }
chat_sessions = {}

app = FastAPI(title="Duy Care AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-ID"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    session_id = req.session_id
    if not session_id or session_id not in chat_sessions:
        session_id = str(uuid.uuid4())
        initial_model = AVAILABLE_MODELS[0]
        chat_sessions[session_id] = {
            "chat": client.chats.create(model=initial_model, config={
                "system_instruction": "Bạn là trợ lý phòng khám Duy Care."
            }),
            "model_index": 0
        }

    async def generate_response():
        fallback_occured = False
        
        while chat_sessions[session_id]['model_index'] < len(AVAILABLE_MODELS):
            current_model = AVAILABLE_MODELS[chat_sessions[session_id]['model_index']]
            chat = chat_sessions[session_id]['chat']
            
            try:
                # Gửi request và lấy stream iterator
                response_stream = chat.send_message_stream(req.message)
                iterator = iter(response_stream)
                
                # Cố gắng kéo chunk đầu tiên để validate lỗi quota (thường xuất hiện ngay lúc request)
                try:
                    first_chunk = next(iterator)
                except StopIteration:
                    first_chunk = None

                # Nếu trước đó có fallback, thông báo cho người dùng
                if fallback_occured:
                    yield f"\n[Hệ thống tự động chuyển sang model mới: {current_model} do lỗi Quota]\n"

                # Yield nội dung
                if first_chunk and first_chunk.text:
                    yield first_chunk.text
                    
                for chunk in iterator:
                    if chunk.text:
                        yield chunk.text
                
                # Thành công thì thoát vòng lặp retry
                break

            except Exception as e:
                error_msg = str(e).lower()
                # Kiểm tra xem có phải lỗi do hết Quota (429) không
                if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
                    chat_sessions[session_id]['model_index'] += 1
                    
                    if chat_sessions[session_id]['model_index'] >= len(AVAILABLE_MODELS):
                        yield "\n[Lỗi: Rất tiếc, đã dùng hết Quota của tất cả các Model khả dụng trên tài khoản Google!]"
                        return
                    
                    # Tiến hành cấu hình model thay thế
                    new_model = AVAILABLE_MODELS[chat_sessions[session_id]['model_index']]
                    try:
                        history = chat.get_history()
                    except:
                        history = []
                        
                    new_chat = client.chats.create(
                        model=new_model, 
                        history=history, 
                        config={"system_instruction": "Bạn là trợ lý phòng khám Duy Care."}
                    )
                    chat_sessions[session_id]['chat'] = new_chat
                    fallback_occured = True
                else:
                    yield f"\n[Lỗi kết nối từ phía AI: {str(e)}]"
                    return

    return StreamingResponse(
        generate_response(), 
        media_type="text/plain", 
        headers={"X-Session-ID": session_id}
    )

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    if not os.path.exists(FRONTEND_DIR):
        os.makedirs(FRONTEND_DIR)
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
