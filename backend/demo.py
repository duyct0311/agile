from google import genai
import sys

# Cấu hình Client
API_KEY = "key4"  # <-- THAY KEY CỦA DUY VÀO ĐÂY
client = genai.Client(api_key=API_KEY)

def chat_realtime():
    print("==========================================")
    print("    HỆ THỐNG CHAT REALTIME - DUY CARE     ")
    print("==========================================")
    
    # Bỏ qua bước quét danh sách model mất thời gian, dùng luôn model flash để phản hồi nhanh
    selected_model = "gemini-2.5-flash"
    
    try:
        # Khởi tạo phiên chat
        chat = client.chats.create(model=selected_model, config={
            "system_instruction": "Bạn là trợ lý y tế phòng khám Duy Care. Cung cấp thông tin lịch sự, ngắn gọn và hữu ích."
        })
        
        print("\nBot: Chào Duy! Tôi đã sẵn sàng để trò chuyện.")
        print("(Gõ 'thoát', 'exit' hoặc 'quit' để dừng cuộc trò chuyện)\n")
        
        while True:
            try:
                # Nhận đầu vào từ người dùng
                text = input("Khách: ")
                if not text.strip():
                    continue
                    
                if text.strip().lower() in ["thoát", "exit", "quit"]:
                    print("Bot: Cảm ơn bạn. Hẹn gặp lại!")
                    break
                
                print("Bot: ", end="", flush=True)
                
                # Chế độ streaming hiển thị từng chữ realtime
                response_stream = chat.send_message_stream(text)
                for chunk in response_stream:
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                print("\n")
                
            except KeyboardInterrupt:
                print("\nBot: Đã ngắt kết nối. Tạm biệt!")
                break
                
    except Exception as e:
        print(f"\n[Lỗi kết nối]: {e}")
        print("Vui lòng kiểm tra lại API_KEY hoặc kết nối mạng.")

if __name__ == "__main__":
    chat_realtime()